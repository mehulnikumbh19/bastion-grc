# 🛡️ BASTION – Security Control Assessment & Evidence Tracker

> A practical security control assessment and audit-readiness tool for GRC, Cloud Security, and Compliance professionals.

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/mehulnikumbh19/bastion-grc)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://bastion-grc.streamlit.app)

---

## 📌 Overview

**BASTION** is a Python-based web application that simulates the core workflow of a security assessor reviewing technical and compliance controls. It maps security requirements across multiple industry frameworks, tracks audit evidence, identifies control gaps, manages remediation efforts, and generates management-ready reports—all in a clean, professional interface.

Built as a portfolio/resume project demonstrating real-world GRC and Cloud Security Compliance skills.

---

## 🔍 Problem Statement

Security assessors and GRC analysts need to:
1. Map hundreds of security controls across multiple frameworks (NIST, CIS, ISO 27001, SOC 2, etc.)
2. Track evidence collection status for each control
3. Identify gaps and create audit findings with risk ratings
4. Assign remediation owners and track progress
5. Manage risk exceptions with business justifications
6. Report status to management in a clear, actionable format

Existing enterprise GRC tools (Archer, ServiceNow GRC, OneTrust) cost thousands of dollars per year. BASTION demonstrates the same conceptual workflow in an open-source Python tool.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **Dashboard** | KPI cards, 3 Plotly charts, and a framework compliance index representing GRC health |
| 📋 **Control Library** | 30 pre-loaded controls across 7 frameworks; full CRUD with filters |
| 🛡️ **Common Controls (CCF)** | Unified Common Control Framework mapping internal policies to multiple external frameworks |
| 🔎 **Assessor Review Center** | Productivity interface for side-by-side control evaluation, evidence audits, and quick actions |
| 🗂️ **Evidence Tracker** | Evidence status tracking with automatic gap flagging |
| 🔍 **Gap & Finding Tracker** | Risk-rated findings with severity, likelihood, impact, and residual risk |
| 🔧 **Remediation Tracker** | Remediation action plans with owner, due date, and overdue detection |
| ⚠️ **Exception Tracker** | Risk acceptance records with compensating controls and expiry tracking |
| 📥 **Import / Export** | CSV import for controls and evidence; multi-sheet Excel export |
| 📄 **Management Report** | Auto-generated executive summary with Excel and Markdown export |

---

## 🏗️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| Web Framework | Streamlit |
| Data Processing | pandas |
| Database | SQLite (stdlib `sqlite3`) |
| Visualization | Plotly |
| Export | openpyxl |

---

## 📁 Project Structure

```
bastion/
│
├── app.py               # Main Streamlit application (8 pages)
├── database.py          # SQLite schema + CRUD operations
├── seed_data.py         # 30 controls, 20 evidence, 10 findings, 8 rem, 5 exc
├── calculations.py      # Risk scoring, gap flagging, overdue detection
├── reports.py           # Management report + Excel/Markdown export
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── .gitignore
│
├── data/
│   └── bastion.db       # SQLite database (auto-created on first run)
│
├── exports/             # Excel and Markdown reports saved here
│
└── sample_imports/
    ├── controls_template.csv   # CSV import template for controls
    └── evidence_template.csv   # CSV import template for evidence
```

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.10 or higher
- pip

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR-USERNAME/bastion.git
cd bastion
```

### 2. Create a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**

> **Note:** On first launch, BASTION automatically creates the SQLite database and loads 30 sample controls, 20 evidence records, 10 findings, 8 remediation items, and 5 exceptions.

---

## 🔄 How to Reset the Database

**Option A – From the App:**
1. Go to **📥 Import / Export** page
2. Scroll to "Reset Database"
3. Click **🗑️ Reset to Seed Data**

**Option B – From the terminal:**
```bash
# Delete the database file
del data\bastion.db        # Windows
rm data/bastion.db         # macOS/Linux

