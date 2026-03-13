"""
Test script for the PlayTennis Prediction API
Run this after starting the FastAPI server to test local or hosted endpoints.
"""

import json
import os
import sys

import requests

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT = 15


def print_response(title, response):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except ValueError:
        print(f"Response Text: {response.text}")


def expect_status(response, expected_status):
    if response.status_code != expected_status:
        raise AssertionError(
            f"Expected status {expected_status}, got {response.status_code}: {response.text}"
        )

def test_root():
    """Test the root endpoint"""
    response = requests.get(f"{BASE_URL}/", timeout=REQUEST_TIMEOUT)
    print_response("Testing Root Endpoint", response)
    expect_status(response, 200)

def test_health():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health", timeout=REQUEST_TIMEOUT)
    print_response("Testing Health Endpoint", response)
    expect_status(response, 200)


def test_openapi():
    """Test the generated OpenAPI schema."""
    response = requests.get(f"{BASE_URL}/openapi.json", timeout=REQUEST_TIMEOUT)
    print_response("Testing OpenAPI Schema", response)
    expect_status(response, 200)

def test_prediction(outlook, temperature, humidity, wind, expected_status=200):
    """Test the prediction endpoint"""
    data = {
        "outlook": outlook,
        "temperature": temperature,
        "humidity": humidity,
        "wind": wind
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=data, timeout=REQUEST_TIMEOUT)
    print_response(
        f"Testing Prediction: {outlook}, {temperature}, {humidity}, {wind}",
        response,
    )
    expect_status(response, expected_status)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Prediction: {result['prediction']}")
        print(f"Message: {result['message']}")

if __name__ == "__main__":
    print("PlayTennis API Test Suite")
    print(f"Target API: {BASE_URL}")
    print("For local testing, start the server with: python .\\fastapi\\backend\\server.py")
    
    try:
        test_root()
        test_health()
        test_openapi()

        test_cases = [
            ("Sunny", "Hot", "High", "Weak"),
            ("Overcast", "Mild", "Normal", "Strong"),
            ("Overcast", "Cool", "Normal", "Weak"),
            ("Rain", "Mild", "High", "Strong"),
            ("Rain", "Hot", "Normal", "Weak"),
        ]
        
        for outlook, temperature, humidity, wind in test_cases:
            test_prediction(outlook, temperature, humidity, wind)
        
        test_prediction("InvalidOutlook", "Hot", "High", "Weak", expected_status=400)
        print("\nAll API checks passed.")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Make sure the server is running, or set API_BASE_URL to your deployed backend.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
