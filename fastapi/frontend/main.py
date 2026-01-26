import streamlit as st
import requests

st.set_page_config(page_title="PlayTennis Prediction", page_icon="🎾")
st.title("🎾 PlayTennis Prediction API")

st.markdown("""
Predict whether you should play tennis based on current weather conditions.
Connects to the FastAPI backend at `http://localhost:8000`.
""")

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
        # Assuming the FastAPI server is running on localhost:8000
        response = requests.post("http://localhost:8000/predict", json=payload)
        
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
            error_detail = response.json().get('detail', 'Unknown error')
            st.error(f"API Error ({response.status_code}): {error_detail}")
            
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the FastAPI server. Please ensure it is running on http://localhost:8000")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

# Health check display in sidebar
if st.sidebar.button("Check API Health"):
    try:
        health = requests.get("http://localhost:8000/health").json()
        st.sidebar.write(health)
    except:
        st.sidebar.error("API is offline")