# Restart the app – seed data reloads automatically
streamlit run app.py
```

---

## 📊 Sample Workflow

1. **Open the Dashboard** → See overall control implementation and risk posture at a glance
2. **Browse the Control Library** → Filter by framework (e.g., HIPAA) or status (e.g., Not Implemented)
3. **Review the Evidence Tracker** → Check the "Show only evidence gaps" filter to see what's missing
4. **Open Gap & Finding Tracker** → Review severity ratings and overdue items
5. **Check Remediation Tracker** → See who owns what and whether items are overdue
6. **Review Exception Tracker** → Confirm no exceptions have expired
7. **Generate a Management Report** → Export to Excel or Markdown for stakeholder review

---

## 🔐 Security & GRC Concepts Demonstrated

- **Control Mapping**: Aligning technical and procedural controls to NIST SP 800-53, CIS Controls, ISO 27001, SOC 2, HIPAA, HITRUST, PCI DSS
- **Evidence Review**: Classifying evidence by type, collection method, validity period, and status
- **Risk Rating**: Using a 5×5 likelihood × impact matrix to calculate inherent and residual risk
- **Gap Analysis**: Identifying control deficiencies and creating structured findings
- **Remediation Tracking**: Assigning owners, due dates, and action plans to close gaps
- **Risk Exception Management**: Documenting business justifications and compensating controls
- **Audit Readiness**: Organizing evidence records to demonstrate control effectiveness
- **Access Control Review**: Tracking unique user identification, MFA, and de-provisioning
- **Encryption Controls**: Monitoring at-rest and in-transit encryption requirements
- **Vendor Risk**: Tracking third-party assessments and BAA compliance
- **Cloud Security**: Mapping AWS configuration controls and security baselines

---

## 📸 Screenshots

*Add screenshots here after running the app locally.*

| Dashboard | Control Library |
|---|---|
| ![Dashboard](screenshots/dashboard.png) | ![Controls](screenshots/controls.png) |

| Evidence Tracker | Management Report |
|---|---|
| ![Evidence](screenshots/evidence.png) | ![Report](screenshots/report.png) |

---

## 📝 Resume Bullet Suggestions

Use these on your resume under a **Projects** or **GRC Tools** section:

- Built a **Streamlit and SQLite-based security control assessment tracker** that maps controls across NIST SP 800-53, CIS Controls, ISO 27001, SOC 2, HIPAA, HITRUST, and PCI DSS.
- Designed a **Common Control Framework (CCF)** mapping 10 unified internal company controls to multiple regulatory standards to streamline audits and prevent "audit fatigue".
- Developed an **interactive Assessor Review Center** for side-by-side control & evidence evaluation, enabling assessors to audit evidence, log findings, or request risk exceptions in a unified dashboard.
- Implemented **automated risk calculations** utilizing a 5×5 likelihood-impact matrix, with system criticality weighting and real-time gap detection across AWS configurations (KMS, CloudTrail, Config).
- Created **executive dashboard metrics and framework compliance charts** using Python, Plotly, and openpyxl to deliver multi-sheet management-ready reports and exports.

---

## 🎤 Interview Talking Points

### One-Sentence Explanation
> "I built BASTION to simulate the daily work of a security assessor—mapping controls to frameworks, tracking evidence, identifying gaps, and generating management-ready risk summaries."

### Detailed Explanation
> "BASTION is a Python and Streamlit application that mirrors what GRC and Cloud Security teams do every day. I designed it around the full assessment lifecycle: you start by mapping controls to frameworks like NIST 800-53, HIPAA, and PCI DSS, then you track evidence collection for each control, flag gaps when evidence is missing or outdated, create structured findings with risk scores, assign remediation owners, and manage exceptions where risks are accepted. The tool automatically flags overdue items, calculates risk scores using a 5×5 likelihood-impact matrix, and generates executive summaries exportable to Excel or Markdown. I built it to demonstrate that I understand not just the tools, but the actual process and decision-making behind a security assessment."

### Technical Questions You Can Answer
- **"How does the risk scoring work?"** — Likelihood (1–5) × Impact (1–5) matrix. A 4×4 scores as High, a 4×5 scores Critical. Matches standard NIST/ISO risk methodology.
- **"What's the difference between a finding and a remediation?"** — A finding documents the gap and its risk. A remediation is the action plan to close it. They're linked by Finding ID.
- **"What's a risk exception?"** — When a control cannot be implemented due to technical or business constraints, an exception documents the reason, compensating controls, business owner approval, and an expiration date for review.
- **"How did you handle evidence gaps?"** — Any evidence record with status Missing, Incomplete, or Outdated is automatically flagged as a gap in the Evidence Tracker and counted in the dashboard KPIs.
- **"Why SQLite instead of PostgreSQL?"** — SQLite requires no server setup, making it ideal for a local portfolio project. The CRUD abstraction layer in database.py could be swapped for PostgreSQL or a cloud database with minimal code changes.

---

## 🔮 Future Improvements

- [ ] User authentication (role-based: Assessor, Manager, Control Owner)
- [ ] Email notifications for overdue items and expiring exceptions
- [ ] Control version history / audit trail
- [ ] Integration with cloud APIs (AWS Config, Azure Policy, GCP SCC)
- [ ] Scheduled automated evidence collection
- [ ] Compliance scoring / maturity model (e.g., CMMC maturity levels)
- [ ] PDF report generation
- [ ] REST API layer for programmatic access

---

## 📜 License

MIT License — free to use, modify, and share.

---

*Built with Python, Streamlit, pandas, SQLite, and Plotly.*
*Designed for Security Assessor, GRC Analyst, and Cloud Security Compliance portfolio use.*
