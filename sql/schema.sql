-- schema.sql
-- Creates the DuckDB tables used by the talk-to-data module.
-- This is auto-executed by db_builder.py after loading CSVs.

CREATE TABLE IF NOT EXISTS applications (
    SK_ID_CURR          INTEGER PRIMARY KEY,
    TARGET              INTEGER,           -- 1 = defaulted, 0 = repaid
    NAME_CONTRACT_TYPE  VARCHAR,
    CODE_GENDER         VARCHAR,
    FLAG_OWN_CAR        VARCHAR,
    FLAG_OWN_REALTY     VARCHAR,
    CNT_CHILDREN        INTEGER,
    AMT_INCOME_TOTAL    DOUBLE,
    AMT_CREDIT          DOUBLE,
    AMT_ANNUITY         DOUBLE,
    AMT_GOODS_PRICE     DOUBLE,
    NAME_INCOME_TYPE    VARCHAR,
    NAME_EDUCATION_TYPE VARCHAR,
    NAME_FAMILY_STATUS  VARCHAR,
    NAME_HOUSING_TYPE   VARCHAR,
    DAYS_BIRTH          INTEGER,
    DAYS_EMPLOYED       INTEGER,
    OCCUPATION_TYPE     VARCHAR,
    CNT_FAM_MEMBERS     DOUBLE,
    REGION_RATING_CLIENT INTEGER
);

CREATE TABLE IF NOT EXISTS bureau_summary (
    SK_ID_CURR          INTEGER PRIMARY KEY,
    bureau_loan_count   INTEGER,
    bureau_active_loans INTEGER,
    bureau_closed_loans INTEGER,
    bureau_avg_days_credit DOUBLE,
    bureau_total_debt   DOUBLE,
    bureau_total_credit DOUBLE
);
