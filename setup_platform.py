"""
setup_platform.py
One-shot setup script: builds DB + trains model.
Run after placing CSVs in data/.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.logger import get_logger
logger = get_logger("setup")

def main():
    logger.info("=== NeoStats Credit Risk Platform — Setup ===")

    # Step 1: Build DuckDB
    logger.info("Step 1/3: Building DuckDB database ...")
    from src.talk_to_data.db_builder import build_db
    build_db()

    # Step 2: Load + preprocess data
    logger.info("Step 2/3: Loading and preprocessing data ...")
    from src.data.loader import build_full_dataset
    from src.data.preprocessor import preprocess
    raw = build_full_dataset()
    X, y = preprocess(raw)

    # Step 3: Train model (and save metrics)
    logger.info("Step 3/4: Training LightGBM model ...")
    from src.ml.train import train
    results = train(X, y, use_smote=False)
    # Save metrics for UI display
    import joblib, os
    from src.utils.config import MODEL_DIR
    joblib.dump(results["metrics"], os.path.join(MODEL_DIR, "metrics.joblib"))

    # Step 4: Derive business rules
    logger.info("Step 4/4: Deriving business decision rules ...")
    import joblib, os
    from src.utils.config import MODEL_DIR
    from src.rules.rule_engine import derive_rules
    model = joblib.load(os.path.join(MODEL_DIR, "lgbm_model.joblib"))
    features = joblib.load(os.path.join(MODEL_DIR, "feature_names.joblib"))
    X_aligned = X[features]
    derive_rules(model, X_aligned, y)

    m = results["metrics"]
    logger.info(f"\n{'='*45}")
    logger.info(f"  ROC-AUC : {m['roc_auc']:.4f}")
    logger.info(f"  PR-AUC  : {m['pr_auc']:.4f}")
    logger.info(f"{'='*45}")
    logger.info("✅ Setup complete! Run: streamlit run ui/app.py")


if __name__ == "__main__":
    main()
