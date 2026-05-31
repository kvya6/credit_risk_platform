"""
predict.py
Load trained model and predict default probability + risk band for new applicants.
"""
import os
import joblib
import numpy as np
import pandas as pd

from src.utils.config import MODEL_DIR, RISK_LOW_MAX, RISK_HIGH_MIN
from src.utils.logger import get_logger

logger = get_logger(__name__)
MODEL_PATH = os.path.join(MODEL_DIR, "lgbm_model.joblib")
FEATURES_PATH = os.path.join(MODEL_DIR, "feature_names.joblib")


def load_model():
    """Load the saved model and feature list."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"No trained model found at {MODEL_PATH}. "
            "Please run the training pipeline first."
        )
    model = joblib.load(MODEL_PATH)
    features = joblib.load(FEATURES_PATH)
    return model, features


def get_risk_band(prob: float) -> str:
    """Map default probability to Low / Medium / High."""
    if prob < RISK_LOW_MAX:
        return "Low"
    elif prob < RISK_HIGH_MIN:
        return "Medium"
    else:
        return "High"


def predict_single(applicant_dict: dict) -> dict:
    """
    Predict for a single applicant given as a dict of feature values.
    Returns: probability, risk_band, risk_score (0-100)
    """
    model, features = load_model()
    row = pd.DataFrame([applicant_dict])

    # Align columns
    for col in features:
        if col not in row.columns:
            row[col] = 0
    row = row[features]

    prob = model.predict_proba(row)[0][1]
    band = get_risk_band(prob)
    score = round(prob * 100, 1)

    return {
        "default_probability": round(float(prob), 4),
        "risk_score": score,
        "risk_band": band,
    }


def predict_batch(df: pd.DataFrame) -> pd.DataFrame:
    """Predict for a DataFrame. Returns df with added prediction columns."""
    model, features = load_model()

    for col in features:
        if col not in df.columns:
            df[col] = 0
    X = df[features]

    probs = model.predict_proba(X)[:, 1]
    df = df.copy()
    df["default_probability"] = probs
    df["risk_score"] = (probs * 100).round(1)
    df["risk_band"] = [get_risk_band(p) for p in probs]
    return df


if __name__ == "__main__":
    sample = {"AMT_INCOME_TOTAL": 150000, "AMT_CREDIT": 400000, "AMT_ANNUITY": 20000}
    result = predict_single(sample)
    print(result)
