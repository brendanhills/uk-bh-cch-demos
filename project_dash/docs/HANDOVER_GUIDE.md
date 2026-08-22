# F-DSE Program Governance & Risk Intelligence Platform — Turnkey Handover Guide

> **Operator & Maintainer Manual**
> **Primary Stakeholder / Business Owner**: Allison Innes (`allins@google.com`)  
> **Technical & Program Leads**: Steve Deacon (`sdeacon@google.com`), Wayne Davis (`waynedavis@google.com`), Brendan Hills (`brendanhills@google.com`)

---

## 📌 Executive Summary & Architecture

The **F-DSE Program Governance & Risk Intelligence Platform** is a zero-build, single-page web application designed for executive decision-making, live risk matrix analysis, and contractual delivery governance.

### Zero-Server / Browser-Direct Architecture
* **Where does the app run?**: The dashboard runs directly in the user's web browser as a pure static Single-Page Application (`index.html`).
* **Who maintains backend servers?**: **No one.** There are no cloud VMs, Borg jobs, or backend servers required to be running 24/7.
* **Storage Backend**: The single source of truth is your team's **Google Drive Shared Folder** containing weekly PDF risk reports, Google Sheets registers, and `weekly_snapshots.json`.
* **AI Intelligence**: Executive briefings are synthesized using Google Gemini 3.5 Pro API.

---

## 👥 Access Control & Ganpati (MDB) Groups

User access is governed through three Google-native **Ganpati (MDB)** Prod groups:

| Group Name | Type | Target Audience | Direct Web Management Link |
| :--- | :--- | :--- | :--- |
| **`monaro-risk-admin`** | `ADMIN` | **System Admins & Leads**: Owns the team groups and manages access policies. | [Manage Admin Group](https://ganpati2.corp.google.com/group/%25monaro-risk-admin.prod) |
| **`monaro-risk-dev`** | `TEAM` | **Developers & Editors**: Technical team members with edit and deployment access. | [Manage Dev Group](https://ganpati2.corp.google.com/group/%25monaro-risk-dev.prod) |
| **`monaro-risk-prod`** | `TEAM` | **Executive Stakeholders & Viewers**: Viewers including `allins@google.com` and governance officers. | [Manage Prod Group](https://ganpati2.corp.google.com/group/%25monaro-risk-prod.prod) |

### How to Add or Remove Users:
1. Open the Ganpati link for **[monaro-risk-prod](https://ganpati2.corp.google.com/group/%25monaro-risk-prod.prod)** (for viewers) or **[monaro-risk-dev](https://ganpati2.corp.google.com/group/%25monaro-risk-dev.prod)** (for editors).
2. Go to the **"Children"** tab $\rightarrow$ click **"Propose New Children"**.
3. Type the user's LDAP (e.g. `allins`) and submit.
4. Since `monaro-risk-admin` owns the groups, the proposal will be automatically approved.

---

## 🔄 How to Ingest New Weekly Reports (1-Click Workflow)

When a new weekly risk register arrives (e.g., Week 28 PDF or updated Google Sheet):

### Method A: Direct from the Dashboard Web UI (Recommended • 0 Code)
1. Drop the new weekly PDF report (e.g. `Weekly Reporting - Week 28 - 14 Aug 2026.pdf` or `Status_Report.pdf`) into the team's shared Google Drive folder.
2. Open the dashboard in your browser (`http://localhost:9000/?project=f-dse`).
3. Click the **"Sync with Google Drive"** button in the header.
4. The dashboard will automatically detect the new file, run the self-healing ingestion pipeline, generate the executive briefing, and refresh the 5×5 heatmap and Time Machine ribbon in real time!

### Method B: Unified Pipeline CLI (Optional 1-Command Tool)
If you prefer running a command-line script to synchronize all streams or ingest a specific report:
```bash
# 1-Command full workspace sync:
python3 scripts/pipeline.py --project=f-dse --sync

# 1-Command weekly PDF ingestion:
python3 scripts/pipeline.py --project=f-dse --ingest-report="Weekly Reporting - Week 28 - 14 Aug 2026.pdf"
```

---


---

## 📚 How to Add & Sync Additional Gemini Notebooks

The dashboard supports a **Generalized Multi-Notebook Architecture**. You can connect multiple Gemini Notebooks (e.g. *Contract Notebook*, *Technical Architecture Blueprints*, *Security ATO Accreditation*, *Commercial SLAs*).

### 1. Adding a New Gemini Notebook (1 Command)
To register and synchronize a new Gemini Notebook, run:
```bash
python3 scripts/sync_notebook.py \
  --notebook-id "<GEMINI_NOTEBOOK_UUID>" \
  --title "Technical Architecture & System Blueprints" \
  --slug "tech_blueprints" \
  --category "Architecture & Engineering" \
  --description "Vertex AI Enclaves, Diode Ingestion, and GDC Infrastructure Specifications"
```

### 2. How It Works in the UI:
1. The dashboard reads the central registry at `data/notebooks/registry.json`.
2. A **Notebook Dropdown Selector** appears in the header of the Contractual & Blueprint Knowledge tab.
3. Switching notebooks instantly swaps the 17+ ingested documents, token counts, category breakdowns, and dynamic risk mappings!

## 🚀 Running & Deploying the Dashboard

### 1. Running Locally or on Cloudtop (1-Command Runner)
```bash
# Start local server in a managed tmux session
./run_server.sh

# Check server status
./run_server.sh status

# Restart server
./run_server.sh restart

# Stop server
./run_server.sh kill

# Access URL:
http://localhost:9000
```

### 2. Immediate Service Shutdown (Emergency Stop)
If you ever need to immediately take any running service offline:
```bash
./deploy/shutdown.sh
# or
./deploy/stop.sh
```

---

## 📁 Key File Index

| File / Directory | Description |
| :--- | :--- |
| **`index.html`** | Core single-file web application (UI, Tailwind CSS, Chart.js, and audio briefing player). |
| **`scripts/pipeline.py`** | Unified ingestion engine: Google Sheets sync, Drive report ingestion, and Gemini AI synthesis. |
| **`server.py`** | Streamlined local Python server with clean REST APIs (`/api/status`, `/api/sync`, `/api/ingest`). |
| **`run_server.sh`** | 1-command tmux lifecycle script (start, attach, restart, kill). |
| **`docs/HANDOVER_GUIDE.md`** | This operator manual and team handover guide. |
| **`README.md`** | Comprehensive project overview and architecture documentation. |
| **`docs/TEAM_PRESENTATION_GUIDE.md`** | Presentation guide and demo narrative for stakeholder meetings. |
| **`docs/DEPLOYMENT_GUIDE.md`** | Automated CI/CD deployment guide and Cloud Run / IAP configuration. |
| **`data/sample/snapshots.json`** | Historical time travel risk register snapshots. |
| **`data/sample/risks.json`** | Live synchronized risk register dataset. |
| **`deploy/`** | Deployment scripts, container definitions, and 1-click shutdown tooling. |

---

## 📞 Support & Contacts

* **Business Owner**: Allison Innes (`allins@google.com`)
* **Technical Lead**: Steve Deacon (`sdeacon@google.com`)
* **Program Lead**: Wayne Davis (`waynedavis@google.com`)
* **Initial Creator**: Brendan Hills (`brendanhills@google.com`)
