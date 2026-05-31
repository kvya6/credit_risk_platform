# 🏦 — AI-Powered Credit Risk Intelligence Platform

> **Intelligence. Innovation. Impact.**  
> End-to-end credit risk platform: EDA · ML Prediction · SHAP Explainability · NL-to-SQL Chatbot

---

## 📋 Table of Contents
- [Architecture Overview](#architecture-overview)
- [Quick Start (5 Steps)](#quick-start-5-steps)
- [Project Structure](#project-structure)
- [Module Breakdown](#module-breakdown)
- [Model Details](#model-details)
- [Talk-to-Data Chatbot](#talk-to-data-chatbot)
- [Evaluation Metrics](#evaluation-metrics)
- [Design Decisions](#design-decisions)
- [Known Limitations](#known-limitations)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Streamlit UI (Port 8501)                    │
│  ┌──────────┐  ┌──────────────┐  ┌────────────┐  ┌─────────┐    │
│  │ EDA Tab  │  │ Risk Predict │  │ SHAP/XAI   │  │Chatbot  │    │
│  └──────────┘  └──────────────┘  └────────────┘  └─────────┘    │
└──────────┬──────────────┬──────────────┬──────────────┬─────────┘
           │              │              │              │
    ┌──────▼──────┐ ┌─────▼──────┐ ┌───▼────┐  ┌─────▼──────┐
    │  Pandas EDA │ │ LightGBM   │ │  SHAP  │  │ Claude API │
    │  Plotly     │ │ Classifier │ │  Tree  │  │ NL → SQL   │
    └─────────────┘ └─────▲──────┘ └────────┘  └─────▼──────┘
                          │                          │
                 ┌────────▼──────────────────────────▼────────┐
                 │           Data Layer                        │
                 │  application_train.csv  →  DuckDB           │
                 │  bureau.csv             →  aggregated       │
                 │  previous_application   →  joined           │
                 └─────────────────────────────────────────────┘
```

---

## Quick Start (5 Steps)

### Prerequisites
- Docker Desktop installed and running
- Kaggle account (to download dataset)
- API key ([get one here](https://console.groq.com))

---

### Step 1 — Clone the Repository
```bash
git clone https://github.com/kvya6/credit_risk_platform.git
cd credit_risk_platform
```

---

### Step 2 — Download the Dataset
1. Go to: https://www.kaggle.com/competitions/home-credit-default-risk/data
2. Click **Download All** → you'll get `home-credit-default-risk.zip`
3. Unzip it and place these files inside the `data/` folder:
   ```
   data/
   ├── application_train.csv      ← Required
   ├── bureau.csv                 ← Required
   ├── previous_application.csv   ← Optional (improves model)
   └── installments_payments.csv  ← Optional (improves model)
   ```

---

### Step 3 — Set Up Environment Variables
```bash
# Copy the example env file
cp .env.example .env

# Open .env and add your groq API key:
# groq_API_KEY=sk-ant-...your-key-here...
```

---

### Step 4 — Train the Model & Build the Database
```bash
# This runs preprocessing, trains LightGBM, and builds DuckDB
docker-compose --profile setup run setup
```
> ⏱️ This takes ~5–10 minutes on first run. You'll see ROC-AUC and PR-AUC printed when done.

---

### Step 5 — Launch the Platform
```bash
docker-compose up
```
Open your browser: **http://localhost:8501**

---

## Project Structure

```
credit_risk_platform/
├── data/                          ← Kaggle CSVs (NOT committed to git)
│   └── eda_outputs/               ← EDA plots saved here
├── documents/
│   └── project_presentation.pdf  ← Project slides
├── notebooks/
│   └── eda.py                     ← EDA script (run standalone)
├── src/
│   ├── data/
│   │   ├── loader.py              ← Load & join all CSV tables
│   │   └── preprocessor.py       ← Clean, encode, impute, engineer features
│   ├── ml/
│   │   ├── train.py               ← LightGBM training pipeline
│   │   ├── predict.py             ← Inference + risk banding
│   │   └── evaluate.py            ← SHAP explanations & metrics
│   ├── talk_to_data/
│   │   ├── nl_to_sql.py           ← Claude-powered NL → SQL agent
│   │   ├── db_builder.py          ← Build DuckDB from CSVs
│   │   └── prompt_templates.py    ← Versioned, schema-grounded prompts
│   └── utils/
│       ├── config.py              ← Centralised config & env vars
│       └── logger.py              ← Structured logging
├── sql/
│   └── schema.sql                 ← DuckDB table definitions
├── models/                        ← Saved model artifacts (git-ignored)
├── ui/
│   └── app.py                     ← Full Streamlit multi-tab UI
├── setup_platform.py              ← One-shot setup runner
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Module Breakdown

### Module 1: EDA Dashboard
- Dataset summary (rows, columns, dtypes, null rates)
- Target distribution (class imbalance visualised)
- Default rate by gender, education, income type, age
- Income and loan amount distributions
- Correlation heatmap
- 5 key business insights

### Module 2: Talk-to-Data Chatbot
- Powered by **Groq / Llama-3 70B** (llama-3.3-70b-versatile)
- Schema-grounded system prompt → prevents hallucination
- SQL validation before execution (blocks DDL/DML)
- DuckDB backend for fast local queries
- Plain-English summary of every result
- 8 pre-built example questions

### Module 3: Machine Learning Layer
- **Model**: LightGBM Classifier
- **Imbalance handling**: `scale_pos_weight` (auto-computed) + optional SMOTE
- **Output**: default probability, risk score (0-100), risk band (Low/Medium/High)
- **Evaluation**: ROC-AUC, PR-AUC, confusion matrix, classification report

### Module 4: Explainable AI
- **SHAP TreeExplainer** (native LightGBM support — fast)
- Global feature importance (mean |SHAP| bar chart)
- Beeswarm summary plot (per-sample impact)
- Per-prediction waterfall chart
- Human-readable interpretation guide

### Module 5: Dockerized Deployment
- Single Dockerfile + docker-compose.yml
- Data mounted as volume (not baked into image)
- Model artifacts persist on host via volume mount
- `docker-compose up` → full platform running

---

## Model Details

### Why LightGBM?
- **Speed**: Handles 300K+ rows in minutes
- **Performance**: Consistently top performer on tabular credit data
- **SHAP compatibility**: Native TreeExplainer support — fast and exact
- **Imbalance handling**: Built-in `scale_pos_weight` parameter

### Class Imbalance Strategy
The dataset has ~8% default rate (severe imbalance). We use:
1. **`scale_pos_weight`** = count(0) / count(1) ≈ 11 — built into LightGBM
2. **Optional SMOTE** (set `use_smote=True` in train.py) for oversampling minority class
3. **PR-AUC** as primary metric (more meaningful than accuracy under imbalance)

### Feature Engineering
| Feature | Description |
|---------|-------------|
| `debt_to_income` | AMT_ANNUITY / AMT_INCOME_TOTAL |
| `credit_to_income` | AMT_CREDIT / AMT_INCOME_TOTAL |
| `age_years` | -DAYS_BIRTH / 365 |
| `employment_years` | -DAYS_EMPLOYED / 365 |
| `credit_term` | AMT_CREDIT / AMT_ANNUITY |

---

## Talk-to-Data Chatbot

### How It Works
```
User question → Claude (NL→SQL) → Validate SQL → DuckDB → Claude (Summarise) → Answer
```

### Hallucination Controls
1. **Schema-grounded prompts** — Claude only knows the exact columns that exist
2. **SQL validation layer** — rejects any non-SELECT query before execution
3. **UNSUPPORTED_QUERY sentinel** — Claude returns this if question can't be answered
4. **Error handling** — graceful fallback with user-friendly messages

### Example Working Queries
1. "What is the overall default rate?"
2. "Which income type has the highest default rate?"
3. "What is the average loan amount for male vs female applicants?"
4. "How does education level affect default probability?"
5. "Show top 5 occupations by number of applicants"
6. "What is the average income for defaulters vs non-defaulters?"
7. "How many applicants own a car and also own real estate?"
8. "Show default rate by region risk rating"

---

## Evaluation Metrics

| Metric | Expected Range | Notes |
|--------|---------------|-------|
| ROC-AUC | 0.74 – 0.78 | Area under ROC curve |
| PR-AUC | 0.25 – 0.35 | Better metric for imbalanced data |
| Precision (default=1) | ~0.35 | Of predicted defaulters, % actually defaulting |
| Recall (default=1) | ~0.60 | Of actual defaulters, % we catch |

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| ML Model | LightGBM | Best perf/speed ratio on tabular credit data; SHAP-native |
| Database | DuckDB | Zero-config, embedded, excellent SQL support |
| LLM | Groq / Llama-3 70B | Free tier, low latency, strong SQL generation, schema-grounded prompts |
| UI | Streamlit | Python-native, fast to build, easy to Dockerize |
| Imbalance | scale_pos_weight | No data modification needed; preserves real distribution |
| SHAP | TreeExplainer | Exact (not approximate), fastest for tree models |

---

## Known Limitations & Possible Improvements

### Current Limitations
- Model trained only on `application_train.csv` + bureau aggregates (for speed)
- SHAP computed on 500-sample subset in UI (full computation is slow)
- Talk-to-data limited to 2 tables (applications, bureau_summary)
- No authentication on the UI

### Possible Improvements
- Add `POS_CASH_balance.csv` and `credit_card_balance.csv` for richer features
- Hyperparameter tuning with Optuna
- Add confidence intervals to predictions
- Expand DuckDB schema to include all 7 source tables
- Add model retraining trigger from UI
- Add PDF export of risk report per applicant

