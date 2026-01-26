"""
Inference Code for PlayTennis Classification
Add this code as a new cell at the end of your classification.ipynb notebook
"""

import pickle
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Step 1: Load the original data to recreate encoders
df_original = pd.read_csv("playtennis.csv")
df_original = pd.DataFrame(df_original)

# Step 2: Handle missing values (same as training)
df_original["Wind"] = df_original["Wind"].fillna(df_original["Wind"].mode()[0])

# Step 3: Create and fit label encoders for each feature column
feature_encoders = {}
feature_columns = ['Outlook', 'Temperature', 'Humidity', 'Wind']

for col in feature_columns:
    le = LabelEncoder()
    le.fit(df_original[col])
    feature_encoders[col] = le

# Also create encoder for target to decode predictions
target_encoder = LabelEncoder()
target_encoder.fit(df_original['PlayTennis'])

# Step 4: Load the saved model
with open('ensemble_model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

print("Model loaded successfully!")
print(f"Feature encodings:")
for col in feature_columns:
    print(f"  {col}: {dict(zip(feature_encoders[col].classes_, feature_encoders[col].transform(feature_encoders[col].classes_)))}")

# Step 5: Create inference function
def predict_play_tennis(outlook, temperature, humidity, wind):
    """
    Predict whether to play tennis given weather conditions
    
    Parameters:
    -----------
    outlook : str
        Weather outlook (e.g., 'Sunny', 'Overcast', 'Rain')
    temperature : str
        Temperature level (e.g., 'Hot', 'Mild', 'Cool')
    humidity : str
        Humidity level (e.g., 'High', 'Normal')
    wind : str
        Wind condition (e.g., 'Weak', 'Strong')
    
    Returns:
    --------
    str : Prediction ('Yes' or 'No')
    """
    try:
        # Encode the input features
        encoded_outlook = feature_encoders['Outlook'].transform([outlook])[0]
        encoded_temperature = feature_encoders['Temperature'].transform([temperature])[0]
        encoded_humidity = feature_encoders['Humidity'].transform([humidity])[0]
        encoded_wind = feature_encoders['Wind'].transform([wind])[0]
        
        # Create input array
        input_data = [[encoded_outlook, encoded_temperature, encoded_humidity, encoded_wind]]
        
        # Make prediction
        prediction_encoded = loaded_model.predict(input_data)[0]
        
        # Decode prediction
        prediction = target_encoder.inverse_transform([prediction_encoded])[0]
        
        return prediction
    except Exception as e:
        return f"Error: {str(e)}"

# Step 6: Example usage with the data provided by user
print("\n" + "="*50)
print("EXAMPLE PREDICTIONS")
print("="*50)

# Test with the example data from user's request
test_cases = [
    {'Outlook': 'Sunny', 'Temperature': 'Hot', 'Humidity': 'High', 'Wind': 'Weak'},
    {'Outlook': 'Overcast', 'Temperature': 'Mild', 'Humidity': 'Normal', 'Wind': 'Strong'},
    {'Outlook': 'Overcast', 'Temperature': 'Cool', 'Humidity': 'Normal', 'Wind': 'Weak'},  # Note: Wind was NaN in original, using 'Weak' as default
    {'Outlook': 'Rain', 'Temperature': 'Mild', 'Humidity': 'High', 'Wind': 'Strong'},
    {'Outlook': 'Rain', 'Temperature': 'Hot', 'Humidity': 'Normal', 'Wind': 'Weak'},
]

for i, test_case in enumerate(test_cases):
    result = predict_play_tennis(
        test_case['Outlook'],
        test_case['Temperature'],
        test_case['Humidity'],
        test_case['Wind']
    )
    print(f"\nTest Case {i+1}:")
    print(f"  Input: {test_case}")
    print(f"  Prediction: Play Tennis = {result}")
