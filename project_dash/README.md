# F-DSE Program Governance & Risk Intelligence Platform

Interactive Executive Cockpit and Risk Intelligence Platform built for the **Future Data Science Environment (F-DSE)** governance lifecycle.

---

## 🌟 Key Architecture & Capabilities

1. **Single Product Vanilla Architecture**:
   - High-performance, zero-build single-file SPA (`index.html`) using Tailwind CSS and Chart.js.
   - Sub-millisecond tab switching and native browser history (`pushState` / `popstate`).
2. **Executive Decision Briefing (Gemini 3.5 Pro)**:
   - Exception-first synthesis highlighting Top 3 Critical Action items, Early Warning Sleeper Outlier (`Ref 1.15`), and schedule squeeze alerts.
   - Neural Australian Audio Briefing (`en-AU-Neural2-A` & `B`) with speed controls, animated waveform, and direct download.
3. **Interactive 5×5 Risk Heatmap & Issue Cockpit**:
   - Dynamic Inherent vs. Residual matrix toggling, active focus rings, and granular 1-click citation jumps (`↗`).
4. **Performance Trends & Velocity**:
   - Dynamic Burndown and Risk Cause Category distribution with `Weekly`, `Bi-Weekly`, and `Monthly` granularity.
5. **Contractual Delivery & Gap Close Horizon**:
   - CD1 Driver Tree linking Level 2 Contractual Milestones to high-priority remediation plans.
6. **Live Google Drive & Sheets Sync API**:
   - Local Python server (`server.py`) handling real-time Google Sheets sync, weekly PDF report ingestion, and Time Machine historical snapshots.

---

## 🚀 Local Quickstart

```bash
# 1-Command Server Lifecycle & Tmux Management
./run_server.sh           # Creates tmux session if missing, starts/restarts server, attaches
./run_server.sh status    # Check live session and server port status
./run_server.sh restart   # Restart server in tmux session
./run_server.sh kill      # Stop server and kill tmux session

# Open in browser
http://localhost:9000
```

---

## 🔒 Cloud Deployment & Operations Pipeline

The platform includes a secured, private deployment pipeline to Google Cloud Run (**`uk-bh-experiments-argolis`**) configured via `.env` with distinct **Dashboard Viewer** and **Dashboard Admin/Editor** IAM access controls, domain security, and immediate shutdown capabilities:

### 1. Configure Role-Based Access in `.env`
Copy `.env.example` to `.env` and configure your authorized viewers and admins:
```bash
# --- Dashboard Viewers (Can view dashboard via Google SSO) ---
DASHBOARD_VIEWER_GROUPS="f-dse-governance-team@google.com"
DASHBOARD_VIEWER_USERS="brendanhills@google.com,colleague1@google.com"

# --- Dashboard Admins / Editors (Can deploy updates and manage revisions) ---
DASHBOARD_ADMIN_GROUPS="f-dse-lead-team@google.com"
DASHBOARD_ADMIN_USERS="brendanhills@google.com,techlead@google.com"

# --- Security & Domain Restrictions ---
BLOCKED_DOMAINS="altostrat.com"
```

### 2. Deploy to Private Cloud Run
```bash
# 1-Click deploy using settings from .env
./deploy/deploy_gcp.sh

# Or optionally override/add viewers or admins via CLI flags
./deploy/deploy_gcp.sh \
  --viewer-group "extra-viewers@google.com" \
  --admin-user "lead-dev@google.com"
```

### 3. Check Live Status & Role Policies
```bash
# Check if the service is online, its URL, and current Viewer and Admin bindings
./deploy/deploy_gcp.sh --status
```

### 4. Immediate Service Shutdown (Stop Server)
Whenever you need to immediately stop the service and take the dashboard offline (like `sudo shutdown -h now`):
```bash
# 1-Click Service Shutdown
./deploy/shutdown.sh

# Or using the alias / flag
./deploy/stop.sh
./deploy/deploy_gcp.sh --stop
```

### 5. Domain Blocking & Security Rules
* **Strict Least Privilege**: Deployed with `--no-allow-unauthenticated` so only explicitly authorized Viewers and Admins can invoke or manage the service.
* **Domain Blocking**: Domains such as `altostrat.com` are strictly forbidden and blocked by pre-flight validation.

---

## 📁 Repository Layout

```
project_dash/
├── .env.example                # Environment template (Gemini API, deployment & role allowlists)
├── index.html                  # Core Single-Page Application (HTML5 / Tailwind / Chart.js)
├── server.py                   # Python server with Drive sync and ingestion APIs
├── run_server.sh               # 1-Command tmux server manager (start, attach, restart, kill)
├── deploy/                     # Cloud deployment & shutdown operations
│   ├── deploy_gcp.sh           # Private Cloud Run deployment with Viewer/Admin IAM & security
│   ├── shutdown.sh / stop.sh   # Immediate service shutdown script
│   ├── deploy_c4a.py           # C4A Starter prototype pipeline
│   ├── README.md               # Detailed deployment operations guide
│   ├── Dockerfile              # Production Nginx container image
│   └── nginx.conf              # Cloud Run Nginx configuration (port 8080)
├── README.md                   # Project documentation
├── TEAM_PRESENTATION_GUIDE.md  # Rolling team showcase narrative, delta notes & demo scripts
├── assets/                     # Audio assets (podcast_w26.mp3, podcast_w26.wav)
├── prompts/                    # Gemini prompt templates (exec_summary_prompt.md)
├── scripts/                    # Ingestion & report processing utilities (ingest_weekly_report.py)
├── src/data/                   # Weekly snapshots and live sync data
├── tests/                      # Automated unit and regression test suite
├── archive/                    # Archived Streamlit prototype files
├── dash_v1/                    # Reference React/Vite v1 prototype
└── conductor/                  # Conductor SDD tracks, specs, and implementation plans
```

---

## 📢 Team Showcase & Feedback

For weekly project team walkthroughs, showcase scripts, and delta updates, refer to [`TEAM_PRESENTATION_GUIDE.md`](./TEAM_PRESENTATION_GUIDE.md).
