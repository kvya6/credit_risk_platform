"""
rule_engine.py
Derives human-readable business decision rules from the trained LightGBM model
using sklearn's DecisionTreeClassifier fitted on LightGBM's predictions.
This gives auditable, explainable IF-THEN rules for credit policy teams.
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from src.utils.config import MODEL_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)
RULES_PATH = os.path.join(MODEL_DIR, "decision_rules.txt")


# Human-readable feature name map
FEATURE_LABELS = {
    "EXT_SOURCE_2": "External Credit Score 2",
    "EXT_SOURCE_3": "External Credit Score 3",
    "EXT_SOURCE_1": "External Credit Score 1",
    "debt_to_income": "Debt-to-Income Ratio",
    "credit_to_income": "Credit-to-Income Ratio",
    "age_years": "Applicant Age (years)",
    "employment_years": "Employment Duration (years)",
    "AMT_CREDIT": "Loan Amount",
    "AMT_INCOME_TOTAL": "Annual Income",
    "DAYS_BIRTH": "Days Since Birth",
    "DAYS_EMPLOYED": "Days Since Employment Start",
    "AMT_ANNUITY": "Annual Repayment",
    "REGION_RATING_CLIENT": "Region Risk Rating (1=best, 3=worst)",
    "CNT_CHILDREN": "Number of Children",
    "bureau_total_debt": "Total External Debt",
    "bureau_loan_count": "Number of Prior Loans",
}


def derive_rules(model, X: pd.DataFrame, y: pd.Series, max_depth: int = 4) -> dict:
    """
    Fit a shallow decision tree on LightGBM predictions to extract business rules.
    Returns dict with rules text, tree model, and top decision features.
    """
    logger.info("Deriving business decision rules from ML model ...")

    # Use LightGBM soft predictions as pseudo-labels for the rule tree
    lgbm_proba = model.predict_proba(X)[:, 1]
    lgbm_pred = (lgbm_proba >= 0.5).astype(int)

    # Fit shallow decision tree
    rule_tree = DecisionTreeClassifier(
        max_depth=max_depth,
        min_samples_leaf=500,  # Each leaf = at least 500 applicants (robust rules)
        random_state=42,
        class_weight="balanced",
    )
    rule_tree.fit(X, lgbm_pred)

    # Export as text
    feature_names = list(X.columns)
    rules_text = export_text(rule_tree, feature_names=feature_names, max_depth=max_depth)

    # Get top features used in the tree
    importances = pd.Series(rule_tree.feature_importances_, index=feature_names)
    top_features = importances[importances > 0].sort_values(ascending=False).head(8)

    # Build plain-English rules summary
    plain_rules = _build_plain_rules(rule_tree, feature_names, X)

    # Save
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(RULES_PATH, "w") as f:
        f.write("=== CREDIT RISK DECISION RULES ===\n\n")
        f.write(rules_text)
    joblib.dump(rule_tree, os.path.join(MODEL_DIR, "rule_tree.joblib"))

    logger.info(f"Rules saved to {RULES_PATH}")
    return {
        "rule_tree": rule_tree,
        "rules_text": rules_text,
        "top_features": top_features,
        "plain_rules": plain_rules,
    }


def _build_plain_rules(tree, feature_names: list, X: pd.DataFrame) -> list[dict]:
    """Extract the most important IF-THEN rules from the decision tree."""
    rules = []
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != -2 else "leaf"
        for i in tree_.feature
    ]

    def get_label(feat):
        return FEATURE_LABELS.get(feat, feat.replace("_", " ").title())

    def recurse(node, conditions, depth):
        if depth > 3:
            return
        if tree_.feature[node] == -2:  # Leaf
            pred_class = np.argmax(tree_.value[node][0])
            n_samples = int(tree_.n_node_samples[node])
            default_rate = tree_.value[node][0][1] / tree_.n_node_samples[node]
            if conditions and n_samples > 200:
                risk = "HIGH RISK — Decline / Review" if pred_class == 1 else "LOW RISK — Approve"
                rules.append({
                    "conditions": list(conditions),
                    "outcome": risk,
                    "samples": n_samples,
                    "default_rate": round(default_rate * 100, 1),
                    "decision": pred_class,
                })
            return

        feat = feature_name[node]
        threshold = tree_.threshold[node]
        label = get_label(feat)

        # Left branch: feat <= threshold
        recurse(
            tree_.children_left[node],
            conditions + [f"{label} ≤ {threshold:.3f}"],
            depth + 1
        )
        # Right branch: feat > threshold
        recurse(
            tree_.children_right[node],
            conditions + [f"{label} > {threshold:.3f}"],
            depth + 1
        )

    recurse(0, [], 0)

    # Sort: high-risk rules first, then by sample count descending
    rules.sort(key=lambda r: (-r["decision"], -r["samples"]))
    return rules[:12]  # Top 12 most impactful rules


def load_rules():
    """Load saved rules text."""
    if os.path.exists(RULES_PATH):
        with open(RULES_PATH) as f:
            return f.read()
    return None


if __name__ == "__main__":
    from src.data.loader import build_full_dataset
    from src.data.preprocessor import preprocess
    import joblib

    raw = build_full_dataset()
    X, y = preprocess(raw)
    model = joblib.load(os.path.join(MODEL_DIR, "lgbm_model.joblib"))
    features = joblib.load(os.path.join(MODEL_DIR, "feature_names.joblib"))
    X = X[features]
    result = derive_rules(model, X, y)
    for rule in result["plain_rules"][:5]:
        print("\n→", rule["outcome"])
        for cond in rule["conditions"]:
            print(f"   IF {cond}")
        print(f"   ({rule['samples']:,} applicants, {rule['default_rate']}% default rate)")
