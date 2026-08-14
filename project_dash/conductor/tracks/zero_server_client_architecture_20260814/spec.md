# Specification: Zero-Server Client-Only Architecture, Drive-Native Storage & Multi-Notebook Registry

## 1. Overview
Transition the **F-DSE Program Governance & Risk Intelligence Platform** into a pure **Zero-Server, Client-Only Web Application** with **Google Drive-Native Storage** and a **Generalized Multi-Notebook Knowledge Base**. This eliminates all cloud backend server maintenance, enables interactive user-triggered ingestion directly in the browser, supports multiple Gemini Notebooks, and delivers an immediate Turnkey Handover package (`HANDOVER_GUIDE.md`) for the team (`allins@`, `sdeacon@`, `waynedavis@`).

## 2. Functional Requirements
- **Zero-Server Runtime**: Pure static SPA (`index.html`) running entirely in the user's browser. No cloud VMs, Borg jobs, or Cloud Run containers required 24/7.
- **Drive-Native Central Storage**: Google Drive Shared Folder serves as the single source of truth for all weekly PDF reports and `weekly_snapshots.json`, guaranteeing 100% consistent data across all users without data drift.
- **Client-Side Live Ingestion**: Users can trigger Google Drive sync, weekly report ingestion, and Gemini 3.5 Pro synthesis directly from the browser UI.
- **Multi-Notebook Registry**:
  - `data/notebooks/registry.json` allows registering multiple Gemini Notebooks (Contracts, Technical Blueprints, Security ATO).
  - Dynamic UI dropdown in the Contractual Delivery / Annexes tab to switch between notebook sources and token breakdowns seamlessly.
  - Generalized sync CLI: `python3 scripts/sync_notebook.py --notebook-id <UUID> --title "<TITLE>" --slug "<SLUG>"`.
- **Turnkey Handover Package**: Self-contained `HANDOVER_GUIDE.md` covering daily operations, Ganpati group management, 1-command startup, and emergency shutdown.

## 3. Non-Functional & Security Requirements
- **Zero Infrastructure Maintenance**: No server crashes, on-call burdens, or cloud storage billing.
- **Google Corporate SSO**: Access governed by Ganpati Prod groups (`monaro-risk-prod` for viewers, `monaro-risk-dev` for editors, `monaro-risk-admin` for admins).
- **Sub-Millisecond UI Performance**: High-speed vanilla JS single-file architecture with zero client-side build steps.

## 4. Acceptance Criteria
- [ ] Multi-Notebook Registry implemented (`data/notebooks/registry.json`) with generalized sync script.
- [ ] UI updated with interactive Notebook Selector dropdown.
- [ ] Client-side Drive sync and ingestion workflow verified.
- [ ] Complete `HANDOVER_GUIDE.md` published and verified.
- [ ] Conductor registry and project tech specs updated.
- [ ] All code committed and pushed to remote `dev`.
