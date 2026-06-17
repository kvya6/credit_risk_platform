"""
app.py — Credit Risk Intelligence Platform
Flask REST API backend (replaces Streamlit ui/app.py)
Serves 5 feature groups: EDA · Risk Predictor · Explainability · Business Rules · Talk-to-Data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import warnings
warnings.filterwarnings("ignore")

import json
import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR      = os.getenv("DATA_DIR",  "./data")
MODEL_DIR     = os.getenv("MODEL_DIR", "./models")
DB_PATH       = os.getenv("DB_PATH",   "./data/credit_risk.duckdb")
MODEL_PATH    = os.path.join(MODEL_DIR, "lgbm_model.joblib")
FEATURES_PATH = os.path.join(MODEL_DIR, "feature_names.joblib")
RULES_PATH    = os.path.join(MODEL_DIR, "rule_tree.joblib")
METRICS_PATH  = os.path.join(MODEL_DIR, "metrics.joblib")

FEATURE_LABELS = {
    'EXT_SOURCE_1': 'Credit Bureau Score 1',
    'EXT_SOURCE_2': 'Credit Bureau Score 2',
    'EXT_SOURCE_3': 'Credit Bureau Score 3',
    'AMT_INCOME_TOTAL': 'Annual Income',
    'AMT_CREDIT': 'Loan Amount',
    'AMT_ANNUITY': 'Annual Repayment',
    'AMT_GOODS_PRICE': 'Goods Price',
    'DAYS_BIRTH': 'Applicant Age',
    'DAYS_EMPLOYED': 'Employment Duration',
    'DAYS_REGISTRATION': 'Days Since Registration',
    'DAYS_ID_PUBLISH': 'Days Since ID Issued',
    'DAYS_LAST_PHONE_CHANGE': 'Days Since Phone Change',
    'CNT_CHILDREN': 'Number of Children',
    'CNT_FAM_MEMBERS': 'Family Size',
    'CODE_GENDER': 'Gender',
    'FLAG_OWN_CAR': 'Owns a Car',
    'FLAG_OWN_REALTY': 'Owns Property',
    'REGION_RATING_CLIENT': 'Region Risk Rating',
    'REGION_POPULATION_RELATIVE': 'Region Population Density',
    'NAME_EDUCATION_TYPE': 'Education Level',
    'NAME_INCOME_TYPE': 'Income Type',
    'NAME_CONTRACT_TYPE': 'Loan Contract Type',
    'ORGANIZATION_TYPE': 'Employer Organisation Type',
    'HOUR_APPR_PROCESS_START': 'Application Hour',
    'debt_to_income': 'Repayment-to-Income Ratio',
    'credit_to_income': 'Loan-to-Income Ratio',
    'age_years': 'Applicant Age (years)',
    'employment_years': 'Years Employed',
    'credit_term': 'Loan Term (years)',
}

# ── Cached loaders ────────────────────────────────────────────────────────────
_df_raw = None
_model = None
_feature_names = None
_rule_tree = None

def load_app_data():
    global _df_raw
    if _df_raw is None:
        path = os.path.join(DATA_DIR, "application_train.csv")
        if not os.path.exists(path):
            return None
        df = pd.read_csv(path, nrows=50000)
        df["age_years"] = (-df["DAYS_BIRTH"]) / 365
        df["DAYS_EMPLOYED"] = df["DAYS_EMPLOYED"].replace(365243, np.nan)
        df["employment_years"] = (-df["DAYS_EMPLOYED"]) / 365
        df["debt_to_income"] = df["AMT_ANNUITY"] / (df["AMT_INCOME_TOTAL"] + 1)
        _df_raw = df
    return _df_raw

def load_model():
    global _model, _feature_names
    if _model is None and os.path.exists(MODEL_PATH):
        _model = joblib.load(MODEL_PATH)
        _feature_names = joblib.load(FEATURES_PATH)
    return _model, _feature_names

def load_rule_tree():
    global _rule_tree
    if _rule_tree is None and os.path.exists(RULES_PATH):
        _rule_tree = joblib.load(RULES_PATH)
    return _rule_tree

def human_name(col):
    return FEATURE_LABELS.get(col, col.replace('_', ' ').title())

def safe_float(val):
    if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
        return None
    return val

def df_to_json(df):
    """Convert DataFrame to JSON-safe list of dicts."""
    records = []
    for rec in df.to_dict(orient="records"):
        clean = {}
        for k, v in rec.items():
            if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
                clean[k] = None
            elif isinstance(v, (np.integer,)):
                clean[k] = int(v)
            elif isinstance(v, (np.floating,)):
                clean[k] = float(v)
            else:
                clean[k] = v
        records.append(clean)
    return records

# ══════════════════════════════════════════════════════════════════════════════
# STATUS
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/status")
def status():
    return jsonify({
        "model_loaded": os.path.exists(MODEL_PATH),
        "db_ready": os.path.exists(DB_PATH),
        "data_ready": os.path.exists(os.path.join(DATA_DIR, "application_train.csv")),
    })

# ══════════════════════════════════════════════════════════════════════════════
# EDA
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/eda/summary")
def eda_summary():
    df = load_app_data()
    if df is None:
        return jsonify({"error": "Data not found. Place application_train.csv in data/ folder."}), 404

    # KPIs
    kpis = {
        "total_applicants": int(len(df)),
        "default_rate": round(float(df["TARGET"].mean() * 100), 2),
        "avg_loan": round(float(df["AMT_CREDIT"].mean()), 0),
        "avg_income": round(float(df["AMT_INCOME_TOTAL"].mean()), 0),
    }

    # Target distribution
    tc = df["TARGET"].value_counts()
    target_dist = [
        {"name": "Repaid", "value": int(tc.get(0, 0))},
        {"name": "Defaulted", "value": int(tc.get(1, 0))},
    ]

    # Default rate by gender
    gd = df.groupby("CODE_GENDER")["TARGET"].mean().reset_index()
    gender_default = [
        {"gender": str(r["CODE_GENDER"]), "rate": round(float(r["TARGET"]) * 100, 2)}
        for _, r in gd.iterrows()
    ]

    # Age vs default rate
    df2 = df.copy()
    df2["age_bin"] = pd.cut(df2["age_years"], bins=[20, 30, 40, 50, 60, 70],
                            labels=["20-30", "30-40", "40-50", "50-60", "60-70"])
    age_def = df2.groupby("age_bin")["TARGET"].mean().reset_index()
    age_default = [
        {"age_group": str(r["age_bin"]), "rate": round(float(r["TARGET"]) * 100, 2)}
        for _, r in age_def.iterrows() if not pd.isna(r["TARGET"])
    ]

    # Default by education
    ed = df.groupby("NAME_EDUCATION_TYPE")["TARGET"].mean().reset_index().sort_values("TARGET")
    edu_default = [
        {"education": str(r["NAME_EDUCATION_TYPE"]), "rate": round(float(r["TARGET"]) * 100, 2)}
        for _, r in ed.iterrows()
    ]

    # Income distribution (capped at 99th pct), sample 2000 pts
    cap = df["AMT_INCOME_TOTAL"].quantile(0.99)
    id2 = df[df["AMT_INCOME_TOTAL"] < cap].sample(min(2000, len(df)), random_state=42)
    income_dist = [
        {"income": float(r["AMT_INCOME_TOTAL"]), "target": int(r["TARGET"])}
        for _, r in id2.iterrows()
    ]

    # Default by income type
    it = df.groupby("NAME_INCOME_TYPE")["TARGET"].mean().reset_index().sort_values("TARGET", ascending=False)
    income_type_default = [
        {"income_type": str(r["NAME_INCOME_TYPE"]), "rate": round(float(r["TARGET"]) * 100, 2)}
        for _, r in it.iterrows()
    ]

    # Insights
    lower_sec_rate = df[df["NAME_EDUCATION_TYPE"] == "Lower secondary"]["TARGET"].mean() * 100
    higher_ed_rate = df[df["NAME_EDUCATION_TYPE"] == "Higher education"]["TARGET"].mean() * 100
    defaulter_income = df[df["TARGET"] == 1]["AMT_INCOME_TOTAL"].median()
    non_defaulter_income = df[df["TARGET"] == 0]["AMT_INCOME_TOTAL"].median()

    insights = [
        {"title": "🔴 Severe Class Imbalance",
         "text": f"Only {kpis['default_rate']:.1f}% defaulted — requires SMOTE or class weighting to avoid biased models."},
        {"title": "👶 Youth Risk",
         "text": "Applicants aged 20–30 default significantly more than older cohorts — age is a strong predictor."},
        {"title": "🎓 Education Signal",
         "text": f"Lower-secondary applicants default at {lower_sec_rate:.1f}% vs {higher_ed_rate:.1f}% for university-educated."},
        {"title": "💰 Income Threshold",
         "text": f"Defaulters' median income ₹{defaulter_income:,.0f} is lower than non-defaulters' ₹{non_defaulter_income:,.0f}."},
        {"title": "📊 Loan Size Risk",
         "text": "Larger loan amounts relative to income strongly predict default — credit-to-income ratio is a key risk driver."},
        {"title": "🏘️ Region Effect",
         "text": "Clients in Region Rating 3 (highest-risk regions) default at nearly 3× the rate of Region 1 clients."},
    ]

    return jsonify({
        "kpis": kpis,
        "target_dist": target_dist,
        "gender_default": gender_default,
        "age_default": age_default,
        "edu_default": edu_default,
        "income_dist": income_dist,
        "income_type_default": income_type_default,
        "insights": insights,
    })

# ══════════════════════════════════════════════════════════════════════════════
# RISK PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/predict", methods=["POST"])
def predict():
    model, feature_names = load_model()
    if model is None:
        return jsonify({"error": "Model not found. Run python setup_platform.py first."}), 404

    data = request.json
    applicant = {
        "AMT_INCOME_TOTAL":     float(data.get("amt_income", 180000)),
        "AMT_CREDIT":           float(data.get("amt_credit", 450000)),
        "AMT_ANNUITY":          float(data.get("amt_annuity", 22000)),
        "AMT_GOODS_PRICE":      float(data.get("amt_goods", 400000)),
        "DAYS_BIRTH":           -float(data.get("age", 35)) * 365,
        "DAYS_EMPLOYED":        -float(data.get("employment_years", 5)) * 365 if float(data.get("employment_years", 5)) > 0 else 365243,
        "CNT_CHILDREN":         int(data.get("cnt_children", 0)),
        "CNT_FAM_MEMBERS":      int(data.get("cnt_fam", 2)),
        "CODE_GENDER":          0 if data.get("gender", "F") == "F" else 1,
        "FLAG_OWN_CAR":         1 if data.get("own_car", "N") == "Y" else 0,
        "FLAG_OWN_REALTY":      1 if data.get("own_realty", "Y") == "Y" else 0,
        "REGION_RATING_CLIENT": int(data.get("region", 2)),
        "EXT_SOURCE_1":         float(data.get("ext1", 0.5)),
        "EXT_SOURCE_2":         float(data.get("ext2", 0.5)),
        "EXT_SOURCE_3":         float(data.get("ext3", 0.5)),
        "debt_to_income":       float(data.get("amt_annuity", 22000)) / (float(data.get("amt_income", 180000)) + 1),
        "credit_to_income":     float(data.get("amt_credit", 450000)) / (float(data.get("amt_income", 180000)) + 1),
        "age_years":            float(data.get("age", 35)),
        "employment_years":     float(data.get("employment_years", 5)),
        "credit_term":          float(data.get("amt_credit", 450000)) / (float(data.get("amt_annuity", 22000)) + 1),
    }

    row = pd.DataFrame([applicant])
    for col in feature_names:
        if col not in row.columns:
            row[col] = 0
    row = row[feature_names]

    prob  = model.predict_proba(row)[0][1]
    score = round(prob * 100, 1)
    band  = "Low" if prob < 0.3 else ("Medium" if prob < 0.6 else "High")

    amt_income  = float(data.get("amt_income", 180000))
    amt_credit  = float(data.get("amt_credit", 450000))
    amt_annuity = float(data.get("amt_annuity", 22000))

    result = {
        "probability": round(float(prob), 4),
        "score": float(score),
        "band": band,
        "credit_to_income": round(amt_credit / amt_income, 2),
        "repayment_to_income": round(amt_annuity / amt_income * 100, 1),
    }

    # Metrics
    if os.path.exists(METRICS_PATH):
        metrics = joblib.load(METRICS_PATH)
        report  = metrics.get("classification_report", {})
        cm      = metrics.get("confusion_matrix", None)
        result["metrics"] = {
            "roc_auc":  metrics.get("roc_auc", "—"),
            "pr_auc":   metrics.get("pr_auc", "—"),
            "n_features": len(feature_names),
            "f1":        report.get("1", {}).get("f1-score", report.get("macro avg", {}).get("f1-score", "—")),
            "precision": report.get("1", {}).get("precision", "—"),
            "recall":    report.get("1", {}).get("recall", "—"),
            "accuracy":  report.get("accuracy", "—"),
            "confusion_matrix": cm.tolist() if cm is not None else None,
        }

    # SHAP waterfall (top features for this applicant)
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        shap_vals = explainer(row)
        sv = shap_vals.values[0]
        base = float(shap_vals.base_values[0])
        feat_shap = sorted(
            [{"feature": human_name(f), "value": float(v), "raw": float(row[f].values[0])}
             for f, v in zip(feature_names, sv)],
            key=lambda x: abs(x["value"]), reverse=True
        )[:12]
        result["shap"] = {"base_value": base, "features": feat_shap}
    except Exception as e:
        result["shap"] = None

    return jsonify(result)

# ══════════════════════════════════════════════════════════════════════════════
# EXPLAINABILITY
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/explainability")
def explainability():
    model, feature_names = load_model()
    df = load_app_data()
    if model is None or df is None:
        return jsonify({"error": "Model and data required."}), 404

    try:
        import shap
        from src.data.preprocessor import preprocess

        sample = df.sample(min(500, len(df)), random_state=42).copy()
        dummy_target = pd.Series(0, index=sample.index, name="TARGET")
        sample_with_target = pd.concat([sample, dummy_target], axis=1)
        X_sample, _ = preprocess(sample_with_target)
        for f in feature_names:
            if f not in X_sample.columns:
                X_sample[f] = 0
        X_sample = X_sample[feature_names]

        explainer  = shap.TreeExplainer(model)
        sv         = explainer.shap_values(X_sample)
        if isinstance(sv, list):
            sv = sv[1]

        importance = np.abs(sv).mean(axis=0)
        feat_imp   = (
            pd.DataFrame({"feature": feature_names, "importance": importance})
            .sort_values("importance", ascending=False)
            .head(15)
        )
        feat_imp["label"] = feat_imp["feature"].apply(human_name)

        # Beeswarm data: top 10 features, 200 sample points each
        top10 = feat_imp["feature"].head(10).tolist()
        beeswarm = []
        for f in top10:
            idx = list(feature_names).index(f)
            vals = sv[:, idx].tolist()
            feat_vals = X_sample[f].tolist()
            beeswarm.append({
                "feature": human_name(f),
                "shap_values": [round(v, 5) for v in vals[:200]],
                "feature_values": [round(v, 5) if isinstance(v, float) else v for v in feat_vals[:200]],
            })

        return jsonify({
            "global_importance": df_to_json(feat_imp[["label", "importance"]].rename(columns={"label": "feature"})),
            "beeswarm": beeswarm,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ══════════════════════════════════════════════════════════════════════════════
# BUSINESS RULES
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/rules")
def rules():
    rule_tree    = load_rule_tree()
    model, feature_names = load_model()
    df           = load_app_data()

    if rule_tree is None:
        return jsonify({"error": "Run python setup_platform.py to derive rules first."}), 404
    if model is None or df is None:
        return jsonify({"error": "Data and model required."}), 404

    try:
        from src.data.preprocessor import preprocess
        from src.rules.rule_engine import derive_rules

        sample = df.sample(min(5000, len(df)), random_state=42).copy()
        X_s, y_s = preprocess(sample)
        feature_list = list(feature_names)
        for f in feature_list:
            if f not in X_s.columns:
                X_s[f] = 0
        X_s = X_s[feature_list]
        result = derive_rules(model, X_s, y_s)

        plain_rules  = result["plain_rules"]
        top_features = result["top_features"]

        tf_list = [
            {"feature": human_name(f), "importance": float(v)}
            for f, v in top_features.items()
        ]

        high_rules = [r for r in plain_rules if r["decision"] == 1][:5]
        low_rules  = [r for r in plain_rules if r["decision"] == 0][:5]

        raw_rules = ""
        rules_file = os.path.join(MODEL_DIR, "decision_rules.txt")
        if os.path.exists(rules_file):
            with open(rules_file) as f:
                raw_rules = f.read()

        return jsonify({
            "top_features": tf_list,
            "high_risk_rules": high_rules,
            "low_risk_rules": low_rules,
            "raw_rules": raw_rules,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ══════════════════════════════════════════════════════════════════════════════
# TALK TO DATA
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/ask", methods=["POST"])
def ask_data():
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return jsonify({"error": "GROQ_API_KEY not set. Add it to your .env file."}), 400

    if not os.path.exists(DB_PATH):
        df = load_app_data()
        if df is None:
            return jsonify({"error": "Place CSVs in data/ folder first."}), 404
        from src.talk_to_data.db_builder import build_db
        build_db()

    question = request.json.get("question", "")
    if not question:
        return jsonify({"error": "No question provided."}), 400

    try:
        from src.talk_to_data.nl_to_sql import ask
        result = ask(question)
        if result["data"] is not None:
            result["data"] = df_to_json(result["data"])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Serve React build in production ──────────────────────────────────────────
import mimetypes
from flask import send_from_directory

STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve React SPA. API routes above take priority."""
    if path and os.path.exists(os.path.join(STATIC_FOLDER, path)):
        return send_from_directory(STATIC_FOLDER, path)
    return send_from_directory(STATIC_FOLDER, 'index.html')


if __name__ == "__main__":
    app.run(debug=True, port=5000)
