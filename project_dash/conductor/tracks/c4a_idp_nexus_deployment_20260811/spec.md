# Specification: Production Deployment, Drive-Native Storage & Turnkey Handover

## 1. Overview
Deploy the **F-DSE Program Governance & Risk Intelligence Platform** using Google Drive as the Single Source of Truth for storage and ingestion, enforce strict Google SSO access control via Ganpati/TwoSync groups, and deliver a comprehensive Turnkey Handover Package (`HANDOVER_GUIDE.md`) enabling immediate, self-service operation by the project team (`allins@`, `sdeacon@`, `waynedavis@`).

## 2. Functional Requirements
- **Google Drive Storage Backend**: All weekly PDF risk reports, Google Sheets registers, and `weekly_snapshots.json` persist directly in the team's shared Google Drive folder, eliminating any GCP Cloud Storage bucket dependencies.
- **Interactive User-Triggered Ingestion**: Dashboard users can trigger Google Drive synchronization, weekly PDF ingestion, and Gemini 3.5 Pro executive synthesis directly from the web UI.
- **Strict Access Control (Google SSO & TwoSync)**: Restrict access exclusively to authorized Ganpati Prod groups:
  - `monaro-risk-prod` (Executive stakeholders and viewers, e.g. `allins@google.com`)
  - `monaro-risk-dev` (Developers, engineers, editors)
  - `monaro-risk-admin` (Admins and technical leads)
- **Turnkey Handover Package (`HANDOVER_GUIDE.md`)**: Complete, zero-tribal-knowledge operational manual covering architecture, daily operations, Ganpati user management, 1-command startup, deployment, and emergency shutdown.
- **Corporate Environment Guardrails**: Strict prohibition of Argolis sandboxes (`altostrat.com`) for production workloads.

## 3. Non-Functional & Operational Requirements
- **Zero Ongoing Maintenance for Creator**: Turnkey documentation and automated tooling allow the receiving team to maintain and update the platform independently.
- **High Performance & Sub-Millisecond Switching**: High-speed vanilla HTML5/JS single-page architecture (`index.html`) with embedded audio briefing player.
- **Operational Safety**: 1-click immediate shutdown script (`./deploy/shutdown.sh`).

## 4. Acceptance Criteria
- [ ] Google Drive storage and ingestion pipeline verified in `server.py`.
- [ ] User-triggered Drive sync and report ingestion tested and functional.
- [ ] Ganpati groups documented and synced via TwoSync.
- [ ] Comprehensive `HANDOVER_GUIDE.md` created and validated.
- [ ] Project tech specs (`tech-stack.md` and `product.md`) updated.
- [ ] All code, scripts, and documentation committed and pushed to repository.
