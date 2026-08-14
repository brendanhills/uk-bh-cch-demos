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
6. **Multi-Register Governance Cockpit**:
   - **Combined Executive Summary**: Unified leadership synthesis aggregating Joint Program and Team Google risks.
   - **Joint Program Risks (107)**: Dedicated 5×5 matrix for overarching multi-party delivery obligations (Accenture/Google/Cth).
   - **Team Google Risks**: Dedicated 5×5 cockpit for Google-internal engineering tasks, GDC air-gap infrastructure, and mitigations.
8. **Generalized Multi-Notebook Knowledge Base**:
   - Central Registry (`data/notebooks/registry.json`) supporting multiple Gemini Notebooks (Contracts, Technical Blueprints, Security ATO).
   - Dynamic UI dropdown selector in the Contractual Delivery / Annexes tab to switch between notebook sources seamlessly.
   - Generalized sync CLI: `python3 scripts/sync_notebook.py --notebook-id <UUID> --title "<TITLE>" --slug "<SLUG>"`.

7. **Gemini Notebook & Contract Blueprint Knowledge Base**:
   - Ingests **Project Monaro Contract Notebook** (`acdbb29b-8632-4fc7-9ba8-2357beeff141`, 17 sources).
   - Bidirectional contract traceability mapping Bundles A through L / Annexes B through L directly to risks and issues.
   - Differential sync engine and 1-click Workspace Sync (`/api/sync-notebook`).

---

## 👥 Access Control & Ganpati (MDB) Groups

Authentication and access control are governed through Google-native **Ganpati (MDB)** Prod groups synced to Google Cloud via **TwoSync**:

| Group Name | Ganpati Namespace / Type | TwoSync Identity (GCP IAM) | Purpose & Target Audience |
| :--- | :--- | :--- | :--- |
| **`monaro-risk-admin`** | `prod` / `ADMIN` | `monaro-risk-admin@twosync.google.com` | **Admin / Ownership Group**: Administers access rules and owns the dev/prod team groups. Self-owned by technical leads. |
| **`monaro-risk-dev`** | `prod` / `TEAM` | `monaro-risk-dev@twosync.google.com` | **Development & Engineering**: Engineers and data developers who can deploy updates and access dev/staging builds. |
| **`monaro-risk-prod`** | `prod` / `TEAM` | `monaro-risk-prod@twosync.google.com` | **Production Stakeholders & Viewers**: Executive stakeholders (e.g. `allins@google.com`), PMs, and cross-functional governance viewers. |

### Adding Members to Groups
1. Open the group in Ganpati:
   - **Admin**: [https://ganpati2.corp.google.com/group/%25monaro-risk-admin.prod](https://ganpati2.corp.google.com/group/%25monaro-risk-admin.prod)
   - **Dev**: [https://ganpati2.corp.google.com/group/%25monaro-risk-dev.prod](https://ganpati2.corp.google.com/group/%25monaro-risk-dev.prod)
   - **Prod (Viewers)**: [https://ganpati2.corp.google.com/group/%25monaro-risk-prod.prod](https://ganpati2.corp.google.com/group/%25monaro-risk-prod.prod)
2. Navigate to the **Children** tab $\rightarrow$ click **Propose New Children**.
3. Add the individual Googler LDAPs (members can be from any team or organization across Google).
4. Submitting the proposal automatically approves it (since `monaro-risk-admin` owns the groups).

### TwoSync Registration
To sync Ganpati groups to GCP IAM rosters (`*@twosync.google.com`), run:
```bash
/google/src/head/depot/google3/security/twosync/tools/register.sh --group monaro-risk-dev
/google/src/head/depot/google3/security/twosync/tools/register.sh --group monaro-risk-prod
```

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

The platform includes a secured, private deployment pipeline to Google Cloud Run configured via `.env` with explicit Dashboard Viewer and Admin access controls, domain security, and immediate shutdown capabilities:

### 1. Configure Role-Based Access in `.env`
Copy `.env.example` to `.env` and configure your authorized viewers and admins:
```bash
# --- Dashboard Viewers (Can view dashboard via Google SSO) ---
DASHBOARD_VIEWER_GROUPS="monaro-risk-prod@twosync.google.com"
DASHBOARD_VIEWER_USERS="brendanhills@google.com,allins@google.com"

# --- Dashboard Admins / Editors (Can deploy updates and manage revisions) ---
DASHBOARD_ADMIN_GROUPS="monaro-risk-dev@twosync.google.com"
DASHBOARD_ADMIN_USERS="brendanhills@google.com"

# --- Security & Domain Restrictions ---
BLOCKED_DOMAINS="altostrat.com"
```

### 2. Deploy to Cloud Run
```bash
# 1-Click deploy using settings from .env
./deploy/deploy_gcp.sh

# Or optionally override/add viewers or admins via CLI flags
./deploy/deploy_gcp.sh \
  --viewer-group "monaro-risk-prod@twosync.google.com" \
  --admin-group "monaro-risk-dev@twosync.google.com"
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

---

## 🛡️ Architecture Guardrails & Engineering Best Practices

To maintain data integrity, eliminate UI breakages, and uphold production-grade reliability across single-page applications and multi-register governance platforms:

### 1. Mandatory AST/Syntax Validation for Inline Web App Scripts
* **Rule**: Whenever modifying JavaScript inside `.html` or single-file SPA templates:
  1. Extract inline script blocks and execute `node -c <script_file.js>` to verify zero unescaped template quotes or syntax anomalies (`SyntaxError: Unexpected string`).
  2. Execute a simulated DOM runtime execution test to confirm global functions (`switchTab`, `initApp`, `renderExecBriefing`) initialize without runtime exceptions before declaring task completion.

### 2. Search & Heatmap Drill-Down Filter State Isolation
* **Rule**: When interacting with targeted analytical widgets (e.g., clicking a 5×5 Risk Heatmap cell or Blueprint Bundle badge):
  - Isolate the filter state by automatically clearing conflicting free-form search text (`explorerSearchInput.value = ''`) and overlapping category dropdowns.
  - This prevents accidental `AND` filter collisions that cause false "0 results" empty states.

### 3. Multi-Register Governance Separation Standard
* **Rule**: When hosting internal vendor workstreams (e.g., *Team Google Delivery Tasks*) alongside multi-party consortium governance (e.g., *Joint Program Risk Register*):
  - Maintain clean data tagging and isolation in memory.
  - Provide dedicated cockpit views with distinct visual branding (e.g., Google Blue theme vs. Joint Slate theme).
  - Dynamically roll up multi-register totals in Executive Decision Briefings with clear source pill badges.
  - Unify all sync pipelines into a single-pane-of-glass Live Sync Hub.
