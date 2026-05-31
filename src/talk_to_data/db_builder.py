"""
db_builder.py
Build a DuckDB database from the Home Credit CSV files.
Run once after placing CSVs in the data/ folder.
"""
import os
import duckdb
import pandas as pd

from src.utils.config import DATA_DIR, DB_PATH
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Columns we want in the applications table (subset for speed)
APP_COLS = [
    "SK_ID_CURR", "TARGET", "NAME_CONTRACT_TYPE", "CODE_GENDER",
    "FLAG_OWN_CAR", "FLAG_OWN_REALTY", "CNT_CHILDREN",
    "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE",
    "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE", "NAME_FAMILY_STATUS",
    "NAME_HOUSING_TYPE", "DAYS_BIRTH", "DAYS_EMPLOYED",
    "OCCUPATION_TYPE", "CNT_FAM_MEMBERS", "REGION_RATING_CLIENT"
]


def build_db(data_dir: str = DATA_DIR, db_path: str = DB_PATH):
    """Create/replace the DuckDB database with cleaned data."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = duckdb.connect(db_path)

    # --- applications table ---
    app_path = os.path.join(data_dir, "application_train.csv")
    if os.path.exists(app_path):
        logger.info("Loading application_train into DuckDB ...")
        app_df = pd.read_csv(app_path, usecols=[c for c in APP_COLS
                              if c in pd.read_csv(app_path, nrows=0).columns])
        conn.execute("DROP TABLE IF EXISTS applications")
        conn.execute("CREATE TABLE applications AS SELECT * FROM app_df")
        count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        logger.info(f"applications table: {count:,} rows")
    else:
        logger.warning("application_train.csv not found — skipping applications table.")

    # --- bureau_summary table ---
    bureau_path = os.path.join(data_dir, "bureau.csv")
    if os.path.exists(bureau_path):
        logger.info("Aggregating bureau.csv into DuckDB ...")
        bureau_df = pd.read_csv(bureau_path)
        agg = bureau_df.groupby("SK_ID_CURR").agg(
            bureau_loan_count=("SK_ID_BUREAU", "count"),
            bureau_active_loans=("CREDIT_ACTIVE", lambda x: (x == "Active").sum()),
            bureau_closed_loans=("CREDIT_ACTIVE", lambda x: (x == "Closed").sum()),
            bureau_avg_days_credit=("DAYS_CREDIT", "mean"),
            bureau_total_debt=("AMT_CREDIT_SUM_DEBT", "sum"),
            bureau_total_credit=("AMT_CREDIT_SUM", "sum"),
        ).reset_index()
        conn.execute("DROP TABLE IF EXISTS bureau_summary")
        conn.execute("CREATE TABLE bureau_summary AS SELECT * FROM agg")
        logger.info(f"bureau_summary table: {len(agg):,} rows")

    conn.close()
    logger.info(f"DuckDB database ready at {db_path}")


if __name__ == "__main__":
    build_db()
