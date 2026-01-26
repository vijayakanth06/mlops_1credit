"""
Test script for the PlayTennis Prediction API
Run this after starting the FastAPI server to test the endpoints
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000"

def test_root():
    """Test the root endpoint"""
    print("\n" + "="*50)
    print("Testing Root Endpoint")
    print("="*50)
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_health():
    """Test the health check endpoint"""
    print("\n" + "="*50)
    print("Testing Health Endpoint")
    print("="*50)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_prediction(outlook, temperature, humidity, wind):
    """Test the prediction endpoint"""
    print("\n" + "="*50)
    print(f"Testing Prediction: {outlook}, {temperature}, {humidity}, {wind}")
    print("="*50)
    
    data = {
        "outlook": outlook,
        "temperature": temperature,
        "humidity": humidity,
        "wind": wind
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Prediction: {result['prediction']}")
        print(f"Message: {result['message']}")
        print(f"Full Response: {json.dumps(result, indent=2)}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("PlayTennis API Test Suite")
    print("Make sure the server is running: uvicorn server:app --reload")
    
    try:
        # Test root endpoint
        test_root()
        
        # Test health endpoint
        test_health()
        
        # Test predictions with various weather conditions
        test_cases = [
            ("Sunny", "Hot", "High", "Weak"),
            ("Overcast", "Mild", "Normal", "Strong"),
            ("Overcast", "Cool", "Normal", "Weak"),
            ("Rain", "Mild", "High", "Strong"),
            ("Rain", "Hot", "Normal", "Weak"),
        ]
        
        for outlook, temperature, humidity, wind in test_cases:
            test_prediction(outlook, temperature, humidity, wind)
        
        # Test with invalid input
        print("\n" + "="*50)
        print("Testing Invalid Input")
        print("="*50)
        test_prediction("InvalidOutlook", "Hot", "High", "Weak")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Make sure the server is running with: uvicorn server:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
