# 🏦 Credit Risk Intelligence Platform

> **Predict. Explain. Decide.**
> An end-to-end AI platform for credit risk scoring — powered by LightGBM, SHAP, Groq Llama-3, and DuckDB.

---

## 👀 What Does This Do?

This platform helps banks make faster, explainable, and auditable credit decisions. Upload applicant data, get an instant risk score, understand *why* the model made that call, and query the entire dataset in plain English.

| Tab | What You Get |
|-----|-------------|
| 📊 **EDA Dashboard** | Visual breakdown of 300K applicants — demographics, income, default patterns |
| 🎯 **Risk Predictor** | Enter applicant details → get a default probability + Approve / Review / Decline |
| 🔍 **Explainability** | SHAP charts showing exactly which features drove the risk score |
| 📋 **Business Rules** | Plain IF-THEN rules derived from the ML model — ready for policy teams |
| 💬 **Talk-to-Data** | Ask questions in plain English → get SQL-powered answers instantly |

---

## 🚀 Quick Start (5 Steps)

### Prerequisites

Before you begin, make sure you have:

- 🐳 [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
- 🔑 A free [Groq API key](https://console.groq.com) (for the chatbot)
- 📦 A [Kaggle account](https://www.kaggle.com) (for the dataset)

---

### Step 1 — Clone the repo

```bash
git clone https://github.com/kvya6/credit_risk_platform.git
cd credit_risk_platform
```

---

### Step 2 — Download the dataset

1. Go to 👉 https://www.kaggle.com/competitions/home-credit-default-risk/data
2. Click **Download All** and unzip
3. Copy the files into the `data/` folder:

```
data/
├── application_train.csv   ← Required (307K rows)
├── bureau.csv              ← Optional — adds ~2% accuracy
├── previous_application.csv  ← Optional
└── installments_payments.csv ← Optional
```

> 💡 Only `application_train.csv` is required to run. The others are optional but improve the model.

---

### Step 3 — Set your API key

```bash
cp .env.example .env
```

Open `.env` and paste your Groq key:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Leave everything else as-is.

---

### Step 4 — Train the model

```bash
docker-compose --profile setup run setup
```

This runs the full setup pipeline (~5–10 minutes):

```
✅ Loads data
✅ Cleans and engineers features
✅ Trains LightGBM model
✅ Computes SHAP values
✅ Builds DuckDB database
✅ Derives IF-THEN business rules
```

---

### Step 5 — Launch the app

```bash
docker-compose up
```

Open your browser and go to: **http://localhost:8501** 🎉

```bash
# To stop the app
docker-compose down

# To rebuild after code changes
docker-compose down && docker-compose up --build
```

---

## 🗂️ Project Structure

```
credit_risk_platform/
│
├── 📁 data/                    ← Your Kaggle CSVs go here (git-ignored)
├── 📁 models/                  ← Saved model artifacts (auto-generated)
├── 📁 documents/               ← Project presentation PDF
├── 📁 notebooks/               ← EDA notebook + script
│
├── 📁 src/
│   ├── data/                   ← loader.py, preprocessor.py
│   ├── ml/                     ← train.py, predict.py, evaluate.py
│   ├── rules/                  ← rule_engine.py (IF-THEN rule derivation)
│   ├── talk_to_data/           ← NL→SQL agent, DuckDB runner, prompt templates
│   └── utils/                  ← config.py, logger.py
│
├── 📁 ui/
│   ├── app.py                  ← Main Streamlit app
│   └── glass_theme.py          ← Dark glassmorphism CSS
│
├── 🐳 Dockerfile
├── 🐳 docker-compose.yml
├── 📄 requirements.txt
└── 📄 .env.example
```

---

## 🤖 The ML Model

**Model:** LightGBM Classifier
**Dataset:** Home Credit Default Risk (307,511 applicants, 122 features)
**Default rate:** 8.1% — severe class imbalance handled with `scale_pos_weight`

### Model Performance

| Metric | Score | What It Means |
|--------|-------|---------------|
| **ROC-AUC** | 0.7675 | 0.5 = random, 1.0 = perfect |
| **PR-AUC** | 0.2555 | 3.2× better than random baseline |
| **Recall** | 62.2% | Catches nearly 2 in 3 real defaulters |
| **Precision** | 19.1% | 1 in 5 flagged applicants actually defaults |
| **F1 Score** | 0.2916 | Balance between precision and recall |
| **Accuracy** | 75.6% | Overall correct predictions |

> ⚠️ High false positives are intentional — in banking, missing a defaulter costs more than extra caution.

### Top Risk Predictors (by SHAP)

| Rank | Feature | Effect |
|------|---------|--------|
| 1 | Credit Bureau Score 3 | Higher → lower risk |
| 2 | Education Level | Higher → lower risk |
| 3 | Credit Bureau Score 2 | Higher → lower risk |
| 4 | Loan Term | Longer → higher risk |
| 5 | Credit Bureau Score 1 | Higher → lower risk |

---

## 💬 Talk-to-Data Chatbot

Ask anything about the dataset in plain English. Groq's Llama-3 70B converts it to SQL, runs it on DuckDB, and returns a readable answer.

**Example questions you can ask:**

- *"What is the overall default rate?"*
- *"Which income type has the highest default rate?"*
- *"Average loan amount: male vs female?"*
- *"Default rate by education level?"*
- *"How many applicants own a car AND property?"*

### Hallucination Controls

The chatbot is designed to be reliable and safe:

- ✅ Schema-grounded prompts — the model can only reference real columns
- ✅ SELECT-only queries — no accidental data modification
- ✅ Auto-retry on SQL errors — feeds error back to model for correction
- ✅ `UNSUPPORTED_QUERY` fallback — model says so instead of hallucinating
- ✅ Row limit of 20 — prevents runaway queries

---

## 📋 Business Rules

The platform converts the black-box LightGBM model into readable IF-THEN rules — suitable for credit policy documentation and regulatory review.

**Sample rules:**

```
❌ HIGH RISK — Decline / Review
   IF Credit Bureau Score 3 ≤ 0.316
   → 734 applicants · 17.6% actual default rate

✅ LOW RISK — Approve
   IF Credit Bureau Score 3 > 0.316
   IF Credit Bureau Score 2 > 0.389
   IF Education Level ≤ 1.500
   → 925 applicants · 4.0% actual default rate
```

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ Yes | Get free at [console.groq.com](https://console.groq.com) |
| `DATA_DIR` | No (default: `./data`) | Path to your Kaggle CSVs |
| `MODEL_DIR` | No (default: `./models`) | Where model artifacts are saved |
| `DB_PATH` | No (default: `./data/credit_risk.duckdb`) | DuckDB database location |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| UI | Streamlit 1.35 |
| ML Model | LightGBM 4.3 |
| Explainability | SHAP 0.45 (TreeExplainer) |
| Database | DuckDB 0.10 |
| LLM | Groq / Llama-3 70B |
| Deployment | Docker + Docker Compose |
| Language | Python 3.11 |

---

## ⚠️ Known Limitations

| Limitation | Workaround |
|------------|-----------|
| Model trained without `bureau.csv` → ~2–3% lower accuracy | Add `bureau.csv` to `data/` and re-run setup |
| EDA uses 50K sample (not full 307K) | Statistically representative; increase in `eda.py` if needed |
| Chatbot limited to 2 tables | Can be extended in `db_builder.py` |
| No login / authentication | Not production-ready as-is |

---

## 📊 Dataset

- **Source:** [Home Credit Default Risk — Kaggle](https://www.kaggle.com/competitions/home-credit-default-risk/data)
- **Size:** 307,511 applications · 122 features
- **Target:** Binary — 1 = defaulted, 0 = repaid
- **Class balance:** 8.1% default · 91.9% repaid

---

## 🙋 FAQ

**Q: Do I need a paid Groq account?**
A: No — the free tier is sufficient. The chatbot uses Llama-3 70B with ~1s latency.

**Q: Can I run this without Docker?**
A: Yes — install dependencies from `requirements.txt` and run `python setup_platform.py` then `streamlit run ui/app.py`.

**Q: The model metrics look low — is that normal?**
A: PR-AUC of 0.2555 is actually 3.2× better than random (baseline ≈ 0.08) given the 8.1% default rate. Adding `bureau.csv` improves it further.

**Q: How long does setup take?**
A: First run takes 5–10 minutes. Subsequent launches are instant (model is cached).

---

*Built with ❤️ on the Home Credit Default Risk dataset.*