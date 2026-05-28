"""
reports.py – BASTION
====================
Management report generation and export functions.
Supports Excel (multi-sheet) and Markdown output.
"""

import os
import io
import pandas as pd
from datetime import date, datetime
from calculations import (
    flag_evidence_gaps, flag_overdue_findings,
    flag_expired_exceptions, enrich_findings,
    get_dashboard_metrics
)

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")


def _ensure_exports_dir():
    os.makedirs(EXPORTS_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Management Report Data Builder
# ---------------------------------------------------------------------------
def build_management_report(controls_df, evidence_df, findings_df,
                             remediation_df, exceptions_df) -> dict:
    """
    Compile all data needed for the Management Report page.

    Returns:
        dict with keys:
          - generated_at
          - metrics         (KPI dict)
          - top_findings    (DataFrame – top 5 by severity)
          - evidence_gaps   (DataFrame – gap records)
          - overdue_items   (DataFrame – overdue findings)
          - overdue_rem     (DataFrame – overdue remediation)
          - active_exceptions (DataFrame)
          - control_by_family (DataFrame – pivot)
          - severity_dist   (Series)
          - status_by_framework (DataFrame)
    """
    metrics = get_dashboard_metrics(
        controls_df, evidence_df, findings_df, remediation_df, exceptions_df
    )

    # Enrich findings
    fd = enrich_findings(findings_df)

    # Top 5 findings by severity
    severity_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    fd["sev_rank"] = fd["severity"].map(severity_order).fillna(0)
    top_findings = (
        fd.sort_values("sev_rank", ascending=False)
          .head(5)[["finding_id", "finding_title", "severity", "status",
                     "finding_owner", "due_date", "is_overdue"]]
    )

    # Evidence gaps
    ev = flag_evidence_gaps(evidence_df)
    evidence_gaps = ev[ev["is_gap"]][
        ["evidence_id", "related_control_id", "evidence_name",
         "evidence_status", "evidence_owner", "expiration_date"]
    ]

    # Overdue findings
    overdue_findings = fd[fd["is_overdue"]][
        ["finding_id", "finding_title", "severity", "due_date",
         "status", "finding_owner"]
    ]

    # Overdue remediation
    from calculations import flag_overdue_remediation
    rem = flag_overdue_remediation(remediation_df)
    overdue_rem = rem[rem["is_overdue"]][
        ["remediation_id", "finding_id", "owner", "target_date", "current_status"]
    ]

    # Active exceptions
    exc = flag_expired_exceptions(exceptions_df)
    active_exc = exc[exc["approval_status"].isin(["Approved", "Pending Approval"])][
        ["exception_id", "related_control_id", "exception_reason",
         "approval_status", "expiration_date", "risk_acceptance_owner"]
    ]

    # Control status by family
    if not controls_df.empty:
        control_by_family = (
            controls_df.groupby(["control_family", "implementation_status"])
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )
    else:
        control_by_family = pd.DataFrame()

    # Severity distribution
    severity_dist = findings_df["severity"].value_counts() if not findings_df.empty else pd.Series()

    # Controls by framework
    if not controls_df.empty:
        status_by_framework = (
            controls_df.groupby(["framework", "implementation_status"])
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )
    else:
        status_by_framework = pd.DataFrame()

    return {
        "generated_at":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metrics":            metrics,
        "top_findings":       top_findings,
        "evidence_gaps":      evidence_gaps,
        "overdue_findings":   overdue_findings,
        "overdue_rem":        overdue_rem,
        "active_exceptions":  active_exc,
        "control_by_family":  control_by_family,
        "severity_dist":      severity_dist,
        "status_by_framework": status_by_framework,
    }


# ---------------------------------------------------------------------------
# Excel Export  (6 sheets)
# ---------------------------------------------------------------------------
def export_to_excel(controls_df, evidence_df, findings_df,
                    remediation_df, exceptions_df,
                    report: dict = None) -> str:
    """
    Write a multi-sheet Excel workbook to the exports/ directory.

    Returns:
        Absolute path to the created file.
    """
    _ensure_exports_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"BASTION_Export_{timestamp}.xlsx"
    filepath  = os.path.join(EXPORTS_DIR, filename)

    # Enrich dataframes
    ev  = flag_evidence_gaps(evidence_df)
    fd  = enrich_findings(findings_df)

    # Build dashboard summary sheet
    if report:
        m = report["metrics"]
        summary_data = {
            "Metric": [
                "Total Controls", "Implemented", "Partially Implemented",
                "Not Implemented", "Not Assessed", "Evidence Gaps",
                "Open Findings", "Overdue Remediation Items",
                "Accepted Exceptions", "High/Critical Risk Findings",
            ],
            "Value": [
                m["total_controls"], m["implemented"], m["partially_implemented"],
                m["not_implemented"], m["not_assessed"], m["evidence_gaps"],
                m["open_findings"], m["overdue_remediation"],
                m["accepted_exceptions"], m["high_risk_findings"],
            ],
        }
        summary_df = pd.DataFrame(summary_data)
    else:
        summary_df = pd.DataFrame({"Note": ["Run from Management Report page for full summary."]})

    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        controls_df.to_excel(writer,    sheet_name="Controls",         index=False)
        ev.to_excel(writer,             sheet_name="Evidence",          index=False)
        fd.to_excel(writer,             sheet_name="Findings",          index=False)
        remediation_df.to_excel(writer, sheet_name="Remediation",       index=False)
        exceptions_df.to_excel(writer,  sheet_name="Exceptions",        index=False)
        summary_df.to_excel(writer,     sheet_name="Dashboard Summary", index=False)

    return filepath


def export_to_excel_bytes(controls_df, evidence_df, findings_df,
                          remediation_df, exceptions_df, report: dict = None) -> bytes:
    """Return Excel workbook as bytes (for Streamlit download button)."""
    ev = flag_evidence_gaps(evidence_df)
    fd = enrich_findings(findings_df)

    if report:
        m = report["metrics"]
        summary_df = pd.DataFrame({
            "Metric": [
                "Total Controls", "Implemented", "Partially Implemented",
                "Not Implemented", "Not Assessed", "Evidence Gaps",
                "Open Findings", "Overdue Remediation Items",
                "Accepted Exceptions", "High/Critical Risk Findings",
            ],
            "Value": [
                m["total_controls"], m["implemented"], m["partially_implemented"],
                m["not_implemented"], m["not_assessed"], m["evidence_gaps"],
                m["open_findings"], m["overdue_remediation"],
                m["accepted_exceptions"], m["high_risk_findings"],
            ],
        })
    else:
        summary_df = pd.DataFrame({"Note": ["Run from Management Report page for full summary."]})

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        controls_df.to_excel(writer,    sheet_name="Controls",         index=False)
        ev.to_excel(writer,             sheet_name="Evidence",          index=False)
        fd.to_excel(writer,             sheet_name="Findings",          index=False)
        remediation_df.to_excel(writer, sheet_name="Remediation",       index=False)
        exceptions_df.to_excel(writer,  sheet_name="Exceptions",        index=False)
        summary_df.to_excel(writer,     sheet_name="Dashboard Summary", index=False)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Markdown Report
# ---------------------------------------------------------------------------
def export_to_markdown(report: dict) -> str:
    """
    Generate a Markdown-formatted management report string.
    """
    m   = report["metrics"]
    now = report["generated_at"]

    lines = [
        "# BASTION – Security Control Assessment Report",
        f"**Generated:** {now}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Total Controls Assessed | {m['total_controls']} |",
        f"| Controls Implemented | {m['implemented']} |",
        f"| Partially Implemented | {m['partially_implemented']} |",
        f"| Not Implemented | {m['not_implemented']} |",
        f"| Not Assessed | {m['not_assessed']} |",
        f"| Evidence Gaps | {m['evidence_gaps']} |",
        f"| Open Findings | {m['open_findings']} |",
        f"| Overdue Remediation Items | {m['overdue_remediation']} |",
        f"| Accepted Exceptions | {m['accepted_exceptions']} |",
        f"| High/Critical Findings | {m['high_risk_findings']} |",
        "",
        "---",
        "",
        "## Top 5 High-Risk Findings",
        "",
    ]

    tf = report["top_findings"]
    if not tf.empty:
        lines.append("| ID | Title | Severity | Status | Owner | Due Date | Overdue |")
        lines.append("|---|---|---|---|---|---|---|")
        for _, row in tf.iterrows():
            overdue_flag = "⚠️ YES" if row.get("is_overdue") else "No"
            lines.append(
                f"| {row['finding_id']} | {row['finding_title']} | "
                f"**{row['severity']}** | {row['status']} | "
                f"{row['finding_owner']} | {row['due_date']} | {overdue_flag} |"
            )
    else:
        lines.append("_No findings recorded._")

    lines += [
        "",
        "---",
        "",
        "## Evidence Gaps",
        "",
    ]

    eg = report["evidence_gaps"]
    if not eg.empty:
        lines.append("| Evidence ID | Control | Name | Status | Owner | Expiry |")
        lines.append("|---|---|---|---|---|---|")
        for _, row in eg.iterrows():
            lines.append(
                f"| {row['evidence_id']} | {row['related_control_id']} | "
                f"{row['evidence_name']} | {row['evidence_status']} | "
                f"{row['evidence_owner']} | {row.get('expiration_date','')} |"
            )
    else:
        lines.append("_No evidence gaps._")

    lines += [
        "",
        "---",
        "",
        "## Overdue Remediation Items",
        "",
    ]

    oi = report["overdue_rem"]
    if not oi.empty:
        lines.append("| Remediation ID | Finding | Owner | Target Date | Status |")
        lines.append("|---|---|---|---|---|")
        for _, row in oi.iterrows():
            lines.append(
                f"| {row['remediation_id']} | {row['finding_id']} | "
                f"{row['owner']} | {row['target_date']} | {row['current_status']} |"
            )
    else:
        lines.append("_No overdue remediation items._")

    lines += [
        "",
        "---",
        "",
        "## Active Risk Exceptions",
        "",
    ]

    ae = report["active_exceptions"]
    if not ae.empty:
        lines.append("| Exception ID | Control | Reason | Status | Expiry | Owner |")
        lines.append("|---|---|---|---|---|---|")
        for _, row in ae.iterrows():
            lines.append(
                f"| {row['exception_id']} | {row['related_control_id']} | "
                f"{row['exception_reason'][:60]}... | {row['approval_status']} | "
                f"{row['expiration_date']} | {row['risk_acceptance_owner']} |"
            )
    else:
        lines.append("_No active exceptions._")

    lines += [
        "",
        "---",
        "",
        "## Recommended Next Steps",
        "",
        "1. **Remediate all Critical and High findings within 30 days.**",
        "2. **Collect missing evidence for all flagged gaps before the next audit cycle.**",
        "3. **Conduct the overdue IR tabletop exercise within 60 days.**",
        "4. **Complete the HIPAA annual risk assessment immediately.**",
        "5. **Obtain executed BAAs from all PHI-handling vendors.**",
        "6. **Deploy vulnerability scanning coverage to AWS S3 Data Lake workloads.**",
        "7. **Review and renew all exceptions approaching expiration.**",
        "",
        "_Report generated by BASTION – Security Control Assessment & Evidence Tracker_",
    ]

    return "\n".join(lines)
