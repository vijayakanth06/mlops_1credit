from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pickle
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from pathlib import Path

app = FastAPI(title="PlayTennis Prediction API")

# Global variables for model and encoders
loaded_model = None
feature_encoders = {}
target_encoder = None

class WeatherInput(BaseModel):
    outlook: str = Field(..., description="Weather outlook: Sunny, Overcast, or Rain")
    temperature: str = Field(..., description="Temperature: Hot, Mild, or Cool")
    humidity: str = Field(..., description="Humidity: High or Normal")
    wind: str = Field(..., description="Wind: Weak or Strong")
    
    class Config:
        schema_extra = {
            "example": {
                "outlook": "Sunny",
                "temperature": "Hot",
                "humidity": "High",
                "wind": "Weak"
            }
        }

class PredictionResponse(BaseModel):
    prediction: str
    input_data: dict
    message: str

def load_model_and_encoders():
    """Load the model and create encoders on startup"""
    global loaded_model, feature_encoders, target_encoder
    
    try:
        # Path to the model file (in day1 directory)
        model_path = Path(__file__).parent.parent.parent / "day1" / "ensemble_model.pkl"
        data_path = Path(__file__).parent.parent.parent / "day1" / "playtennis.csv"
        
        # Load the original data to recreate encoders
        df_original = pd.read_csv(data_path)
        df_original["Wind"] = df_original["Wind"].fillna(df_original["Wind"].mode()[0])
        
        # Create and fit label encoders for each feature column
        feature_columns = ['Outlook', 'Temperature', 'Humidity', 'Wind']
        
        for col in feature_columns:
            le = LabelEncoder()
            le.fit(df_original[col])
            feature_encoders[col] = le
        
        # Create encoder for target
        target_encoder = LabelEncoder()
        target_encoder.fit(df_original['PlayTennis'])
        
        # Load the saved model
        with open(model_path, 'rb') as file:
            loaded_model = pickle.load(file)
        
        print("✓ Model and encoders loaded successfully!")
        return True
    except Exception as e:
        print(f"✗ Error loading model: {str(e)}")
        return False

@app.on_event("startup")
async def startup_event():
    """Load model when the application starts"""
    success = load_model_and_encoders()
    if not success:
        print("WARNING: Model failed to load. Prediction endpoint will not work.")

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
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": loaded_model is not None,
        "encoders_loaded": len(feature_encoders) == 4
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
        # Validate and encode inputs
        encoded_outlook = feature_encoders['Outlook'].transform([weather.outlook])[0]
        encoded_temperature = feature_encoders['Temperature'].transform([weather.temperature])[0]
        encoded_humidity = feature_encoders['Humidity'].transform([weather.humidity])[0]
        encoded_wind = feature_encoders['Wind'].transform([weather.wind])[0]
        
        # Create input array
        input_data = [[encoded_outlook, encoded_temperature, encoded_humidity, encoded_wind]]
        
        # Make prediction
        prediction_encoded = loaded_model.predict(input_data)[0]
        
        # Decode prediction
        prediction = target_encoder.inverse_transform([prediction_encoded])[0]
        
        return PredictionResponse(
            prediction=prediction,
            input_data={
                "outlook": weather.outlook,
                "temperature": weather.temperature,
                "humidity": weather.humidity,
                "wind": weather.wind
            },
            message=f"Prediction: {'Play Tennis!' if prediction == 'Yes' else 'Do not play tennis.'}"
        )
    
    except ValueError as e:
        # Handle invalid input values
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input value: {str(e)}. Please check that all values are valid."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

