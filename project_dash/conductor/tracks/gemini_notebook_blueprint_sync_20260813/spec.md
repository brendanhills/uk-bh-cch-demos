# Specification: Gemini Notebook Ingestion & Contract Blueprint Traceability

## Overview
Ingest project knowledge, design blueprints, contract annexes, and research reports from the **"Project Monaro Contract Notebook"** ([Gemini Notebook `acdbb29b-8632-4fc7-9ba8-2357beeff141`](https://notebook.google.com/notebook/acdbb29b-8632-4fc7-9ba8-2357beeff141)) into the Project Dashboard platform, establishing **bidirectional traceability between risks/issues and their governing contract blueprints**, consolidated under a central `data/` folder and integrated directly into the **"Sync Workspace"** control.

---

## Functional Requirements

### 1. Unified `data/` Directory Structure
Consolidate all project data streams under `data/`:
- `data/notebook/`: Source catalog, project briefings, annex summaries, bundle-to-risk mappings, and verbatim research markdown.
- `data/sheets/`: Risk & issue register (`live_synced_data.json`).
- `data/drive/`: Weekly status report snapshots (`weekly_snapshots.json`).

### 2. Ingestion & Differential Sync Engine (`scripts/sync_notebook.py`)
- Connect to the NotebookLM Partner API (`McpService`) via Stubby with LOAS end-user credentials.
- Perform **differential sync**: Compare remote source modification timestamps with `data/notebook/sources_catalog.json` so unchanged PDF annexes are not re-parsed unnecessarily.
- Extract verbatim text from Markdown/text sources (e.g. *Subcontractor ABN Verification*, *Read Me First*).
- Generate structured contract annex summaries for Bundles A through L (Annexes B, C, D, E, F, G, H, J, K, L).
- Build a relational cross-reference mapping (`bundle_annex_mapping.json`) linking contract clauses and bundles to the 107 risks and 29 issues.

### 3. Backend API Endpoints (`server.py`)
- `GET /api/check-notebook-sync`: Returns current sync status, total sources (17), last synced timestamp, and catalog metadata.
- `POST /api/sync-notebook` & `GET /api/sync-notebook`: Invokes the differential sync worker and returns the updated catalog and mappings.

### 4. Workspace Sync Modal Integration (`index.html`)
- Update the **Google Workspace Live Sync** modal (`#sheetsModal`):
  - Add **"3. Project Knowledge & Contract Blueprints (Gemini Notebook)"** displaying live source count, last synced status, and deep link to NotebookLM.
  - Clicking **"Sync Workspace Now"** synchronizes Sheets, Drive, and the Gemini Notebook in a single unified action.

### 5. Contextual Blueprint Grounding in Risk & Issue Modals
- In the **Item Detail Modal** (`openItemDetailModal`), render a dedicated **"Contract & Blueprint Traceability"** card:
  - Displays the item's governing contract annex (e.g. `📘 Solution Blueprint Annex H (Managed Infrastructure)` for Risk #26).
  - Shows relevant contract clauses and scope context.
  - Provides a 1-click `Open Source in NotebookLM ↗` deep link.

### 6. Dedicated `📚 Blueprint Knowledge` Tab (`#view-blueprints`)
- Add a new tab to the dashboard navigation bar.
- **Bundle & Annex Matrix (A through L)**: Interactive cards for all 10 Solution Blueprints and High-Level Designs, displaying version (`v0.1`, `v0.2`), token volume, scope summary, and **active risk/issue count badges**.
- **1-Click Filtering**: Clicking an annex card filters the risk matrix directly to that bundle's risks.
- **Research & Governance Repository**: Cards for working documents (*Supply Chain Management Plan*, *Subcontractor ABN Verification*).

---

## Acceptance Criteria
- [ ] All 17 sources from NotebookLM are cataloged and structured under `data/notebook/`.
- [ ] Clicking "Sync Workspace Now" in the UI refreshes the notebook catalog alongside Google Sheets and Drive.
- [ ] Opening any risk or issue detail modal displays its governing contract annex and blueprint context.
- [ ] The `📚 Blueprint Knowledge` tab displays the full bundle matrix with accurate live risk counters and filter links.
- [ ] Automated unit and endpoint tests pass.

---

## Out of Scope
- Direct in-browser PDF rendering (users use direct deep-links to NotebookLM / Google Drive).
- Modifying remote NotebookLM sources from the dashboard UI (read/sync ingestion only).
