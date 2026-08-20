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

## 🔄 How to Ingest New Weekly Reports (Interactive User Workflow)

When a new weekly risk register arrives (e.g., Week 28 PDF or updated Google Sheet):

### Method A: Direct from the Dashboard Web UI
1. Drop the new weekly PDF report (e.g. `Weekly Reporting - Week 28.pdf`) into the team's shared Google Drive folder.
2. Open the dashboard in your browser.
3. Click the **"Sync with Google Drive"** button in the header.
4. The browser will detect the new weekly file, invoke Gemini 3.5 Pro to extract risks and generate the executive brief, and update the 5x5 heatmap and trends in real time!

### Method B: Local Python Ingestion Script (Optional CLI)
If you prefer running a command-line script to pre-generate snapshots:
```bash
python3 scripts/ingest_weekly_report.py --file-id "<DRIVE_FILE_ID>" --name "Weekly Reporting - Week 28.pdf"
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
| **`server.py`** | Optional local Python server with Drive sync and ingestion APIs. |
| **`run_server.sh`** | 1-command tmux lifecycle script (start, attach, restart, kill). |
| **`HANDOVER_GUIDE.md`** | This operator manual and team handover guide. |
| **`README.md`** | Comprehensive project overview and architecture documentation. |
| **`TEAM_PRESENTATION_GUIDE.md`** | Presentation guide and demo narrative for stakeholder meetings. |
| **`src/data/weekly_snapshots.json`** | Weekly historical risk register snapshots (Week 22 through Week 27+). |
| **`src/data/live_synced_data.json`** | Live synchronized dataset from Google Sheets. |
| **`deploy/`** | Deployment scripts, container definitions, and 1-click shutdown tooling. |

---

## 📞 Support & Contacts

* **Business Owner**: Allison Innes (`allins@google.com`)
* **Technical Lead**: Steve Deacon (`sdeacon@google.com`)
* **Program Lead**: Wayne Davis (`waynedavis@google.com`)
* **Initial Creator**: Brendan Hills (`brendanhills@google.com`)
