import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DATA_DIR = os.getenv("DATA_DIR", "./data")
MODEL_DIR = os.getenv("MODEL_DIR", "./models")
DB_PATH = os.getenv("DB_PATH", "./data/credit_risk.duckdb")

# ML config
RANDOM_STATE = 42
TEST_SIZE = 0.2
TARGET_COL = "TARGET"

# Risk band thresholds
RISK_LOW_MAX = 0.3
RISK_HIGH_MIN = 0.6
