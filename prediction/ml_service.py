import os
import joblib
import pandas as pd
import xgboost as xgb

from django.conf import settings

BASE_DIR = settings.BASE_DIR

# ==========================================
# MODEL PATHS
# ==========================================

MODEL1_PATH = os.path.join(BASE_DIR, "sensors", "ml_models", "model1.json")
SCALER1_PATH = os.path.join(BASE_DIR, "sensors", "ml_models", "scaler.pkl")

MODEL2_TYPE_PATH = os.path.join(BASE_DIR, "sensors", "ml_models", "model2_type.pkl")
MODEL2_PCT_PATH = os.path.join(BASE_DIR, "sensors", "ml_models", "model2_pct.pkl")
SCALER2_PATH = os.path.join(BASE_DIR, "sensors", "ml_models", "scaler2.pkl")
LABEL_ENCODER_PATH = os.path.join(BASE_DIR, "sensors", "ml_models", "label_encoder.pkl")

# ==========================================
# LOAD MODELS ONCE
# ==========================================

# Model 1 (XGBoost)
scaler1 = joblib.load(SCALER1_PATH)

model1 = xgb.XGBClassifier()
model1.load_model(MODEL1_PATH)

# Model 2 (Random Forest)
scaler2 = joblib.load(SCALER2_PATH)

model2_type = joblib.load(MODEL2_TYPE_PATH)
model2_pct = joblib.load(MODEL2_PCT_PATH)

label_encoder = joblib.load(LABEL_ENCODER_PATH)


def predict_milk_quality(
    ph,
    temperature,
    taste,
    odor,
    fat,
    turbidity,
    colour
):
    """
    Two-stage prediction:

    Stage 1:
        PURE vs ADULTERATED

    Stage 2:
        Adulteration Type + Percentage
    """

    # ==========================================
    # CREATE INPUT DATAFRAME
    # ==========================================

    feature_names = [
        "pH",
        "Temprature",
        "Taste",
        "Odor",
        "Fat",
        "Turbidity",
        "Colour"
    ]

    raw_input = pd.DataFrame(
        [[
            ph,
            temperature,
            taste,
            odor,
            fat,
            turbidity,
            colour
        ]],
        columns=feature_names
    )

    # ==========================================
    # STAGE 1
    # PURE vs ADULTERATED
    # ==========================================

    scaled_input_1 = scaler1.transform(raw_input)

    prediction = model1.predict(scaled_input_1)[0]

    probability = model1.predict_proba(
        scaled_input_1
    )[0]

    confidence = float(
        probability[prediction] * 100
    )

    # IMPORTANT:
    # Verify from your notebook:
    # 0 = PURE ?
    # 1 = ADULTERATED ?
    #
    # If opposite, swap the condition below.

    if prediction == 1:

        return {
            "status": "GOOD",
            "confidence": round(confidence, 2),
            "adulteration_type": None,
            "percentage": 0.0,
            "reasons": "Milk classified as pure."
        }

    # ==========================================
    # STAGE 2
    # TYPE + PERCENTAGE
    # ==========================================

    scaled_input_2 = scaler2.transform(raw_input)

    type_code = model2_type.predict(
        scaled_input_2
    )[0]

    adulteration_type = label_encoder.inverse_transform(
        [type_code]
    )[0]

    percentage = float(
        model2_pct.predict(
            scaled_input_2
        )[0]
    )

    percentage = max(0.0, percentage)

    return {
        "status": "BAD",
        "confidence": round(confidence, 2),
        "adulteration_type": adulteration_type,
        "percentage": round(percentage, 2),
        "reasons": f"Detected {adulteration_type}"
    }