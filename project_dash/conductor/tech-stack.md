# Tech Stack Definition: F-DSE Risk Intelligence Platform

## 1. Primary Architecture & Hosting
- **Frontend Architecture:** High-performance, zero-build Single Page Application (`index.html`) using modern JavaScript ES6+, Tailwind CSS, and Chart.js.
- **Runtime Model:** **Zero-Server / Browser-Direct Architecture**. No permanent backend server runs in the cloud; client-side browser orchestrates Google Drive and Gemini APIs.
- **Local / Cloudtop Runner:** Optional Python 3.11+ server (`server.py`) managed via 1-command tmux lifecycle (`run_server.sh`) on port 9000.

## 2. Data & Storage Layer (Google Drive-Native)
- **Primary Source of Truth:** Google Drive Shared Folder / Workspace Storage (zero GCP bucket overhead).
- **Weekly Ingestion Pipeline:** Google Drive PDF reports (Week 27, 26, 25...) and Google Sheets risk registers.
- **Historical Persistence:** `weekly_snapshots.json` and `live_synced_data.json` stored in Google Drive and cached in browser `localStorage` / local JSON.
- **User-Triggered Ingestion:** On-demand sync and PDF extraction triggered directly from the web UI.

## 3. AI & Intelligence Layer
- **Executive Synthesis Engine:** Google Gemini 3.5 Pro API (`@google/genai` / Python SDK) generating 3-tier exception-first executive briefings.
- **Neural Audio Engine:** Australian Neural2 Voice synthesis (`en-AU-Neural2-A` & `B`) with animated waveform playback.
- **Contract Analysis:** Google Gemini Notebook integration (`notebook.google.com`) mapping contractual annexes to delivery drivers.

## 4. Access Control & Security
- **Authentication:** Google Single Sign-On (SSO) enforced via Corporate UberProxy / Google Workspace.
- **Ganpati Access Groups:**
  - `monaro-risk-admin`: Admin and infrastructure ownership group.
  - `monaro-risk-dev` (`monaro-risk-dev@twosync.google.com`): Developer and editor access.
  - `monaro-risk-prod` (`monaro-risk-prod@twosync.google.com`): Executive stakeholder and viewer access (e.g. `allins@google.com`).
- **Domain Guardrails:** Strict exclusion of unauthorized domains (`altostrat.com`). Argolis sandboxes are strictly prohibited for production.

## 5. Turnkey Operations & Handover Tooling
- **Operator Runbook:** `HANDOVER_GUIDE.md` for self-service maintenance by team members (`allins@`, `sdeacon@`, `waynedavis@`).
- **Emergency Lifecycle:** 1-click immediate service shutdown (`deploy/shutdown.sh` / `deploy/stop.sh`).
