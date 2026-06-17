# ── Stage 1: Build React frontend ────────────────────────────────────────────
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python + Flask backend ──────────────────────────────────────────
FROM python:3.11-slim
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgomp1 && rm -rf /var/lib/apt/lists/*

# Python deps
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Project source (src/, models/, data/, sql/)
COPY ../src ./src
COPY ../models ./models
COPY ../data ./data
COPY ../sql ./sql
COPY ../setup_platform.py ./

# Flask backend
COPY backend/app.py ./

# React build output — served as static files by Flask
COPY --from=frontend-build /app/frontend/build ./static

# Patch Flask app to serve React build from /static
# (see app.py — it has a catch-all route below)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV DATA_DIR=/app/data
ENV MODEL_DIR=/app/models
ENV DB_PATH=/app/data/credit_risk.duckdb

EXPOSE 5000
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
