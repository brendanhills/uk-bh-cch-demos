# Tech Stack Definition: F-DSE Risk Intelligence Platform

## 1. Core Architecture & Strict Invariants
- **Zero GCP Cloud Project Constraint (MANDATORY):**
  - The project operates with **NO Google Cloud Project** (no GCP Project ID, no Cloud Billing, no GCS Buckets, and no Cloud Run services).
  - Argolis projects are demo-only and strictly prohibited for production data.
- **Frontend Architecture:** High-performance, zero-build Single Page Application (`index.html`) using modern JavaScript ES6+, Tailwind CSS, and Chart.js.
- **Runtime Model:** **Zero-Server / Browser-Direct Architecture**. No permanent backend server runs in the cloud; client-side browser directly interacts with Google Drive and Gemini APIs.
- **Local / Cloudtop Runner:** Optional Python 3.11+ server (`server.py`) managed via 1-command tmux lifecycle (`run_server.sh`) on port 9000 for local development and review.

## 2. Data & Storage Layer (Google Drive-Native)
- **Primary Source of Truth:** Google Drive Shared Folder / Workspace Storage (zero GCP bucket overhead).
- **Weekly Ingestion Pipeline:** Google Drive PDF reports (Week 27, 26, 25...) and Google Sheets risk registers.
- **Historical Persistence:** `weekly_snapshots.json` and `live_synced_data.json` stored directly in Google Drive and cached in browser `localStorage` / local JSON.
- **User-Triggered Ingestion:** On-demand sync and PDF extraction triggered directly from the web UI.

## 3. Access Control & User Restriction (Data-Layer Enforced)
- **Data-Layer Access Restriction:** User access restriction is enforced at the **Google Drive / Google Workspace data layer** via Shared Folder permissions tied to the team's Ganpati / Google Groups roster.
- **Access Governance Groups:**
  - `monaro-risk-admin`: Admin and infrastructure ownership group.
  - `monaro-risk-dev` (`monaro-risk-dev@twosync.google.com`): Developer and editor access.
  - `monaro-risk-prod` (`monaro-risk-prod@twosync.google.com`): Executive stakeholder and viewer access (e.g. `allins@google.com`).
- **Access Denial Behavior:** Any user not explicitly granted membership in the Drive Shared Folder / Ganpati roster receives a Google Workspace `403 Permission Denied` error and cannot load snapshots or reports.

## 4. Multi-Notebook Knowledge Base
- **Central Registry:** `data/notebooks/registry.json` supporting multiple Gemini Notebooks (Contracts, Technical Blueprints, Security ATO).
- **UI Switching:** Dynamic dropdown selector in the Contractual Horizon tab.
- **Generalized Sync CLI:** `python3 scripts/sync_notebook.py --notebook-id <UUID> --title "<TITLE>" --slug "<SLUG>"`.

## 5. Turnkey Operations & Handover Tooling
- **Operator Runbook:** `HANDOVER_GUIDE.md` for self-service maintenance by team members (`allins@`, `sdeacon@`, `waynedavis@`).
- **Emergency Lifecycle:** 1-click immediate local service shutdown (`deploy/shutdown.sh` / `deploy/stop.sh`).
