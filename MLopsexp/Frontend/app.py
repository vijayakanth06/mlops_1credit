import streamlit as st
import requests

# Base URL of FastAPI backend
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Machine Learning Prediction App",
    layout="wide"
)

st.title("Machine Learning Prediction Application")
st.caption("Predict exam scores and classify email spam using machine learning models")

# Sidebar
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Select Model", ["Linear Regression", "Logistic Regression", "About"])

# Linear Regression Section
if menu == "Linear Regression":
    st.header("Linear Regression - Exam Score Prediction")
    st.write("""
    This model predicts exam scores based on the number of hours studied.
    Linear regression establishes a linear relationship between study hours and exam performance.
    """)

    hours_studied = st.number_input(
        "Enter Hours Studied",
        min_value=0.0,
        max_value=24.0,
        value=5.0,
        step=0.5,
        help="Enter the number of hours studied (0-24)"
    )

    if st.button("Predict Exam Score"):
        try:
            payload = {"hours_studied": hours_studied}
            res = requests.post(f"{BASE_URL}/predict/linear", json=payload)
            if res.status_code == 200:
                prediction = res.json()['prediction']
                st.success(f"Predicted Exam Score: {prediction:.2f}")
                st.info(f"Based on {hours_studied} hours of study, the model predicts an exam score of {prediction:.2f}")
            else:
                st.error("Failed to get prediction. Please check the backend server.")
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")

# Logistic Regression Section
elif menu == "Logistic Regression":
    st.header("Logistic Regression - Email Spam Classification")
    st.write("""
    This model classifies emails as spam or not spam based on email content.
    Logistic regression analyzes text patterns to determine the likelihood of spam.
    """)

    email_text = st.text_area(
        "Enter Email Text",
        "Congratulations! You won a prize...",
        height=150,
        help="Enter the email content to classify as spam or not spam"
    )

    if st.button("Classify Email"):
        try:
            payload = {"email_text": email_text}
            res = requests.post(f"{BASE_URL}/predict/logistic",json=payload)
            if res.status_code == 200:
                pred = res.json()
                label = pred['label']
                prediction_class = pred['prediction']
                
                if label == "Spam":
                    st.error(f"Classification: {label} (Class {prediction_class})")
                    st.warning("This email appears to be spam based on the model's analysis.")
                else:
                    st.success(f"Classification: {label} (Class {prediction_class})")
                    st.info("This email appears to be legitimate based on the model's analysis.")
            else:
                st.error("Failed to get prediction. Please check the backend server.")
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")

# About Page
elif menu == "About":
    st.header("About this Application")
    st.write("""
    This application demonstrates machine learning predictions using two regression models:
    
    **Linear Regression Model:**
    - Predicts continuous numerical values (exam scores)
    - Input: Hours studied
    - Output: Predicted exam score
    - Use case: Understanding the relationship between study time and academic performance
    
    **Logistic Regression Model:**
    - Classifies data into categories (spam vs. not spam)
    - Input: Email text content
    - Output: Classification label and probability
    - Use case: Email filtering and spam detection
    
    **Technology Stack:**
    - Frontend: Streamlit for interactive web interface
    - Backend: FastAPI for REST API endpoints
    - Models: Scikit-learn machine learning models
    """)
