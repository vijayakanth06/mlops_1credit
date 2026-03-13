import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv


FASTAPI_DIR = Path(__file__).resolve().parent.parent
load_dotenv(FASTAPI_DIR / ".env")


def get_backend_url() -> str:
    """Read the backend URL from Streamlit secrets, .env, or environment variables."""
    try:
        secret_value = st.secrets.get("BACKEND_URL")
    except Exception:
        secret_value = None

    backend_url = secret_value or os.getenv("BACKEND_URL") or "http://127.0.0.1:8000"
    return backend_url.rstrip("/")


def build_api_url(path: str) -> str:
    return f"{BACKEND_URL}{path}"


def get_error_detail(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text or "Unknown error"

    if isinstance(payload, dict):
        return payload.get("detail") or payload.get("message") or str(payload)

    return str(payload)


BACKEND_URL = get_backend_url()
REQUEST_TIMEOUT = 15

st.set_page_config(page_title="PlayTennis Prediction", page_icon="🎾")
st.title("🎾 PlayTennis Prediction API")

st.markdown("""
Predict whether you should play tennis based on current weather conditions.
This frontend uses the BACKEND_URL environment variable when deployed.
""")

st.caption(f"Connected backend: {BACKEND_URL}")

# Input form
with st.form("prediction_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        outlook = st.selectbox("Outlook", ["Sunny", "Overcast", "Rain"])
        temperature = st.selectbox("Temperature", ["Hot", "Mild", "Cool"])
        
    with col2:
        humidity = st.selectbox("Humidity", ["High", "Normal"])
        wind = st.selectbox("Wind", ["Weak", "Strong"])
        
    submit = st.form_submit_button("Predict")

if submit:
    payload = {
        "outlook": outlook,
        "temperature": temperature,
        "humidity": humidity,
        "wind": wind
    }
    
    try:
        response = requests.post(
            build_api_url("/predict"),
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        
        if response.status_code == 200:
            result = response.json()
            prediction = result["prediction"]
            message = result["message"]
            
            if prediction == "Yes":
                st.success(f"### {message}")
                st.balloons()
            else:
                st.error(f"### {message}")
                st.snow()
                
            st.json(result["input_data"])
        else:
            error_detail = get_error_detail(response)
            st.error(f"API Error ({response.status_code}): {error_detail}")
            
    except requests.exceptions.RequestException as exc:
        st.error(f"Could not reach the backend at {BACKEND_URL}: {exc}")

# Health check display in sidebar
st.sidebar.write(f"Backend: {BACKEND_URL}")
st.sidebar.markdown(f"[Open API docs]({build_api_url('/docs')})")

if st.sidebar.button("Check API Health"):
    try:
        health_response = requests.get(build_api_url("/health"), timeout=REQUEST_TIMEOUT)
        st.sidebar.write(health_response.json())
        if health_response.status_code != 200:
            st.sidebar.error(f"Health check returned {health_response.status_code}")
    except requests.exceptions.RequestException as exc:
        st.sidebar.error(f"API is offline: {exc}")
