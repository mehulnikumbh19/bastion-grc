"""
app.py – BASTION
================
BASTION – Security Control Assessment & Evidence Tracker
Main Streamlit application with 8-page sidebar navigation.

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
import uuid

# Local modules
import database as db
import calculations as calc
import reports as rep
from seed_data import load_seed_data

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="BASTION – Security Control Assessment",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS – professional dark GRC aesthetic
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Dark sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
    }
    [data-testid="stSidebar"] * {
        color: #c9d1d9 !important;
    }

    /* KPI metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1c2128 0%, #22272e 100%);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 18px 20px;
        text-align: center;
        margin: 4px;
        transition: border-color 0.2s;
    }
    .metric-card:hover { border-color: #58a6ff; }
    .metric-label {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #8b949e;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #f0f6fc;
        line-height: 1;
    }
    .metric-value.red   { color: #f85149; }
    .metric-value.amber { color: #d29922; }
    .metric-value.green { color: #3fb950; }
    .metric-value.blue  { color: #58a6ff; }

    /* Section header */
    .section-header {
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #58a6ff;
        border-bottom: 1px solid #30363d;
        padding-bottom: 6px;
        margin: 24px 0 16px;
    }

    /* Badge pills */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-critical { background: #4d1f1f; color: #f85149; }
    .badge-high     { background: #3d2b1a; color: #d29922; }
    .badge-medium   { background: #1f2d3d; color: #58a6ff; }
    .badge-low      { background: #1a2e22; color: #3fb950; }

    /* App title banner */
    .app-banner {
        background: linear-gradient(90deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px 28px;
        margin-bottom: 24px;
    }
    .app-title {
        font-size: 26px;
        font-weight: 800;
        color: #f0f6fc;
        letter-spacing: -0.5px;
    }
    .app-subtitle {
        font-size: 13px;
        color: #8b949e;
        margin-top: 4px;
    }

    /* Streamlit overrides */
    .stDataFrame { border-radius: 8px; }
    div[data-testid="stForm"] { border: 1px solid #30363d; border-radius: 8px; padding: 16px; }
    .stExpander { border: 1px solid #30363d !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Boot-time initialization
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def initialize():
    db.init_db()
    load_seed_data()

initialize()


# ---------------------------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------------------------
PAGES = [
    "📊  Dashboard",
    "📋  Control Library",
    "🛡️  Common Controls (CCF)",
    "🔎  Assessor Review Center",
    "🗂️  Evidence Tracker",
    "🔍  Gap & Finding Tracker",
    "🔧  Remediation Tracker",
    "⚠️  Exception Tracker",
    "📥  Import / Export",
    "📄  Management Report",
]

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 20px;'>
        <div style='font-size:28px;'>🛡️</div>
        <div style='font-size:16px; font-weight:800; color:#f0f6fc; letter-spacing:1px;'>BASTION</div>
        <div style='font-size:10px; color:#8b949e; letter-spacing:2px;'>GRC CONTROL TRACKER</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("Navigation", PAGES, label_visibility="collapsed")

    st.markdown("---")
    st.markdown(
        "<div style='font-size:11px; color:#8b949e; text-align:center;'>"
        "Security Control Assessment<br>& Evidence Tracker<br><br>"
        "v1.0.0 · Built with Python & Streamlit"
        "</div>",
        unsafe_allow_html=True
    )


# ---------------------------------------------------------------------------
# Helper: load all data fresh from DB
# ---------------------------------------------------------------------------
def load_all():
    return (
        db.get_all_controls(),
        db.get_all_evidence(),
        db.get_all_findings(),
        db.get_all_remediation(),
        db.get_all_exceptions(),
    )


# ---------------------------------------------------------------------------
# Helper: KPI card HTML
# ---------------------------------------------------------------------------
def kpi_card(label: str, value, color: str = "") -> str:
    cls = f"metric-value {color}" if color else "metric-value"
    return (
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="{cls}">{value}</div>'
        f'</div>'
    )


# ===========================================================================
# PAGE: Dashboard
# ===========================================================================
def page_dashboard():
    controls_df, evidence_df, findings_df, remediation_df, exceptions_df = load_all()

    st.markdown("""
    <div class="app-banner">
        <div class="app-title">🛡️ BASTION</div>
        <div class="app-subtitle">Security Control Assessment & Evidence Tracker — Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    metrics = calc.get_dashboard_metrics(
        controls_df, evidence_df, findings_df, remediation_df, exceptions_df
    )
    m = metrics

    # --- Row 1: Control Status ---
    st.markdown('<div class="section-header">Control Implementation Status</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    with cols[0]:
        st.markdown(kpi_card("Total Controls", m["total_controls"], "blue"), unsafe_allow_html=True)
    with cols[1]:
        st.markdown(kpi_card("Implemented", m["implemented"], "green"), unsafe_allow_html=True)
    with cols[2]:
        st.markdown(kpi_card("Partially Implemented", m["partially_implemented"], "amber"), unsafe_allow_html=True)
    with cols[3]:
        st.markdown(kpi_card("Not Implemented", m["not_implemented"], "red"), unsafe_allow_html=True)
    with cols[4]:
        st.markdown(kpi_card("Not Assessed", m["not_assessed"]), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Row 2: Risk & Compliance ---
    st.markdown('<div class="section-header">Risk & Compliance Posture</div>', unsafe_allow_html=True)
    cols2 = st.columns(5)
    with cols2[0]:
        st.markdown(kpi_card("Evidence Gaps", m["evidence_gaps"], "red"), unsafe_allow_html=True)
    with cols2[1]:
        st.markdown(kpi_card("Open Findings", m["open_findings"], "amber"), unsafe_allow_html=True)
    with cols2[2]:
        st.markdown(kpi_card("Overdue Items", m["overdue_remediation"], "red"), unsafe_allow_html=True)
    with cols2[3]:
        st.markdown(kpi_card("Active Exceptions", m["accepted_exceptions"], "amber"), unsafe_allow_html=True)
    with cols2[4]:
        st.markdown(kpi_card("High/Critical Findings", m["high_risk_findings"], "red"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Charts Row ---
    st.markdown('<div class="section-header">Visual Analytics</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    # Chart 1: Control status by family
    with c1:
        if not controls_df.empty:
            fam_data = (
                controls_df.groupby(["control_family", "implementation_status"])
                .size()
                .reset_index(name="count")
            )
            color_map = {
                "Implemented":           "#3fb950",
                "Partially Implemented": "#d29922",
                "Not Implemented":       "#f85149",
                "Not Assessed":          "#8b949e",
                "Not Applicable":        "#484f58",
            }
            fig1 = px.bar(
                fam_data,
                x="count",
                y="control_family",
                color="implementation_status",
                color_discrete_map=color_map,
                orientation="h",
                title="Controls by Family & Status",
                labels={"control_family": "", "count": "Controls", "implementation_status": "Status"},
                template="plotly_dark",
            )
            fig1.update_layout(
                paper_bgcolor="#1c2128",
                plot_bgcolor="#1c2128",
                legend=dict(font=dict(size=9)),
                margin=dict(l=10, r=10, t=40, b=10),
                height=340,
            )
            st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Severity distribution
    with c2:
        if not findings_df.empty:
            sev_counts = findings_df["severity"].value_counts().reset_index()
            sev_counts.columns = ["severity", "count"]
            sev_color = {
                "Critical": "#f85149",
                "High":     "#d29922",
                "Medium":   "#58a6ff",
                "Low":      "#3fb950",
            }
            fig2 = px.pie(
                sev_counts,
                names="severity",
                values="count",
                color="severity",
                color_discrete_map=sev_color,
                title="Findings by Severity",
                template="plotly_dark",
                hole=0.45,
            )
            fig2.update_layout(
                paper_bgcolor="#1c2128",
                plot_bgcolor="#1c2128",
                margin=dict(l=10, r=10, t=40, b=10),
                height=340,
            )
            st.plotly_chart(fig2, use_container_width=True)

    # Chart 3: Finding status distribution
    with c3:
        if not findings_df.empty:
            status_counts = findings_df["status"].value_counts().reset_index()
            status_counts.columns = ["status", "count"]
            status_color = {
                "Open":             "#f85149",
                "In Progress":      "#d29922",
                "Pending Evidence": "#58a6ff",
                "Risk Accepted":    "#a371f7",
                "Remediated":       "#3fb950",
                "Closed":           "#484f58",
            }
            fig3 = px.bar(
                status_counts,
                x="status",
                y="count",
                color="status",
                color_discrete_map=status_color,
                title="Findings by Remediation Status",
                labels={"status": "", "count": "Count"},
                template="plotly_dark",
            )
            fig3.update_layout(
                paper_bgcolor="#1c2128",
                plot_bgcolor="#1c2128",
                showlegend=False,
                margin=dict(l=10, r=10, t=40, b=10),
                height=340,
            )
            st.plotly_chart(fig3, use_container_width=True)

    # --- Framework Compliance Scores ---
    st.markdown('<div class="section-header">Framework Compliance Index</div>', unsafe_allow_html=True)
    fw_comp = calc.calculate_framework_compliance(controls_df)
    if not fw_comp.empty:
        fig_fw = px.bar(
            fw_comp,
            x="Score",
            y="Framework",
            orientation="h",
            text="Score",
            title="Compliance Score by Framework (%)",
            labels={"Score": "Compliance Score (%)", "Framework": ""},
            template="plotly_dark",
            color="Score",
            color_continuous_scale="RdYlGn",
        )
        fig_fw.update_layout(
            paper_bgcolor="#1c2128",
            plot_bgcolor="#1c2128",
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=40, b=10),
            height=280,
        )
        fig_fw.update_traces(texttemplate='%{text}%', textposition='outside')
        st.plotly_chart(fig_fw, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Recent high-risk findings table ---
    st.markdown('<div class="section-header">High & Critical Findings</div>', unsafe_allow_html=True)
    if not findings_df.empty:
        high = findings_df[findings_df["severity"].isin(["Critical", "High"])][
            ["finding_id", "finding_title", "severity", "status",
             "finding_owner", "due_date"]
        ].sort_values("severity")
        st.dataframe(high, use_container_width=True, hide_index=True)
    else:
        st.info("No findings recorded yet.")


# ===========================================================================
# PAGE: Control Library
# ===========================================================================
def page_control_library():
    st.markdown("## 📋 Control Library")
    controls_df = db.get_all_controls()

    # --- Filters ---
    with st.expander("🔍 Filter & Search", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            frameworks = ["All"] + sorted(controls_df["framework"].dropna().unique().tolist())
            sel_fw = st.selectbox("Framework", frameworks)
        with col2:
            families = ["All"] + sorted(controls_df["control_family"].dropna().unique().tolist())
            sel_fam = st.selectbox("Control Family", families)
        with col3:
            statuses = ["All"] + sorted(controls_df["implementation_status"].dropna().unique().tolist())
            sel_stat = st.selectbox("Implementation Status", statuses)
        with col4:
            search = st.text_input("Search (ID / Title / Owner)")

    filtered = controls_df.copy()
    if sel_fw   != "All": filtered = filtered[filtered["framework"]             == sel_fw]
    if sel_fam  != "All": filtered = filtered[filtered["control_family"]        == sel_fam]
    if sel_stat != "All": filtered = filtered[filtered["implementation_status"] == sel_stat]
    if search:
        mask = (
            filtered["control_id"].str.contains(search, case=False, na=False) |
            filtered["control_title"].str.contains(search, case=False, na=False) |
            filtered["control_owner"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]

    st.caption(f"Showing **{len(filtered)}** of **{len(controls_df)}** controls")
    display_cols = [
        "control_id", "framework", "control_family", "control_title",
        "control_owner", "system_application", "implementation_status",
        "evidence_available", "last_reviewed_date", "next_review_date",
    ]
    st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

    # --- Add / Edit Form ---
    st.markdown("---")
    with st.expander("➕ Add or Edit a Control"):
        FRAMEWORKS = ["NIST SP 800-53", "CIS Controls", "ISO 27001",
                      "SOC 2", "HIPAA", "HITRUST", "PCI DSS"]
        FAMILIES   = ["Access Control", "Audit and Logging", "Encryption and Data Protection",
                      "Incident Response", "Risk Assessment", "Configuration Management",
                      "Vendor Risk", "Change Management", "Vulnerability Management",
                      "Security Awareness"]
        IMPL_STATI = ["Implemented", "Partially Implemented", "Not Implemented",
                      "Not Assessed", "Not Applicable"]
        DATA_TYPES = ["PII", "PHI", "Cardholder Data", "Internal Confidential",
                      "Authentication Logs", "Security Event Logs"]

        # Pre-fill from existing if control_id entered
        prefill_id = st.text_input("Existing Control ID to edit (leave blank to create new)")
        existing   = {}
        if prefill_id and not controls_df.empty:
            rows = controls_df[controls_df["control_id"] == prefill_id]
            if not rows.empty:
                existing = rows.iloc[0].to_dict()
                st.success(f"Loaded existing control: {prefill_id}")

        def _g(field, default=""):
            return existing.get(field, default) or default

        with st.form("control_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                cid   = st.text_input("Control ID *", value=_g("control_id") or f"CTL-{str(uuid.uuid4())[:8].upper()}")
                fw    = st.selectbox("Framework *", FRAMEWORKS, index=FRAMEWORKS.index(_g("framework", FRAMEWORKS[0])) if _g("framework") in FRAMEWORKS else 0)
                fam   = st.selectbox("Control Family *", FAMILIES, index=FAMILIES.index(_g("control_family", FAMILIES[0])) if _g("control_family") in FAMILIES else 0)
            with c2:
                title = st.text_input("Control Title *", value=_g("control_title"))
                owner = st.text_input("Control Owner", value=_g("control_owner"))
                sys   = st.text_input("System / Application", value=_g("system_application"))
            with c3:
                dtype = st.selectbox("Data Type", DATA_TYPES, index=DATA_TYPES.index(_g("data_type", DATA_TYPES[0])) if _g("data_type") in DATA_TYPES else 0)
                impl  = st.selectbox("Implementation Status *", IMPL_STATI, index=IMPL_STATI.index(_g("implementation_status", IMPL_STATI[0])) if _g("implementation_status") in IMPL_STATI else 0)
                ev_av = st.selectbox("Evidence Available", ["Yes", "No", "Partial", "N/A"],
                                     index=["Yes","No","Partial","N/A"].index(_g("evidence_available","No")) if _g("evidence_available") in ["Yes","No","Partial","N/A"] else 0)

            desc    = st.text_area("Control Description",    value=_g("control_description"))
            req_sum = st.text_area("Requirement Summary",    value=_g("requirement_summary"))
            ev_req  = st.text_area("Evidence Required",      value=_g("evidence_required"))
            ev_src  = st.text_input("Evidence Source",       value=_g("evidence_source"))
            ev_link = st.text_input("Evidence Link / Path",  value=_g("evidence_link"))
            notes   = st.text_area("Assessor Notes",         value=_g("assessor_notes"))

            c4, c5 = st.columns(2)
            with c4:
                last_rev = st.date_input("Last Reviewed Date",
                                         value=datetime.strptime(_g("last_reviewed_date", date.today().isoformat()), "%Y-%m-%d").date()
                                         if _g("last_reviewed_date") else date.today())
            with c5:
                next_rev = st.date_input("Next Review Date",
                                         value=datetime.strptime(_g("next_review_date", date.today().isoformat()), "%Y-%m-%d").date()
                                         if _g("next_review_date") else date.today())

            submitted = st.form_submit_button("💾 Save Control", type="primary")
            if submitted:
                if not cid or not title:
                    st.error("Control ID and Title are required.")
                else:
                    row = {
                        "control_id": cid, "framework": fw, "control_family": fam,
                        "control_title": title, "control_description": desc,
                        "requirement_summary": req_sum, "control_owner": owner,
                        "system_application": sys, "data_type": dtype,
                        "implementation_status": impl, "evidence_required": ev_req,
                        "evidence_available": ev_av, "evidence_source": ev_src,
                        "evidence_link": ev_link,
                        "last_reviewed_date": str(last_rev),
                        "next_review_date":   str(next_rev),
                        "assessor_notes": notes,
                    }
                    db.upsert_control(row)
                    st.success(f"✅ Control **{cid}** saved.")
                    st.rerun()

    # --- Delete ---
    with st.expander("🗑️ Delete a Control"):
        del_id = st.selectbox("Select Control to Delete", [""] + controls_df["control_id"].tolist())
        if st.button("Delete Selected Control", type="secondary") and del_id:
            st.warning(f"Deleted control {del_id}")
            st.rerun()


# ===========================================================================
# PAGE: Common Control Framework (CCF) Matrix
# ===========================================================================
def page_ccf():
    st.markdown("## 🛡️ Common Control Framework (CCF) Mapping")
    st.write(
        "A **Common Control Framework (CCF)** maps a single internal, company-defined control "
        "to multiple external regulatory frameworks (NIST SP 800-53, CIS Controls, ISO 27001, SOC 2, HIPAA, PCI DSS, HITRUST). "
        "This minimizes duplicate compliance tasks and prevents audit fatigue by auditing once and satisfying many."
    )

    controls_df = db.get_all_controls()
    ccf_df = calc.get_ccf_mappings(controls_df)

    # Summary metric of CCF health
    total_cc = len(ccf_df)
    implemented_cc = (ccf_df["Implementation Status"] == "Implemented").sum()
    partial_cc = (ccf_df["Implementation Status"] == "Partially Implemented").sum()
    gap_cc = (ccf_df["Implementation Status"] == "Gap").sum()

    st.markdown('<div class="section-header">CCF Posture Overview</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("Total Common Controls", total_cc, "blue"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Fully Compliant (All Mapped)", implemented_cc, "green"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Partially Compliant", partial_cc, "amber"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Critical Gaps (No Mapped)", gap_cc, "red"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Common Control Mapping Details</div>', unsafe_allow_html=True)
    
    # Custom colored status display
    for _, row in ccf_df.iterrows():
        color_map = {
            "Implemented": "badge-low",
            "Partially Implemented": "badge-high",
            "Gap": "badge-critical"
        }
        badge_cls = color_map.get(row["Implementation Status"], "badge-medium")
        
        status_html = f'<span class="badge {badge_cls}">{row["Implementation Status"]}</span>'
        
        with st.expander(f"🔑 **{row['Common Control ID']}** — {row['Common Control Title']}  |  ({row['Implementation Status']})", expanded=True if row["Implementation Status"] == "Gap" else False):
            st.markdown(f"**Description:** {row['Description']}")
            st.markdown(f"**Mapped Regulatory Controls:** `{row['Mapped Framework Controls']}`")
            
            # Show details of mapped controls
            mapped_ids = [cid.strip() for cid in row["Mapped Framework Controls"].split(",")]
            mapped_details = controls_df[controls_df["control_id"].isin(mapped_ids)][
                ["control_id", "framework", "control_title", "implementation_status", "control_owner"]
            ]
            st.dataframe(mapped_details, use_container_width=True, hide_index=True)


# ===========================================================================
# PAGE: Assessor Review Center
# ===========================================================================
def page_assessor_review_center():
    st.markdown("## 🔎 Assessor Control & Evidence Review Center")
    st.write(
        "A unified assessor interface designed for speed and productivity. Review a control's details "
        "and its associated evidence side-by-side. Perform audits, approve evidence, and log "
        "findings or risk exceptions without leaving this page."
    )

    controls_df, evidence_df, findings_df, remediation_df, exceptions_df = load_all()

    col_ctrl, col_detail = st.columns([1, 2])

    with col_ctrl:
        st.markdown("### 📋 Select Control to Audit")
        sel_fw = st.selectbox("Filter by Framework", ["All"] + sorted(controls_df["framework"].dropna().unique().tolist()))
        
        filtered_ctrls = controls_df.copy()
        if sel_fw != "All":
            filtered_ctrls = filtered_ctrls[filtered_ctrls["framework"] == sel_fw]
            
        ctrl_list = filtered_ctrls["control_id"].tolist()
        if not ctrl_list:
            st.warning("No controls found for this framework.")
            return
            
        selected_cid = st.radio("Controls", ctrl_list, label_visibility="collapsed")

    with col_detail:
        if selected_cid:
            row = controls_df[controls_df["control_id"] == selected_cid].iloc[0]
            st.markdown(f"### 🛡️ Auditing: **{row['control_id']}** — {row['control_title']}")
            
            t1, t2, t3 = st.tabs(["📋 Control Details & Evidence", "📝 Perform Audit Action", "📁 Audit Trail (Linked Items)"])
            
            with t1:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Framework:** {row['framework']}")
                    st.markdown(f"**Family:** {row['control_family']}")
                    st.markdown(f"**Owner:** {row['control_owner']}")
                    st.markdown(f"**System/App:** {row['system_application']}")
                    st.markdown(f"**Data Sensitivity:** `{row['data_type']}`")
                with col_b:
                    st.markdown(f"**Implementation Status:** `{row['implementation_status']}`")
                    st.markdown(f"**Evidence Required:** {row['evidence_required']}")
                    st.markdown(f"**Assessor Notes:** *{row['assessor_notes'] or 'None'}*")

                st.markdown("#### 📂 Associated Evidence Logs")
                linked_ev = evidence_df[evidence_df["related_control_id"] == selected_cid]
                if not linked_ev.empty:
                    st.dataframe(linked_ev[["evidence_id", "evidence_name", "evidence_type", "evidence_status", "expiration_date"]], 
                                 use_container_width=True, hide_index=True)
                else:
                    st.error("⚠️ No evidence has been uploaded for this control.")

            with t2:
                st.markdown("#### ⚡ Quick Actions")
                action = st.selectbox("Action type", ["Approve/Update Evidence Status", "Log Audit Finding", "Request Risk Exception"])
                
                if action == "Approve/Update Evidence Status":
                    if not linked_ev.empty:
                        ev_to_update = st.selectbox("Select Evidence to Update", linked_ev["evidence_id"].tolist())
                        new_ev_status = st.selectbox("New Evidence Status", ["Available", "Incomplete", "Outdated", "Missing", "Approved"])
                        ev_rev_notes = st.text_area("Review Notes / Assessment comments")
                        
                        if st.button("💾 Update Evidence Status", type="primary"):
                            ev_row = evidence_df[evidence_df["evidence_id"] == ev_to_update].iloc[0].to_dict()
                            ev_row["evidence_status"] = new_ev_status
                            ev_row["review_notes"] = ev_rev_notes
                            db.upsert_evidence(ev_row)
                            st.success(f"Evidence {ev_to_update} updated successfully!")
                            st.rerun()
                    else:
                        st.info("No evidence uploaded for this control. You can add one under the Evidence Tracker.")
                        
                elif action == "Log Audit Finding":
                    with st.form("quick_finding_form"):
                        st.markdown("##### 🚨 Log a Control Deficiency / Gap")
                        f_title = st.text_input("Finding Title *", value=f"Deficiency in {selected_cid}: {row['control_title']}")
                        f_sev = st.selectbox("Severity", ["Critical", "High", "Medium", "Low"])
                        f_desc = st.text_area("Description / Assessors Proof of Concept")
                        f_rec = st.text_area("Recommended Action", value=f"Implement and enforce {selected_cid} controls.")
                        f_owner = st.text_input("Finding Owner", value=row["control_owner"])
                        f_due = st.date_input("Due Date")
                        
                        if st.form_submit_button("🚨 Raise Finding"):
                            fid = f"FND-{str(uuid.uuid4())[:6].upper()}"
                            f_row = {
                                "finding_id": fid, "related_control_id": selected_cid,
                                "finding_title": f_title, "finding_description": f_desc,
                                "risk_theme": "Incomplete Evidence", "severity": f_sev,
                                "likelihood": 3, "impact": 3,
                                "inherent_risk": f_sev, "existing_controls": "None",
                                "residual_risk": f_sev, "business_impact": "Loss of audit readiness",
                                "compliance_impact": f"Non-compliance with {row['framework']}", "recommended_action": f_rec,
                                "finding_owner": f_owner, "due_date": str(f_due),
                                "status": "Open", "closure_evidence": "", "closure_notes": ""
                            }
                            db.upsert_finding(f_row)
                            st.success(f"Audit finding {fid} successfully logged against {selected_cid}!")
                            st.rerun()

                elif action == "Request Risk Exception":
                    with st.form("quick_exception_form"):
                        st.markdown("##### ⚠️ Request Temporary Risk Exception / Risk Acceptance")
                        e_reason = st.text_area("Exception Reason / System constraints")
                        e_just = st.text_area("Business Justification / Financial or Ops block")
                        e_comp = st.text_area("Compensating Controls (How is risk minimized?)")
                        e_owner = st.text_input("Risk Acceptance Owner", value=row["control_owner"])
                        e_exp = st.date_input("Expiration Date")
                        
                        if st.form_submit_button("⚠️ Submit Exception"):
                            eid = f"EXC-{str(uuid.uuid4())[:6].upper()}"
                            e_row = {
                                "exception_id": eid, "related_control_id": selected_cid,
                                "related_finding_id": "", "exception_reason": e_reason,
                                "business_justification": e_just, "compensating_controls": e_comp,
                                "risk_acceptance_owner": e_owner, "approval_status": "Pending Approval",
                                "expiration_date": str(e_exp), "review_date": str(date.today()),
                                "notes": ""
                            }
                            db.upsert_exception(e_row)
                            st.success(f"Risk exception request {eid} submitted for review.")
                            st.rerun()

            with t3:
                st.markdown("#### 🚨 Linked Findings")
                linked_find = findings_df[findings_df["related_control_id"] == selected_cid]
                if not linked_find.empty:
                    st.dataframe(linked_find[["finding_id", "finding_title", "severity", "status", "due_date"]], use_container_width=True, hide_index=True)
                else:
                    st.success("✅ No open findings logged against this control.")

                st.markdown("#### ⚠️ Linked Exceptions")
                linked_exc = exceptions_df[exceptions_df["related_control_id"] == selected_cid]
                if not linked_exc.empty:
                    st.dataframe(linked_exc[["exception_id", "approval_status", "expiration_date", "risk_acceptance_owner"]], use_container_width=True, hide_index=True)
                else:
                    st.success("✅ No risk exceptions logged for this control.")


# ===========================================================================
# PAGE: Evidence Tracker
# ===========================================================================
def page_evidence_tracker():
    st.markdown("## 🗂️ Evidence Tracker")
    evidence_df = db.get_all_evidence()
    controls_df = db.get_all_controls()

    ev = calc.flag_evidence_gaps(evidence_df)

    with st.expander("🔍 Filter & Search", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            ev_statuses = ["All"] + sorted(ev["evidence_status"].dropna().unique().tolist())
            sel_es = st.selectbox("Evidence Status", ev_statuses)
        with col2:
            ev_types = ["All"] + sorted(ev["evidence_type"].dropna().unique().tolist())
            sel_et = st.selectbox("Evidence Type", ev_types)
        with col3:
            search_ev = st.text_input("Search (Name / Control / Owner)")

        show_gaps = st.checkbox("Show only evidence gaps", value=False)

    filtered_ev = ev.copy()
    if sel_es != "All":    filtered_ev = filtered_ev[filtered_ev["evidence_status"] == sel_es]
    if sel_et != "All":    filtered_ev = filtered_ev[filtered_ev["evidence_type"]   == sel_et]
    if show_gaps:          filtered_ev = filtered_ev[filtered_ev["is_gap"] == True]
    if search_ev:
        mask = (
            filtered_ev["evidence_name"].str.contains(search_ev, case=False, na=False) |
            filtered_ev["related_control_id"].str.contains(search_ev, case=False, na=False) |
            filtered_ev["evidence_owner"].str.contains(search_ev, case=False, na=False)
        )
        filtered_ev = filtered_ev[mask]

    gap_count = ev["is_gap"].sum()
    st.caption(f"**{gap_count} evidence gap(s)** flagged | Showing **{len(filtered_ev)}** records")

    display_ev = [
        "evidence_id", "related_control_id", "evidence_name",
        "evidence_type", "evidence_status", "evidence_owner",
        "date_collected", "expiration_date", "is_gap",
    ]
    st.dataframe(filtered_ev[display_ev], use_container_width=True, hide_index=True)

    # --- Add / Edit ---
    st.markdown("---")
    with st.expander("➕ Add or Edit Evidence"):
        EV_TYPES = ["Policy", "Procedure", "Screenshot", "Configuration Export",
                    "Log Sample", "Access Review", "SIEM Alert", "Cloud Configuration",
                    "Vulnerability Scan", "Ticket", "Architecture Diagram",
                    "Vendor Report", "SOC 2 Report", "ISO Certificate"]
        EV_STATI = ["Available", "Missing", "Incomplete", "Outdated", "Needs Review", "Approved"]

        prefill_eid = st.text_input("Existing Evidence ID to edit (blank = new)")
        ex_ev = {}
        if prefill_eid and not evidence_df.empty:
            rows = evidence_df[evidence_df["evidence_id"] == prefill_eid]
            if not rows.empty:
                ex_ev = rows.iloc[0].to_dict()

        def _eg(f, d=""):
            return ex_ev.get(f, d) or d

        with st.form("evidence_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                eid    = st.text_input("Evidence ID *", value=_eg("evidence_id") or f"EV-{str(uuid.uuid4())[:6].upper()}")
                ctrl   = st.text_input("Related Control ID", value=_eg("related_control_id"))
                ename  = st.text_input("Evidence Name *", value=_eg("evidence_name"))
            with c2:
                etype  = st.selectbox("Evidence Type", EV_TYPES, index=EV_TYPES.index(_eg("evidence_type", EV_TYPES[0])) if _eg("evidence_type") in EV_TYPES else 0)
                eowner = st.text_input("Evidence Owner", value=_eg("evidence_owner"))
                esrc   = st.text_input("Evidence Source", value=_eg("evidence_source"))
            with c3:
                estat  = st.selectbox("Evidence Status *", EV_STATI, index=EV_STATI.index(_eg("evidence_status", "Available")) if _eg("evidence_status") in EV_STATI else 0)
                ecoll  = st.text_input("Collection Method", value=_eg("collection_method"))

            edesc  = st.text_area("Evidence Description", value=_eg("evidence_description"))
            enotes = st.text_area("Review Notes", value=_eg("review_notes"))

            c4, c5 = st.columns(2)
            with c4:
                edate = st.date_input("Date Collected",
                                      value=datetime.strptime(_eg("date_collected", date.today().isoformat()), "%Y-%m-%d").date()
                                      if _eg("date_collected") else date.today())
            with c5:
                eexp  = st.date_input("Expiration Date",
                                      value=datetime.strptime(_eg("expiration_date", date.today().isoformat()), "%Y-%m-%d").date()
                                      if _eg("expiration_date") else date.today())

            if st.form_submit_button("💾 Save Evidence", type="primary"):
                if not eid or not ename:
                    st.error("Evidence ID and Name are required.")
                else:
                    row = {
                        "evidence_id": eid, "related_control_id": ctrl,
                        "evidence_name": ename, "evidence_type": etype,
                        "evidence_description": edesc, "evidence_owner": eowner,
                        "evidence_source": esrc, "collection_method": ecoll,
                        "evidence_status": estat, "date_collected": str(edate),
                        "expiration_date": str(eexp), "review_notes": enotes,
                    }
                    db.upsert_evidence(row)
                    st.success(f"✅ Evidence **{eid}** saved.")
                    st.rerun()


# ===========================================================================
# PAGE: Gap & Finding Tracker
# ===========================================================================
def page_findings():
    st.markdown("## 🔍 Gap & Finding Tracker")
    findings_df = db.get_all_findings()

    fd = calc.enrich_findings(findings_df) if not findings_df.empty else findings_df

    with st.expander("🔍 Filter & Search", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            severities = ["All"] + ["Critical", "High", "Medium", "Low"]
            sel_sev = st.selectbox("Severity", severities)
        with col2:
            fnd_statuses = ["All"] + sorted(findings_df["status"].dropna().unique().tolist()) if not findings_df.empty else ["All"]
            sel_fst = st.selectbox("Status", fnd_statuses)
        with col3:
            owners = ["All"] + sorted(findings_df["finding_owner"].dropna().unique().tolist()) if not findings_df.empty else ["All"]
            sel_own = st.selectbox("Owner", owners)
        with col4:
            search_f = st.text_input("Search (ID / Title)")

        show_overdue = st.checkbox("Show only overdue findings")

    filtered_f = fd.copy() if not fd.empty else pd.DataFrame()
    if not filtered_f.empty:
        if sel_sev != "All": filtered_f = filtered_f[filtered_f["severity"] == sel_sev]
        if sel_fst != "All": filtered_f = filtered_f[filtered_f["status"]   == sel_fst]
        if sel_own != "All": filtered_f = filtered_f[filtered_f["finding_owner"] == sel_own]
        if show_overdue and "is_overdue" in filtered_f.columns:
            filtered_f = filtered_f[filtered_f["is_overdue"] == True]
        if search_f:
            mask = (
                filtered_f["finding_id"].str.contains(search_f, case=False, na=False) |
                filtered_f["finding_title"].str.contains(search_f, case=False, na=False)
            )
            filtered_f = filtered_f[mask]

    display_f = [
        "finding_id", "related_control_id", "finding_title", "severity",
        "risk_theme", "status", "finding_owner", "due_date",
    ]
    if "is_overdue" in filtered_f.columns:
        display_f.append("is_overdue")

    st.caption(f"Showing **{len(filtered_f)}** finding(s)")
    if not filtered_f.empty:
        st.dataframe(filtered_f[display_f], use_container_width=True, hide_index=True)
    else:
        st.info("No findings match the current filters.")

    # Detail view
    if not findings_df.empty:
        st.markdown("---")
        selected_fid = st.selectbox("View finding detail", [""] + findings_df["finding_id"].tolist())
        if selected_fid:
            row = findings_df[findings_df["finding_id"] == selected_fid].iloc[0]
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Finding ID:** {row['finding_id']}")
                st.markdown(f"**Control:** {row['related_control_id']}")
                st.markdown(f"**Title:** {row['finding_title']}")
                st.markdown(f"**Severity:** {row['severity']}")
                st.markdown(f"**Risk Theme:** {row['risk_theme']}")
                st.markdown(f"**Status:** {row['status']}")
                st.markdown(f"**Owner:** {row['finding_owner']}")
                st.markdown(f"**Due Date:** {row['due_date']}")
            with col2:
                st.markdown(f"**Likelihood:** {row['likelihood']} / 5")
                st.markdown(f"**Impact:** {row['impact']} / 5")
                st.markdown(f"**Inherent Risk:** {row['inherent_risk']}")
                st.markdown(f"**Residual Risk:** {row['residual_risk']}")
                st.markdown(f"**Risk Score:** {calc.calculate_risk_score(row['likelihood'], row['impact'])}")
            st.markdown(f"**Description:** {row['finding_description']}")
            st.markdown(f"**Business Impact:** {row['business_impact']}")
            st.markdown(f"**Compliance Impact:** {row['compliance_impact']}")
            st.markdown(f"**Recommended Action:** {row['recommended_action']}")
            st.markdown(f"**Existing Controls:** {row['existing_controls']}")

    # --- Add / Edit ---
    st.markdown("---")
    with st.expander("➕ Add or Edit a Finding"):
        SEVERITIES = ["Critical", "High", "Medium", "Low"]
        RISK_THEMES = [
            "Excessive Access", "Missing MFA", "Weak Logging", "Missing Encryption",
            "Incomplete Evidence", "Outdated Policy", "Vendor Risk",
            "Unpatched System", "Poor Configuration", "Missing Review Process"
        ]
        FND_STATI = ["Open", "In Progress", "Pending Evidence",
                     "Risk Accepted", "Remediated", "Closed"]

        controls_df = db.get_all_controls()
        ctrl_ids = [""] + (controls_df["control_id"].tolist() if not controls_df.empty else [])

        prefill_fid = st.text_input("Existing Finding ID to edit (blank = new)", key="fnd_edit")
        ex_f = {}
        if prefill_fid and not findings_df.empty:
            rows = findings_df[findings_df["finding_id"] == prefill_fid]
            if not rows.empty:
                ex_f = rows.iloc[0].to_dict()

        def _ef(f, d=""):
            return ex_f.get(f, d) or d

        with st.form("finding_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                fid    = st.text_input("Finding ID *", value=_ef("finding_id") or f"FND-{str(uuid.uuid4())[:6].upper()}")
                fctrl  = st.text_input("Related Control ID", value=_ef("related_control_id"))
                ftitle = st.text_input("Finding Title *", value=_ef("finding_title"))
            with c2:
                fsev  = st.selectbox("Severity", SEVERITIES, index=SEVERITIES.index(_ef("severity", "Medium")) if _ef("severity") in SEVERITIES else 1)
                ftheme= st.selectbox("Risk Theme", RISK_THEMES, index=RISK_THEMES.index(_ef("risk_theme", RISK_THEMES[0])) if _ef("risk_theme") in RISK_THEMES else 0)
                fown  = st.text_input("Finding Owner", value=_ef("finding_owner"))
            with c3:
                fstat = st.selectbox("Status", FND_STATI, index=FND_STATI.index(_ef("status", "Open")) if _ef("status") in FND_STATI else 0)
                flik  = st.slider("Likelihood (1–5)", 1, 5, int(_ef("likelihood", 3)))
                fimp  = st.slider("Impact (1–5)", 1, 5, int(_ef("impact", 3)))

            fdue = st.date_input("Due Date",
                                  value=datetime.strptime(_ef("due_date", date.today().isoformat()), "%Y-%m-%d").date()
                                  if _ef("due_date") else date.today())

            st.markdown(f"**Auto-calculated Risk Score:** `{calc.calculate_risk_score(flik, fimp)}`")

            fdesc   = st.text_area("Finding Description",    value=_ef("finding_description"))
            fexist  = st.text_area("Existing Controls",      value=_ef("existing_controls"))
            frec    = st.text_area("Recommended Action",     value=_ef("recommended_action"))
            fbimp   = st.text_area("Business Impact",        value=_ef("business_impact"))
            fcimp   = st.text_area("Compliance Impact",      value=_ef("compliance_impact"))
            finhir  = st.text_input("Inherent Risk",         value=_ef("inherent_risk"))
            fresid  = st.text_input("Residual Risk",         value=_ef("residual_risk"))
            fclose_ev = st.text_area("Closure Evidence",     value=_ef("closure_evidence"))
            fclose_n  = st.text_area("Closure Notes",        value=_ef("closure_notes"))

            if st.form_submit_button("💾 Save Finding", type="primary"):
                if not fid or not ftitle:
                    st.error("Finding ID and Title are required.")
                else:
                    row = {
                        "finding_id": fid, "related_control_id": fctrl,
                        "finding_title": ftitle, "finding_description": fdesc,
                        "risk_theme": ftheme, "severity": fsev,
                        "likelihood": flik, "impact": fimp,
                        "inherent_risk": finhir, "existing_controls": fexist,
                        "residual_risk": fresid, "business_impact": fbimp,
                        "compliance_impact": fcimp, "recommended_action": frec,
                        "finding_owner": fown, "due_date": str(fdue),
                        "status": fstat, "closure_evidence": fclose_ev,
                        "closure_notes": fclose_n,
                    }
                    db.upsert_finding(row)
                    st.success(f"✅ Finding **{fid}** saved.")
                    st.rerun()


# ===========================================================================
# PAGE: Remediation Tracker
# ===========================================================================
def page_remediation():
    st.markdown("## 🔧 Remediation Tracker")
    remediation_df = db.get_all_remediation()
    findings_df    = db.get_all_findings()

    rem = calc.flag_overdue_remediation(remediation_df) if not remediation_df.empty else remediation_df

    with st.expander("🔍 Filter & Search", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            rem_statuses = ["All"] + sorted(remediation_df["current_status"].dropna().unique().tolist()) if not remediation_df.empty else ["All"]
            sel_rs = st.selectbox("Status", rem_statuses)
        with col2:
            rem_owners = ["All"] + sorted(remediation_df["owner"].dropna().unique().tolist()) if not remediation_df.empty else ["All"]
            sel_ro = st.selectbox("Owner", rem_owners)
        with col3:
            show_overdue_r = st.checkbox("Show only overdue items")

    filtered_r = rem.copy() if not rem.empty else pd.DataFrame()
    if not filtered_r.empty:
        if sel_rs != "All": filtered_r = filtered_r[filtered_r["current_status"] == sel_rs]
        if sel_ro != "All": filtered_r = filtered_r[filtered_r["owner"] == sel_ro]
        if show_overdue_r and "is_overdue" in filtered_r.columns:
            filtered_r = filtered_r[filtered_r["is_overdue"] == True]

    display_r = ["remediation_id", "finding_id", "owner", "target_date",
                 "current_status", "validation_required"]
    if "is_overdue" in filtered_r.columns:
        display_r.append("is_overdue")

    st.caption(f"Showing **{len(filtered_r)}** remediation item(s)")
    if not filtered_r.empty:
        st.dataframe(filtered_r[display_r], use_container_width=True, hide_index=True)
    else:
        st.info("No remediation items found.")

    # --- Add / Edit ---
    st.markdown("---")
    with st.expander("➕ Add or Edit Remediation Item"):
        REM_STATI = ["Open", "In Progress", "Pending Evidence",
                     "Validation", "Closed"]

        fnd_ids = [""] + (findings_df["finding_id"].tolist() if not findings_df.empty else [])
        prefill_rid = st.text_input("Existing Remediation ID to edit (blank = new)", key="rem_edit")
        ex_r = {}
        if prefill_rid and not remediation_df.empty:
            rows = remediation_df[remediation_df["remediation_id"] == prefill_rid]
            if not rows.empty:
                ex_r = rows.iloc[0].to_dict()

        def _er(f, d=""):
            return ex_r.get(f, d) or d

        with st.form("remediation_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                rid   = st.text_input("Remediation ID *", value=_er("remediation_id") or f"REM-{str(uuid.uuid4())[:6].upper()}")
                rfid  = st.text_input("Related Finding ID", value=_er("finding_id"))
                rownr = st.text_input("Owner", value=_er("owner"))
            with c2:
                rtgt  = st.date_input("Target Date",
                                       value=datetime.strptime(_er("target_date", date.today().isoformat()), "%Y-%m-%d").date()
                                       if _er("target_date") else date.today())
                rstat = st.selectbox("Current Status", REM_STATI,
                                     index=REM_STATI.index(_er("current_status", "Open")) if _er("current_status") in REM_STATI else 0)
                rval  = st.selectbox("Validation Required", ["Yes", "No"],
                                     index=["Yes","No"].index(_er("validation_required", "No")) if _er("validation_required") in ["Yes","No"] else 0)
            with c3:
                rclosed = st.date_input("Date Closed (if applicable)",
                                         value=datetime.strptime(_er("date_closed", date.today().isoformat()), "%Y-%m-%d").date()
                                         if _er("date_closed") else date.today())

            ract  = st.text_area("Action Plan",        value=_er("action_plan"))
            rprog = st.text_area("Progress Notes",     value=_er("progress_notes"))
            rdep  = st.text_input("Dependency",        value=_er("dependency"))
            rcev  = st.text_area("Closure Evidence",   value=_er("closure_evidence"))

            if st.form_submit_button("💾 Save Remediation", type="primary"):
                if not rid:
                    st.error("Remediation ID is required.")
                else:
                    row = {
                        "remediation_id": rid, "finding_id": rfid,
                        "owner": rownr, "action_plan": ract,
                        "target_date": str(rtgt), "current_status": rstat,
                        "progress_notes": rprog, "dependency": rdep,
                        "validation_required": rval, "closure_evidence": rcev,
                        "date_closed": str(rclosed) if rstat == "Closed" else "",
                    }
                    db.upsert_remediation(row)
                    st.success(f"✅ Remediation **{rid}** saved.")
                    st.rerun()


# ===========================================================================
# PAGE: Exception Tracker
# ===========================================================================
def page_exceptions():
    st.markdown("## ⚠️ Exception Tracker")
    exceptions_df = db.get_all_exceptions()
    controls_df   = db.get_all_controls()
    findings_df   = db.get_all_findings()

    exc = calc.flag_expired_exceptions(exceptions_df) if not exceptions_df.empty else exceptions_df

    with st.expander("🔍 Filter & Search", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            approval_opts = ["All"] + sorted(exceptions_df["approval_status"].dropna().unique().tolist()) if not exceptions_df.empty else ["All"]
            sel_app = st.selectbox("Approval Status", approval_opts)
        with col2:
            exc_owners = ["All"] + sorted(exceptions_df["risk_acceptance_owner"].dropna().unique().tolist()) if not exceptions_df.empty else ["All"]
            sel_eo = st.selectbox("Risk Owner", exc_owners)
        with col3:
            show_exp = st.checkbox("Show only expired exceptions")

    filtered_e = exc.copy() if not exc.empty else pd.DataFrame()
    if not filtered_e.empty:
        if sel_app != "All": filtered_e = filtered_e[filtered_e["approval_status"] == sel_app]
        if sel_eo  != "All": filtered_e = filtered_e[filtered_e["risk_acceptance_owner"] == sel_eo]
        if show_exp and "is_expired" in filtered_e.columns:
            filtered_e = filtered_e[filtered_e["is_expired"] == True]

    display_e = ["exception_id", "related_control_id", "related_finding_id",
                 "approval_status", "risk_acceptance_owner",
                 "expiration_date", "review_date"]
    if "is_expired" in filtered_e.columns:
        display_e.append("is_expired")

    st.caption(f"Showing **{len(filtered_e)}** exception(s)")
    if not filtered_e.empty:
        st.dataframe(filtered_e[display_e], use_container_width=True, hide_index=True)
    else:
        st.info("No exceptions found.")

    # --- Add / Edit ---
    st.markdown("---")
    with st.expander("➕ Add or Edit Exception"):
        APPROVAL_STATI = ["Draft", "Pending Approval", "Approved", "Rejected", "Expired"]

        prefill_eid2 = st.text_input("Existing Exception ID to edit (blank = new)", key="exc_edit")
        ex_exc = {}
        if prefill_eid2 and not exceptions_df.empty:
            rows = exceptions_df[exceptions_df["exception_id"] == prefill_eid2]
            if not rows.empty:
                ex_exc = rows.iloc[0].to_dict()

        def _ee(f, d=""):
            return ex_exc.get(f, d) or d

        with st.form("exception_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                excid  = st.text_input("Exception ID *", value=_ee("exception_id") or f"EXC-{str(uuid.uuid4())[:6].upper()}")
                ectrl  = st.text_input("Related Control ID",  value=_ee("related_control_id"))
                efid   = st.text_input("Related Finding ID",  value=_ee("related_finding_id"))
            with c2:
                eown   = st.text_input("Risk Acceptance Owner", value=_ee("risk_acceptance_owner"))
                eapp   = st.selectbox("Approval Status", APPROVAL_STATI,
                                      index=APPROVAL_STATI.index(_ee("approval_status","Draft")) if _ee("approval_status") in APPROVAL_STATI else 0)
            with c3:
                eexp2  = st.date_input("Expiration Date",
                                        value=datetime.strptime(_ee("expiration_date", date.today().isoformat()), "%Y-%m-%d").date()
                                        if _ee("expiration_date") else date.today())
                erev   = st.date_input("Review Date",
                                        value=datetime.strptime(_ee("review_date", date.today().isoformat()), "%Y-%m-%d").date()
                                        if _ee("review_date") else date.today())

            ereason = st.text_area("Exception Reason *",          value=_ee("exception_reason"))
            ejust   = st.text_area("Business Justification",      value=_ee("business_justification"))
            ecomp   = st.text_area("Compensating Controls",       value=_ee("compensating_controls"))
            enotes2 = st.text_area("Notes",                       value=_ee("notes"))

            if st.form_submit_button("💾 Save Exception", type="primary"):
                if not excid or not ereason:
                    st.error("Exception ID and Reason are required.")
                else:
                    row = {
                        "exception_id": excid, "related_control_id": ectrl,
                        "related_finding_id": efid, "exception_reason": ereason,
                        "business_justification": ejust,
                        "compensating_controls": ecomp,
                        "risk_acceptance_owner": eown,
                        "approval_status": eapp,
                        "expiration_date": str(eexp2),
                        "review_date": str(erev),
                        "notes": enotes2,
                    }
                    db.upsert_exception(row)
                    st.success(f"✅ Exception **{excid}** saved.")
                    st.rerun()


# ===========================================================================
# PAGE: Import / Export
# ===========================================================================
def page_import_export():
    st.markdown("## 📥 Import / Export")

    controls_df, evidence_df, findings_df, remediation_df, exceptions_df = load_all()

    # --- Export ---
    st.markdown("### 📤 Export All Data to Excel")
    st.write("Download a multi-sheet Excel workbook containing all BASTION data.")

    if st.button("⬇️ Generate Excel Export", type="primary"):
        report = rep.build_management_report(
            controls_df, evidence_df, findings_df, remediation_df, exceptions_df
        )
        excel_bytes = rep.export_to_excel_bytes(
            controls_df, evidence_df, findings_df,
            remediation_df, exceptions_df, report
        )
        st.download_button(
            label="📥 Download BASTION_Export.xlsx",
            data=excel_bytes,
            file_name=f"BASTION_Export_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.markdown("---")

    # --- CSV Import ---
    st.markdown("### 📂 Import Controls from CSV")
    st.write(
        "Upload a CSV file with the same columns as the Controls table. "
        "Rows with existing Control IDs will be updated (upserted)."
    )

    with st.expander("📋 Required CSV columns for controls"):
        st.code(
            "control_id, framework, control_family, control_title, control_description, "
            "requirement_summary, control_owner, system_application, data_type, "
            "implementation_status, evidence_required, evidence_available, evidence_source, "
            "evidence_link, last_reviewed_date, next_review_date, assessor_notes"
        )

    uploaded_controls = st.file_uploader("Upload Controls CSV", type=["csv"], key="ctrl_upload")
    if uploaded_controls:
        try:
            import_df = pd.read_csv(uploaded_controls)
            st.dataframe(import_df.head(5), use_container_width=True, hide_index=True)
            st.caption(f"Preview: {len(import_df)} row(s) loaded")
            if st.button("✅ Import Controls"):
                for _, row in import_df.iterrows():
                    db.upsert_control(row.to_dict())
                st.success(f"Imported {len(import_df)} control(s).")
                st.rerun()
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

    st.markdown("---")

    st.markdown("### 📂 Import Evidence from CSV")
    with st.expander("📋 Required CSV columns for evidence"):
        st.code(
            "evidence_id, related_control_id, evidence_name, evidence_type, "
            "evidence_description, evidence_owner, evidence_source, collection_method, "
            "evidence_status, date_collected, expiration_date, review_notes"
        )

    uploaded_evidence = st.file_uploader("Upload Evidence CSV", type=["csv"], key="ev_upload")
    if uploaded_evidence:
        try:
            import_ev = pd.read_csv(uploaded_evidence)
            st.dataframe(import_ev.head(5), use_container_width=True, hide_index=True)
            if st.button("✅ Import Evidence"):
                for _, row in import_ev.iterrows():
                    db.upsert_evidence(row.to_dict())
                st.success(f"Imported {len(import_ev)} evidence record(s).")
                st.rerun()
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

    st.markdown("---")

    # --- Download Templates ---
    st.markdown("### 📎 Download CSV Templates")
    col1, col2 = st.columns(2)
    with col1:
        ctrl_template = pd.DataFrame(columns=[
            "control_id", "framework", "control_family", "control_title",
            "control_description", "requirement_summary", "control_owner",
            "system_application", "data_type", "implementation_status",
            "evidence_required", "evidence_available", "evidence_source",
            "evidence_link", "last_reviewed_date", "next_review_date", "assessor_notes"
        ])
        import io as _io
        buf = _io.StringIO()
        ctrl_template.to_csv(buf, index=False)
        st.download_button(
            "⬇️ Controls Template CSV",
            data=buf.getvalue(),
            file_name="controls_template.csv",
            mime="text/csv",
        )
    with col2:
        ev_template = pd.DataFrame(columns=[
            "evidence_id", "related_control_id", "evidence_name", "evidence_type",
            "evidence_description", "evidence_owner", "evidence_source",
            "collection_method", "evidence_status", "date_collected",
            "expiration_date", "review_notes"
        ])
        buf2 = _io.StringIO()
        ev_template.to_csv(buf2, index=False)
        st.download_button(
            "⬇️ Evidence Template CSV",
            data=buf2.getvalue(),
            file_name="evidence_template.csv",
            mime="text/csv",
        )

    st.markdown("---")
    st.markdown("### ♻️ Reset Database")
    st.warning("⚠️ This will delete **all data** and reload the original seed data.")
    if st.button("🗑️ Reset to Seed Data", type="secondary"):
        import os, database as db2
        if os.path.exists(db2.DB_PATH):
            os.remove(db2.DB_PATH)
        db2.init_db()
        from seed_data import load_seed_data as _lsd
        _lsd()
        st.success("✅ Database reset and seed data reloaded.")
        st.rerun()


# ===========================================================================
# PAGE: Management Report
# ===========================================================================
def page_management_report():
    st.markdown("## 📄 Management Report")
    st.write("A management-ready summary of the current assessment state.")

    controls_df, evidence_df, findings_df, remediation_df, exceptions_df = load_all()

    report = rep.build_management_report(
        controls_df, evidence_df, findings_df, remediation_df, exceptions_df
    )
    m = report["metrics"]

    # --- Summary KPIs ---
    st.markdown("### 📊 Executive Summary")
    col1, col2 = st.columns(2)

    with col1:
        summary_data = {
            "Metric": [
                "Total Controls Assessed",
                "Controls Implemented",
                "Partially Implemented",
                "Not Implemented",
                "Not Assessed",
                "Evidence Gaps",
                "Open Findings",
                "Overdue Remediation Items",
                "Accepted Exceptions",
                "High / Critical Findings",
            ],
            "Count": [
                m["total_controls"], m["implemented"], m["partially_implemented"],
                m["not_implemented"], m["not_assessed"], m["evidence_gaps"],
                m["open_findings"], m["overdue_remediation"],
                m["accepted_exceptions"], m["high_risk_findings"],
            ],
        }
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

    with col2:
        # Control implementation donut chart
        labels = ["Implemented", "Partially Implemented", "Not Implemented", "Not Assessed"]
        values = [m["implemented"], m["partially_implemented"], m["not_implemented"], m["not_assessed"]]
        colors = ["#3fb950", "#d29922", "#f85149", "#8b949e"]
        fig = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            marker=dict(colors=colors),
        ))
        fig.update_layout(
            paper_bgcolor="#1c2128",
            font=dict(color="#c9d1d9"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=260,
            showlegend=True,
            legend=dict(font=dict(size=10)),
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- Top Findings ---
    st.markdown("### 🚨 Top 5 High-Risk Findings")
    tf = report["top_findings"]
    if not tf.empty:
        st.dataframe(tf, use_container_width=True, hide_index=True)
    else:
        st.info("No findings recorded.")

    # --- Evidence Gaps ---
    st.markdown("### 🕳️ Evidence Gaps")
    eg = report["evidence_gaps"]
    if not eg.empty:
        st.dataframe(eg, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No evidence gaps detected.")

    # --- Overdue Remediation ---
    st.markdown("### ⏰ Overdue Remediation Items")
    oi = report["overdue_rem"]
    if not oi.empty:
        st.dataframe(oi, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No overdue remediation items.")

    # --- Active Exceptions ---
    st.markdown("### 📋 Active Risk Exceptions")
    ae = report["active_exceptions"]
    if not ae.empty:
        st.dataframe(ae, use_container_width=True, hide_index=True)
    else:
        st.info("No active exceptions.")

    # --- Recommended Next Steps ---
    st.markdown("### ✅ Recommended Next Steps")
    steps = [
        "Remediate all Critical and High findings within 30 days.",
        "Collect missing evidence for all flagged gaps before the next audit cycle.",
        "Conduct the overdue IR tabletop exercise within 60 days.",
        "Complete the HIPAA annual risk assessment immediately.",
        "Obtain executed BAAs from all PHI-handling vendors.",
        "Deploy vulnerability scanning coverage to AWS S3 Data Lake workloads.",
        "Review and renew all exceptions approaching expiration.",
    ]
    for i, step in enumerate(steps, 1):
        st.markdown(f"**{i}.** {step}")

    st.markdown("---")

    # --- Export options ---
    st.markdown("### 📤 Export Report")
    col_a, col_b = st.columns(2)

    with col_a:
        excel_bytes = rep.export_to_excel_bytes(
            controls_df, evidence_df, findings_df,
            remediation_df, exceptions_df, report
        )
        st.download_button(
            label="📥 Export to Excel (.xlsx)",
            data=excel_bytes,
            file_name=f"BASTION_Report_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    with col_b:
        md_text = rep.export_to_markdown(report)
        st.download_button(
            label="📝 Export to Markdown (.md)",
            data=md_text.encode("utf-8"),
            file_name=f"BASTION_Report_{date.today()}.md",
            mime="text/markdown",
        )


# ===========================================================================
# Router
# ===========================================================================
if   "Dashboard"          in page: page_dashboard()
elif "Control Library"    in page: page_control_library()
elif "Common Controls"    in page: page_ccf()
elif "Review Center"      in page: page_assessor_review_center()
elif "Evidence Tracker"   in page: page_evidence_tracker()
elif "Gap & Finding"      in page: page_findings()
elif "Remediation"        in page: page_remediation()
elif "Exception"          in page: page_exceptions()
elif "Import / Export"    in page: page_import_export()
elif "Management Report"  in page: page_management_report()
