# Credit Risk Platform — React + Flask UI

This replaces the Streamlit `ui/app.py` with a proper **React.js frontend + Flask REST API backend**.
Everything in `src/`, `models/`, `data/`, `sql/`, `setup_platform.py`, `notebooks/` is **unchanged**.

---

## What changed

| Before | After |
|---|---|
| `ui/app.py` (Streamlit) | `ui_web/backend/app.py` (Flask) |
| `ui/glass_theme.py` | `ui_web/frontend/src/index.css` |
| `streamlit==1.35.0` in requirements | `flask==3.0.3` + `flask-cors==4.0.1` |
| `streamlit run ui/app.py` | Flask API on `:5000` + React dev on `:3000` |

---

## Project structure

```
ui_web/                         ← this folder (drop alongside existing src/, models/, etc.)
├── backend/
│   ├── app.py                  ← Flask REST API (5 endpoints, mirrors all 5 Streamlit tabs)
│   └── requirements.txt        ← pip deps (streamlit removed, flask added)
├── frontend/
│   ├── package.json
│   ├── public/index.html
│   └── src/
│       ├── index.js
│       ├── index.css           ← glassmorphism theme (same visual as original)
│       ├── App.jsx             ← sidebar + tab routing
│       └── tabs/
│           ├── EDA.jsx
│           ├── RiskPredictor.jsx
│           ├── Explainability.jsx
│           ├── BusinessRules.jsx
│           └── TalkToData.jsx
├── Dockerfile
└── docker-compose.yml
```

---

## Running locally (development)

### 1. Install Python deps
```bash
pip install -r ui_web/backend/requirements.txt
```

### 2. Train the model (if not already done)
```bash
python setup_platform.py
```

### 3. Start Flask backend
```bash
cd <project-root>
FLASK_APP=ui_web/backend/app.py GROQ_API_KEY=gsk_xxx python -m flask run --port 5000
```

### 4. Start React frontend (new terminal)
```bash
cd ui_web/frontend
npm install
npm start          # opens http://localhost:3000
```

React's `proxy` in `package.json` forwards `/api/*` → `http://localhost:5000` automatically.

---

## Production (Docker)

```bash
# From project root
docker compose -f ui_web/docker-compose.yml up --build
# Open http://localhost:5000
```

In production the Flask server serves the React build as static files — no separate Node process needed.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/status` | Model/DB/data readiness |
| GET | `/api/eda/summary` | All EDA data (KPIs, charts, insights) |
| POST | `/api/predict` | Risk prediction + SHAP waterfall |
| GET | `/api/explainability` | Global SHAP importance + beeswarm |
| GET | `/api/rules` | IF-THEN business rules |
| POST | `/api/ask` | Talk-to-Data (Groq NL→SQL) |

---

## .env (same as before)
```
GROQ_API_KEY=gsk_your_key_here
DATA_DIR=./data
MODEL_DIR=./models
DB_PATH=./data/credit_risk.duckdb
```
