"""
nl_to_sql.py
Convert natural language questions to SQL using Groq (free),
execute against DuckDB, and return plain-English summaries.
"""
import re
import os
from groq import Groq
import duckdb
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DB_PATH = os.getenv("DB_PATH", "./data/credit_risk.duckdb")

client = Groq(api_key=GROQ_API_KEY)

NL_TO_SQL_SYSTEM = """
You are a precise SQL assistant for a credit risk database.

You have access to a DuckDB database with the following tables:

TABLE: applications
  - SK_ID_CURR        INTEGER  -- unique applicant ID
  - TARGET            INTEGER  -- 1 = defaulted, 0 = repaid
  - NAME_CONTRACT_TYPE VARCHAR -- 'Cash loans' or 'Revolving loans'
  - CODE_GENDER       VARCHAR  -- 'M' or 'F'
  - FLAG_OWN_CAR      VARCHAR  -- 'Y' or 'N'
  - FLAG_OWN_REALTY   VARCHAR  -- 'Y' or 'N'
  - CNT_CHILDREN      INTEGER  -- number of children
  - AMT_INCOME_TOTAL  DOUBLE   -- annual income
  - AMT_CREDIT        DOUBLE   -- loan amount
  - AMT_ANNUITY       DOUBLE   -- annual repayment
  - AMT_GOODS_PRICE   DOUBLE   -- price of goods
  - NAME_INCOME_TYPE  VARCHAR  -- e.g. 'Working', 'Pensioner'
  - NAME_EDUCATION_TYPE VARCHAR -- e.g. 'Higher education'
  - NAME_FAMILY_STATUS VARCHAR -- e.g. 'Married'
  - NAME_HOUSING_TYPE  VARCHAR -- e.g. 'House / apartment'
  - DAYS_BIRTH        INTEGER  -- negative days before application
  - DAYS_EMPLOYED     INTEGER  -- negative = employed; 365243 = unemployed
  - OCCUPATION_TYPE   VARCHAR  -- e.g. 'Laborers', 'Managers'
  - CNT_FAM_MEMBERS   DOUBLE   -- family size
  - REGION_RATING_CLIENT INTEGER -- region risk rating 1=best 3=worst

TABLE: bureau_summary
  - SK_ID_CURR            INTEGER
  - bureau_loan_count     INTEGER
  - bureau_active_loans   INTEGER
  - bureau_closed_loans   INTEGER
  - bureau_avg_days_credit DOUBLE
  - bureau_total_debt     DOUBLE
  - bureau_total_credit   DOUBLE

RULES:
1. Output ONLY a valid DuckDB SQL query — no explanation, no markdown, no comments.
2. Only use tables and columns listed above. Never invent column names.
3. Always add LIMIT 20 unless user specifies otherwise.
4. Round floats to 2 decimal places using ROUND(..., 2).
5. If the question cannot be answered, output exactly: UNSUPPORTED_QUERY
6. Never use DROP, DELETE, INSERT, UPDATE, ALTER, CREATE, TRUNCATE.
7. Always start with SELECT.
"""

SUMMARY_SYSTEM = """
You are a business analyst explaining SQL query results to non-technical banking staff.
Write 2-3 clear sentences summarising the key finding. Be specific with numbers.
Do not mention SQL or technical terms. Keep it professional and concise.
"""

BLOCKED = re.compile(r"\b(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE|TRUNCATE)\b", re.IGNORECASE)


def generate_sql(question: str, error_context: str = "") -> str:
    user_msg = question
    if error_context:
        user_msg = f"{question}\n\n[Previous attempt failed: {error_context}. Please fix the SQL.]"
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": NL_TO_SQL_SYSTEM},
            {"role": "user",   "content": user_msg},
        ],
        temperature=0,
        max_tokens=512,
    )
    sql = response.choices[0].message.content.strip()
    sql = re.sub(r"```sql|```", "", sql).strip()
    return sql


def validate_sql(sql: str) -> tuple:
    if sql == "UNSUPPORTED_QUERY":
        return False, "This question cannot be answered with the available data."
    if BLOCKED.search(sql):
        return False, "Query blocked: only SELECT statements are allowed."
    if not sql.upper().strip().startswith("SELECT"):
        return False, "Generated query does not start with SELECT — blocked for safety."
    return True, ""


# run_query is now in query_runner.py (single-responsibility module)
from src.talk_to_data.query_runner import run_query


def summarise_results(question: str, df: pd.DataFrame) -> str:
    if df.empty:
        return "The query returned no results."
    table_str = df.to_string(index=False, max_rows=20)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SUMMARY_SYSTEM},
            {"role": "user",   "content": f"Question: {question}\n\nResults:\n{table_str}\n\nSummarise in 2-3 plain English sentences."},
        ],
        temperature=0.3,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


def ask(question: str, max_retries: int = 2) -> dict:
    logger.info(f"Question: {question}")
    result = {"question": question, "sql": None, "data": None, "summary": None, "error": None}
    last_error = ""

    for attempt in range(max_retries + 1):
        try:
            sql = generate_sql(question, error_context=last_error)
            result["sql"] = sql
            logger.info(f"SQL (attempt {attempt+1}): {sql}")

            valid, err = validate_sql(sql)
            if not valid:
                result["error"] = err
                return result

            df = run_query(sql)
            result["data"] = df
            result["error"] = None
            logger.info(f"Query returned {len(df)} rows")
            result["summary"] = summarise_results(question, df)
            return result

        except Exception as e:
            last_error = str(e)
            logger.warning(f"Attempt {attempt+1} failed: {e}")
            if attempt == max_retries:
                result["error"] = f"Failed after {max_retries+1} attempts: {last_error}"

    return result


EXAMPLE_QUESTIONS = [
    "What is the overall default rate?",
    "Which income type has the highest default rate?",
    "What is the average loan amount for male vs female applicants?",
    "How does education level affect default probability?",
    "Show top 5 occupations by number of applicants",
    "What is the average income for defaulters vs non-defaulters?",
    "How many applicants own a car and also own real estate?",
    "Show default rate by region risk rating",
    "What percentage of applicants have children?",
    "Show average credit amount by contract type",
]

