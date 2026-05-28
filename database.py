"""
database.py – BASTION
====================
SQLite schema creation and all CRUD operations.
Uses the stdlib sqlite3 module (no extra dependencies needed).
"""

import sqlite3
import os
import pandas as pd
from datetime import date

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH  = os.path.join(DATA_DIR, "bastion.db")

def _get_conn():
    """Return a sqlite3 connection with Row factory enabled."""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Schema creation
# ---------------------------------------------------------------------------
CREATE_CONTROLS = """
CREATE TABLE IF NOT EXISTS controls (
    control_id          TEXT PRIMARY KEY,
    framework           TEXT,
    control_family      TEXT,
    control_title       TEXT,
    control_description TEXT,
    requirement_summary TEXT,
    control_owner       TEXT,
    system_application  TEXT,
    data_type           TEXT,
    implementation_status TEXT,
    evidence_required   TEXT,
    evidence_available  TEXT,
    evidence_source     TEXT,
    evidence_link       TEXT,
    last_reviewed_date  TEXT,
    next_review_date    TEXT,
    assessor_notes      TEXT
);
"""

CREATE_EVIDENCE = """
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id         TEXT PRIMARY KEY,
    related_control_id  TEXT,
    evidence_name       TEXT,
    evidence_type       TEXT,
    evidence_description TEXT,
    evidence_owner      TEXT,
    evidence_source     TEXT,
    collection_method   TEXT,
    evidence_status     TEXT,
    date_collected      TEXT,
    expiration_date     TEXT,
    review_notes        TEXT
);
"""

CREATE_FINDINGS = """
CREATE TABLE IF NOT EXISTS findings (
    finding_id          TEXT PRIMARY KEY,
    related_control_id  TEXT,
    finding_title       TEXT,
    finding_description TEXT,
    risk_theme          TEXT,
    severity            TEXT,
    likelihood          INTEGER,
    impact              INTEGER,
    inherent_risk       TEXT,
    existing_controls   TEXT,
    residual_risk       TEXT,
    business_impact     TEXT,
    compliance_impact   TEXT,
    recommended_action  TEXT,
    finding_owner       TEXT,
    due_date            TEXT,
    status              TEXT,
    closure_evidence    TEXT,
    closure_notes       TEXT
);
"""

CREATE_REMEDIATION = """
CREATE TABLE IF NOT EXISTS remediation (
    remediation_id      TEXT PRIMARY KEY,
    finding_id          TEXT,
    owner               TEXT,
    action_plan         TEXT,
    target_date         TEXT,
    current_status      TEXT,
    progress_notes      TEXT,
    dependency          TEXT,
    validation_required TEXT,
    closure_evidence    TEXT,
    date_closed         TEXT
);
"""

CREATE_EXCEPTIONS = """
CREATE TABLE IF NOT EXISTS exceptions (
    exception_id            TEXT PRIMARY KEY,
    related_control_id      TEXT,
    related_finding_id      TEXT,
    exception_reason        TEXT,
    business_justification  TEXT,
    compensating_controls   TEXT,
    risk_acceptance_owner   TEXT,
    approval_status         TEXT,
    expiration_date         TEXT,
    review_date             TEXT,
    notes                   TEXT
);
"""


def init_db():
    """Create all tables if they don't already exist."""
    conn = _get_conn()
    c = conn.cursor()
    for sql in [CREATE_CONTROLS, CREATE_EVIDENCE, CREATE_FINDINGS,
                CREATE_REMEDIATION, CREATE_EXCEPTIONS]:
        c.execute(sql)
    conn.commit()
    conn.close()


def is_seeded():
    """Return True if the controls table already has rows."""
    conn = _get_conn()
    count = conn.execute("SELECT COUNT(*) FROM controls").fetchone()[0]
    conn.close()
    return count > 0


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------
def _table_to_df(table: str) -> pd.DataFrame:
    conn = _get_conn()
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    return df


def _upsert(table: str, pk_col: str, row: dict):
    """Insert or replace a row (dict) into a table."""
    conn = _get_conn()
    cols = ", ".join(row.keys())
    placeholders = ", ".join(["?"] * len(row))
    sql = f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({placeholders})"
    conn.execute(sql, list(row.values()))
    conn.commit()
    conn.close()


def _delete_row(table: str, pk_col: str, pk_val: str):
    conn = _get_conn()
    conn.execute(f"DELETE FROM {table} WHERE {pk_col} = ?", (pk_val,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------
def get_all_controls() -> pd.DataFrame:
    return _table_to_df("controls")

def upsert_control(row: dict):
    _upsert("controls", "control_id", row)

def delete_control(control_id: str):
    _delete_row("controls", "control_id", control_id)


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------
def get_all_evidence() -> pd.DataFrame:
    return _table_to_df("evidence")

def upsert_evidence(row: dict):
    _upsert("evidence", "evidence_id", row)

def delete_evidence(evidence_id: str):
    _delete_row("evidence", "evidence_id", evidence_id)


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------
def get_all_findings() -> pd.DataFrame:
    return _table_to_df("findings")

def upsert_finding(row: dict):
    _upsert("findings", "finding_id", row)

def delete_finding(finding_id: str):
    _delete_row("findings", "finding_id", finding_id)


# ---------------------------------------------------------------------------
# Remediation
# ---------------------------------------------------------------------------
def get_all_remediation() -> pd.DataFrame:
    return _table_to_df("remediation")

def upsert_remediation(row: dict):
    _upsert("remediation", "remediation_id", row)

def delete_remediation(remediation_id: str):
    _delete_row("remediation", "remediation_id", remediation_id)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------
def get_all_exceptions() -> pd.DataFrame:
    return _table_to_df("exceptions")

def upsert_exception(row: dict):
    _upsert("exceptions", "exception_id", row)

def delete_exception(exception_id: str):
    _delete_row("exceptions", "exception_id", exception_id)


# ---------------------------------------------------------------------------
# Bulk insert (used by seed_data and CSV import)
# ---------------------------------------------------------------------------
def bulk_insert_df(table: str, df: pd.DataFrame, if_exists: str = "append"):
    """Write a DataFrame to the given table using pandas."""
    conn = _get_conn()
    df.to_sql(table, conn, if_exists=if_exists, index=False)
    conn.commit()
    conn.close()
