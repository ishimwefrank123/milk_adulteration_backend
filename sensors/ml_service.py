import os
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
