from contextlib import asynccontextmanager
import os
from pathlib import Path
import pickle

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

FASTAPI_DIR = Path(__file__).resolve().parent.parent
load_dotenv(FASTAPI_DIR / ".env")

# Global model state
loaded_model = None

MODEL_PATH = Path(__file__).resolve().parent / "models" / "ensemble_model.pkl"

FEATURE_ENCODINGS = {
    "Outlook": {"Sunny": 2, "Overcast": 0, "Rain": 1},
    "Temperature": {"Hot": 1, "Mild": 2, "Cool": 0},
    "Humidity": {"High": 0, "Normal": 1},
    "Wind": {"Weak": 1, "Strong": 0},
}

TARGET_LABELS = {0: "No", 1: "Yes"}


def get_allowed_origins() -> list[str]:
    """Read CORS origins from the environment for local and hosted frontends."""
    raw_value = os.getenv("ALLOWED_ORIGINS", "*")
    origins = [origin.strip() for origin in raw_value.split(",") if origin.strip()]
    return origins or ["*"]


def encode_feature_value(field_name: str, raw_value: str) -> tuple[str, int]:
    """Normalize incoming values and map them to the trained label encoding."""
    valid_values = FEATURE_ENCODINGS[field_name]
    normalized_value = raw_value.strip().lower()

    for canonical_value, encoded_value in valid_values.items():
        if canonical_value.lower() == normalized_value:
            return canonical_value, encoded_value

    allowed_values = ", ".join(valid_values.keys())
    raise ValueError(f"{field_name} must be one of: {allowed_values}")


def decode_prediction(prediction_value: int) -> str:
    """Convert the model output back to the original class label."""
    try:
        return TARGET_LABELS[int(prediction_value)]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Unexpected prediction value: {prediction_value}") from exc


def load_model() -> bool:
    """Load the trained model from the local backend folder."""
    global loaded_model

    try:
        with open(MODEL_PATH, "rb") as file:
            loaded_model = pickle.load(file)

        print(f"✓ Model loaded successfully from {MODEL_PATH}!")
        return True
    except Exception as e:
        print(f"✗ Error loading model: {str(e)}")
        return False


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Load model state when the application starts."""
    success = load_model()
    if not success:
        print("WARNING: Model failed to load. Prediction endpoint will not work.")
    yield


app = FastAPI(title="PlayTennis Prediction API", lifespan=lifespan)

allowed_origins = get_allowed_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials="*" not in allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WeatherInput(BaseModel):
    outlook: str = Field(..., description="Weather outlook: Sunny, Overcast, or Rain")
    temperature: str = Field(..., description="Temperature: Hot, Mild, or Cool")
    humidity: str = Field(..., description="Humidity: High or Normal")
    wind: str = Field(..., description="Wind: Weak or Strong")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "outlook": "Sunny",
                "temperature": "Hot",
                "humidity": "High",
                "wind": "Weak",
            }
        }
    )


class PredictionResponse(BaseModel):
    prediction: str
    input_data: dict[str, str]
    message: str


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "PlayTennis Prediction API",
        "status": "running",
        "model_loaded": loaded_model is not None,
        "endpoints": {
            "predict": "/predict",
            "health": "/health",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health_check(response: Response):
    """Health check endpoint for local and hosted service probes."""
    model_loaded = loaded_model is not None
    response.status_code = (
        status.HTTP_200_OK if model_loaded else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return {
        "status": "healthy" if model_loaded else "unhealthy",
        "model_loaded": model_loaded,
        "feature_mappings_loaded": True,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(weather: WeatherInput):
    """
    Predict whether to play tennis based on weather conditions

    Parameters:
    - outlook: Sunny, Overcast, or Rain
    - temperature: Hot, Mild, or Cool
    - humidity: High or Normal
    - wind: Weak or Strong

    Returns prediction: Yes or No
    """
    if loaded_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        outlook, encoded_outlook = encode_feature_value("Outlook", weather.outlook)
        temperature, encoded_temperature = encode_feature_value(
            "Temperature", weather.temperature
        )
        humidity, encoded_humidity = encode_feature_value("Humidity", weather.humidity)
        wind, encoded_wind = encode_feature_value("Wind", weather.wind)

        input_data = pd.DataFrame(
            [
                {
                    "Outlook": encoded_outlook,
                    "Temperature": encoded_temperature,
                    "Humidity": encoded_humidity,
                    "Wind": encoded_wind,
                }
            ]
        )
        prediction_encoded = loaded_model.predict(input_data)[0]
        prediction = decode_prediction(prediction_encoded)

        return PredictionResponse(
            prediction=prediction,
            input_data={
                "outlook": outlook,
                "temperature": temperature,
                "humidity": humidity,
                "wind": wind,
            },
            message=f"Prediction: {'Play Tennis!' if prediction == 'Yes' else 'Do not play tennis.'}",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input value: {str(e)}. Please check that all values are valid.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


if __name__ == "__main__":
    try:
        import uvicorn
    except ImportError as exc:
        raise SystemExit(
            "uvicorn is required to run this API directly. Install it with: pip install uvicorn"
        ) from exc

    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
    )

