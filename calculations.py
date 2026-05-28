"""
calculations.py – BASTION
=========================
Automated risk scoring, gap flagging, overdue detection, and severity suggestions.
All functions accept pandas DataFrames and return modified copies.
"""

import pandas as pd
from datetime import date


# ---------------------------------------------------------------------------
# Risk score matrix  (Likelihood 1-5 × Impact 1-5)
# ---------------------------------------------------------------------------
RISK_LABELS = {
    (1, 1): "Low",  (1, 2): "Low",  (1, 3): "Low",    (1, 4): "Medium", (1, 5): "Medium",
    (2, 1): "Low",  (2, 2): "Low",  (2, 3): "Medium",  (2, 4): "Medium", (2, 5): "High",
    (3, 1): "Low",  (3, 2): "Medium",(3, 3): "Medium", (3, 4): "High",   (3, 5): "High",
    (4, 1): "Medium",(4,2): "Medium",(4,3): "High",    (4, 4): "High",   (4, 5): "Critical",
    (5, 1): "Medium",(5,2): "High", (5, 3): "High",    (5, 4): "Critical",(5,5): "Critical",
}

SEVERITY_ORDER = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "": 0}


def calculate_risk_score(likelihood: int, impact: int) -> str:
    """
    Return a risk label (Critical/High/Medium/Low) based on a 5×5 matrix.

    Args:
        likelihood: 1 (rare) – 5 (almost certain)
        impact:     1 (negligible) – 5 (catastrophic)

    Returns:
        Risk label string
    """
    try:
        l = max(1, min(5, int(likelihood)))
        i = max(1, min(5, int(impact)))
        return RISK_LABELS.get((l, i), "Medium")
    except (TypeError, ValueError):
        return "Unknown"


def flag_evidence_gaps(evidence_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a boolean column 'is_gap' to evidence DataFrame.
    An evidence gap is status = Missing, Incomplete, or Outdated.
    """
    df = evidence_df.copy()
    gap_statuses = {"Missing", "Incomplete", "Outdated"}
    df["is_gap"] = df["evidence_status"].apply(
        lambda s: s in gap_statuses if isinstance(s, str) else False
    )
    return df


def flag_overdue_findings(findings_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add boolean column 'is_overdue' to findings DataFrame.
    A finding is overdue if its due_date is in the past and status is not Closed/Remediated.
    """
    df = findings_df.copy()
    closed_statuses = {"Closed", "Remediated", "Risk Accepted"}
    today = date.today().isoformat()

    def _overdue(row):
        if not row.get("due_date"):
            return False
        if row.get("status", "") in closed_statuses:
            return False
        return str(row["due_date"]) < today

    df["is_overdue"] = df.apply(_overdue, axis=1)
    return df


def flag_overdue_remediation(remediation_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add boolean column 'is_overdue' to remediation DataFrame.
    Overdue if target_date is past and current_status is not Closed.
    """
    df = remediation_df.copy()
    today = date.today().isoformat()

    def _overdue(row):
        if not row.get("target_date"):
            return False
        if str(row.get("current_status", "")).lower() == "closed":
            return False
        return str(row["target_date"]) < today

    df["is_overdue"] = df.apply(_overdue, axis=1)
    return df


def flag_expired_exceptions(exceptions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add boolean column 'is_expired' to exceptions DataFrame.
    Expired if expiration_date is in the past AND approval_status is not Expired/Rejected/Draft.
    Also update approval_status to 'Expired' for display purposes.
    """
    df = exceptions_df.copy()
    today = date.today().isoformat()
    non_active = {"Expired", "Rejected", "Draft"}

    def _expired(row):
        if not row.get("expiration_date"):
            return False
        if row.get("approval_status", "") in non_active:
            return False
        return str(row["expiration_date"]) < today

    df["is_expired"] = df.apply(_expired, axis=1)
    # Auto-mark expired status for display
    df.loc[df["is_expired"], "approval_status"] = "Expired"
    return df


def suggest_severity(implementation_status: str, data_type: str) -> str:
    """
    Suggest a severity level based on implementation status and data type.
    High-sensitivity data types (PHI, Cardholder Data) with unimplemented controls
    get elevated severity suggestions.

    Returns:
        Suggested severity string
    """
    high_sensitivity = {"PHI", "Cardholder Data"}
    if implementation_status == "Not Implemented" and data_type in high_sensitivity:
        return "Critical"
    if implementation_status == "Not Implemented":
        return "High"
    if implementation_status == "Partially Implemented" and data_type in high_sensitivity:
        return "High"
    if implementation_status == "Partially Implemented":
        return "Medium"
    return "Low"


def enrich_findings(findings_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 'is_overdue' and 'risk_score' columns to a findings DataFrame.
    Recalculates risk score from likelihood and impact columns.
    """
    df = flag_overdue_findings(findings_df)
    df["risk_score"] = df.apply(
        lambda r: calculate_risk_score(r.get("likelihood", 3), r.get("impact", 3)),
        axis=1
    )
    return df


def get_dashboard_metrics(controls_df, evidence_df, findings_df, remediation_df, exceptions_df):
    """
    Compute all KPI numbers for the Dashboard page.

    Returns:
        dict of metric_name -> value
    """
    today = date.today().isoformat()

    # --- Controls ---
    total_controls         = len(controls_df)
    implemented            = (controls_df["implementation_status"] == "Implemented").sum()
    partially              = (controls_df["implementation_status"] == "Partially Implemented").sum()
    not_implemented        = (controls_df["implementation_status"] == "Not Implemented").sum()
    not_assessed           = (controls_df["implementation_status"] == "Not Assessed").sum()

    # --- Evidence ---
    ev = flag_evidence_gaps(evidence_df)
    evidence_gaps          = ev["is_gap"].sum()

    # --- Findings ---
    fd = flag_overdue_findings(findings_df)
    open_findings          = findings_df["status"].isin(["Open", "In Progress", "Pending Evidence"]).sum()
    overdue_remediations   = fd["is_overdue"].sum()
    high_risk              = findings_df["severity"].isin(["Critical", "High"]).sum()

    # --- Remediation ---
    rem = flag_overdue_remediation(remediation_df)
    open_remediation       = remediation_df["current_status"].isin(["Open", "In Progress"]).sum()
    overdue_rem_items      = rem["is_overdue"].sum()

    # --- Exceptions ---
    exc = flag_expired_exceptions(exceptions_df)
    accepted_exceptions    = exceptions_df["approval_status"].isin(["Approved", "Pending Approval"]).sum()

    return {
        "total_controls":         int(total_controls),
        "implemented":            int(implemented),
        "partially_implemented":  int(partially),
        "not_implemented":        int(not_implemented),
        "not_assessed":           int(not_assessed),
        "evidence_gaps":          int(evidence_gaps),
        "open_findings":          int(open_findings),
        "overdue_remediation":    int(overdue_rem_items),
        "accepted_exceptions":    int(accepted_exceptions),
        "high_risk_findings":     int(high_risk),
    }
