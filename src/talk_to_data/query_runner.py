"""
query_runner.py
Execute validated SQL queries against DuckDB and return results as a DataFrame.
"""
import os
import duckdb
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)

DB_PATH = os.getenv("DB_PATH", "./data/credit_risk.duckdb")


def run_query(sql: str, db_path: str = DB_PATH) -> pd.DataFrame:
    """
    Execute a SELECT query against DuckDB and return results as a DataFrame.
    Raises on execution errors so the caller can handle retry logic.
    """
    logger.info(f"Executing SQL: {sql[:120]}{'...' if len(sql) > 120 else ''}")
    conn = duckdb.connect(db_path, read_only=True)
    try:
        df = conn.execute(sql).df()
        logger.info(f"Query returned {len(df)} rows, {len(df.columns)} columns")
        return df
    finally:
        conn.close()


def run_query_safe(sql: str, db_path: str = DB_PATH) -> tuple:
    """
    Safe wrapper -- returns (DataFrame | None, error_message | None).
    Never raises. Use this in the UI layer.
    """
    try:
        df = run_query(sql, db_path)
        return df, None
    except Exception as e:
        logger.warning(f"Query failed: {e}")
        return None, str(e)


if __name__ == "__main__":
    df, err = run_query_safe("SELECT COUNT(*) AS total FROM applications")
    if err:
        print(f"Error: {err}")
    else:
        print(df)
