"""
train.py
Train a LightGBM model to predict loan default probability.
Handles class imbalance with scale_pos_weight and optional SMOTE.
"""
import os
import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, average_precision_score,
    classification_report, confusion_matrix
)
from imblearn.over_sampling import SMOTE

from src.utils.config import RANDOM_STATE, TEST_SIZE, MODEL_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)
MODEL_PATH = os.path.join(MODEL_DIR, "lgbm_model.joblib")
FEATURES_PATH = os.path.join(MODEL_DIR, "feature_names.joblib")


def get_class_weight(y: pd.Series) -> float:
    """Compute scale_pos_weight = count(negative) / count(positive)."""
    neg = (y == 0).sum()
    pos = (y == 1).sum()
    weight = neg / pos
    logger.info(f"Class distribution — 0: {neg:,} | 1: {pos:,} | scale_pos_weight: {weight:.2f}")
    return weight


def train(X: pd.DataFrame, y: pd.Series, use_smote: bool = False) -> dict:
    """
    Train LightGBM model.
    Returns dict with model, metrics, and feature names.
    """
    logger.info("Splitting data into train/test ...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    if use_smote:
        logger.info("Applying SMOTE to training set ...")
        sm = SMOTE(random_state=RANDOM_STATE, sampling_strategy=0.3)
        X_train, y_train = sm.fit_resample(X_train, y_train)
        logger.info(f"After SMOTE — train shape: {X_train.shape}")

    scale_pos_weight = get_class_weight(y_train)

    logger.info("Training LightGBM model ...")
    model = LGBMClassifier(
        n_estimators=500,
        learning_rate=0.05,
        num_leaves=63,
        max_depth=-1,
        min_child_samples=50,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=-1,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        callbacks=[],
    )

    logger.info("Evaluating model ...")
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)

    roc_auc = roc_auc_score(y_test, y_proba)
    pr_auc = average_precision_score(y_test, y_proba)
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred).tolist()

    logger.info(f"ROC-AUC: {roc_auc:.4f} | PR-AUC: {pr_auc:.4f}")

    # Save
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(list(X.columns), FEATURES_PATH)
    logger.info(f"Model saved to {MODEL_PATH}")

    return {
        "model": model,
        "feature_names": list(X.columns),
        "metrics": {
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "classification_report": report,
            "confusion_matrix": cm,
        },
        "X_test": X_test,
        "y_test": y_test,
    }


if __name__ == "__main__":
    from src.data.loader import build_full_dataset
    from src.data.preprocessor import preprocess

    logger.info("=== Training Pipeline Start ===")
    raw = build_full_dataset()
    X, y = preprocess(raw)
    results = train(X, y, use_smote=False)
    print(f"\nROC-AUC : {results['metrics']['roc_auc']}")
    print(f"PR-AUC  : {results['metrics']['pr_auc']}")
