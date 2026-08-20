# Tech Stack Definition: F-DSE Risk Intelligence Platform

## 1. Core Architecture & Strict Invariants
- **Automated Cloud Run Deployment with IAP Google SSO:**
  - Automated CI/CD deployment via **Google Cloud Build** triggers on push to `dev` (scoped to `project_dash/**`).
  - Containerized deployment to **Google Cloud Run** secured behind **Identity-Aware Proxy (IAP)** with `--no-allow-unauthenticated`.
  - Seamless corporate Google SSO authorization tied to Google Groups (`monaro-risk-dev@google.com` / `monaro-risk-prod@google.com`).
- **Frontend Architecture:** High-performance, decoupled Single Page Application (`index.html`) using modern JavaScript ES6+, Tailwind CSS, and Chart.js.
- **Runtime Model:** Lightweight containerized Python/Nginx server (`server.py`) serving the client-side SPA, project data files, and on-demand sync APIs.
- **Local / Cloudtop Runner:** Local Python 3.11+ server managed via 1-command tmux lifecycle (`run_server.sh`) on port 9000 for development and review.

## 2. Data & Storage Layer (Google Drive-Native)
- **Primary Source of Truth:** Google Drive Shared Folder / Workspace Storage (zero GCP bucket overhead).
- **Weekly Ingestion Pipeline:** Google Drive PDF reports (Week 27, 26, 25...) and Google Sheets risk registers.
- **Historical Persistence:** `weekly_snapshots.json` and `live_synced_data.json` stored directly in Google Drive and cached in browser `localStorage` / local JSON.
- **User-Triggered Ingestion:** On-demand sync and PDF extraction triggered directly from the web UI.

## 3. Access Control & Governance (Multi-Tier Architecture)
- **Identity-Aware Proxy (IAP) Web Access Layer (Primary User Interface):**
  - Web application access is secured by Google Cloud IAP, requiring corporate Google SSO.
  - Access is granted directly to **Google Groups**:
    - `monaro-risk-dev@google.com`: Development and operator access.
    - `monaro-risk-prod@google.com`: Executive stakeholder and viewer access (e.g. `allins@google.com`).
  - Day-to-day user onboarding/offboarding is handled via the standard [Google Groups UI](https://groups.google.com/a/google.com/g/monaro-risk-dev), instantly granting or revoking IAP access without requiring GCP IAM modifications.
- **Corporate Infrastructure & TwoSync Synchronization Layer:**
  - **Ganpati (MDB) Prod Groups** (`%monaro-risk-admin.prod`, `%monaro-risk-dev.prod`, `%monaro-risk-prod.prod`) govern Nexus GCP project ownership, Cloud Build permissions, and service accounts.
  - **TwoSync** bridges internal Ganpati MDB rosters to Google Groups (`@twosync.google.com` / `@google.com`).
- **Data-Layer Permissions (Google Drive & Sheets):**
  - Team Google Sheets and Drive Shared Folders inherit group-level access rosters. Users outside the authorized groups receive standard `403 Permission Denied` errors.

## 4. Multi-Notebook Knowledge Base & Ingestion
- **Knowledge Catalog:** Project blueprints and contract deliverables are stored in `data/<project-slug>/knowledge.json` (e.g. Technical Architecture, Security ATO, Contractual SOWs).
- **Unified Ingestion:** Knowledge entries and contractual driver trees are processed and organized alongside risks and issues via the master CLI:
  `python3 scripts/ingest_data.py --project=<project-slug>`
- **Optional Helper CLI (`sync_notebook.py`):** Standalone differential sync script available for direct Notebook ID fetching if needed, though primary workflows use `ingest_data.py`.

## 5. Turnkey Operations & Handover Tooling
- **Operator Runbook:** `docs/HANDOVER_GUIDE.md` for self-service maintenance by team members (`allins@`, `sdeacon@`, `waynedavis@`).
- **Emergency Lifecycle:** 1-click immediate local service shutdown (`deploy/shutdown.sh` / `deploy/stop.sh`).
