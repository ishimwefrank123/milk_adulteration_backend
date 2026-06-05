import os
import joblib  # Use joblib as it was used for saving the scaler
import numpy as np
import xgboost as xgb

# --- Path Configuration ---
# The model files ('scaler.pkl', 'model1.json') should be in the same directory as this file.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCALER_PATH = os.path.join(BASE_DIR, 'scaler.pkl') # Corrected filename from your Colab
MODEL_PATH = os.path.join(BASE_DIR, 'model1.json')

# --- Global Variables for Model and Scaler ---
scaler = None
model = None

# --- Loading Artifacts ---
try:
    # 1. Load the Scaler using joblib
    scaler = joblib.load(SCALER_PATH)
    print("--- Scaler loaded successfully ---")

    # 2. Load the XGBoost Model
    model = xgb.XGBClassifier()
    model.load_model(MODEL_PATH)
    print("--- XGBoost model loaded successfully ---")

except FileNotFoundError as e:
    print(f"ERROR: Model or scaler file not found. Make sure 'scaler.pkl' and 'model1.json' are in the same directory as ml_service.py. Details: {e}")
except Exception as e:
    print(f"An unexpected error occurred during model loading: {e}")
    scaler = None
    model = None

# --- Prediction Function ---
# IMPORTANT: The function signature and feature order MUST match your training script.
# Your Colab script used 7 features: ['pH', 'Temprature', 'Taste', 'Odor', 'Fat', 'Turbidity', 'Colour']
def predict_milk_quality(ph, temperature, taste, odor, fat, turbidity, colour):
    """
    Scales input data and predicts milk quality using the loaded XGBoost model.
    """
    if scaler is None or model is None:
        raise Exception("Model or Scaler not loaded properly. Check server logs for details.")

    # 1. Prepare features array in the EXACT order used for training
    # The order from your Colab notebook was: pH, Temprature, Taste, Odor, Fat, Turbidity, Colour
    features = np.array([[ph, temperature, taste, odor, fat, turbidity, colour]])

    # 2. Scale features using the loaded scaler
    scaled_features = scaler.transform(features)

    # 3. Make prediction and get probabilities
    prediction_class = model.predict(scaled_features)[0]
    prediction_proba = model.predict_proba(scaled_features)[0]

    # 4. Interpret results based on your Colab encoding
    # 'low' (Adulterated) was encoded as 0
    # 'medium'/'high' (Pure) was encoded as 1
    if prediction_class == 0:  # Adulterated
        # The probability of being adulterated is the probability of class 0
        adulteration_percentage = prediction_proba[0] * 100
        return {
            'status': 'BAD',
            'adulteration_type': 'Suspected Adulteration',  # Binary model can't specify the type
            'percentage': round(adulteration_percentage, 2),
            'reasons': f'ML model predicted low quality with {adulteration_percentage:.2f}% confidence.'
        }
    else:  # Pure
        # The probability of being pure is the probability of class 1
        purity_percentage = prediction_proba[1] * 100
        return {
            'status': 'GOOD',
            'adulteration_type': None,
            'percentage': 0.0,  # Percentage of adulteration is 0
            'reasons': f'ML model predicted good quality with {purity_percentage:.2f}% confidence.'
        }
import joblib
import numpy as np
import xgboost as xgb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCALER_PATH = os.path.join(BASE_DIR, 'scaler.pkl')
MODEL_PATH  = os.path.join(BASE_DIR, 'model1.json')

scaler = None
model  = None

try:
    scaler = joblib.load(SCALER_PATH)
    print("--- Scaler loaded successfully ---")
    model = xgb.XGBClassifier()
    model.load_model(MODEL_PATH)
    print("--- XGBoost model loaded successfully ---")
except FileNotFoundError as e:
    print(f"ERROR: Model file not found: {e}")
    print("Place 'scaler.pkl' and 'model1.json' in the sensors/ folder.")
except Exception as e:
    print(f"Unexpected error loading model: {e}")
    scaler = None
    model  = None


def predict_milk_quality(ph, temperature, taste, odor, fat, turbidity, colour):
    """
    Predicts milk quality using XGBoost.
    Features order: pH, Temperature, Taste, Odor, Fat, Turbidity, Colour
    Returns dict with status, adulteration_type, percentage, reasons.
    """
    if scaler is None or model is None:
        raise Exception("Model not loaded. Place 'scaler.pkl' and 'model1.json' in sensors/ folder.")

    features = np.array([[ph, temperature, taste, odor, fat, turbidity, colour]])
    scaled   = scaler.transform(features)

    prediction_class = model.predict(scaled)[0]
    prediction_proba = model.predict_proba(scaled)[0]

    if prediction_class == 0:  # Adulterated (class 0 = BAD)
        pct = round(float(prediction_proba[0]) * 100, 2)
        return {
            'status':            'BAD',
            'adulteration_type': 'Suspected Adulteration',
            'percentage':        pct,
            'reasons':           f'ML model predicted low quality with {pct}% confidence.',
        }
    else:  # Pure (class 1 = GOOD)
        pct = round(float(prediction_proba[1]) * 100, 2)
        return {
            'status':            'GOOD',
            'adulteration_type': None,
            'percentage':        0.0,
            'reasons':           f'ML model predicted good quality with {pct}% confidence.',
        }
