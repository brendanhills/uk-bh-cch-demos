# Implementation Plan: Gemini Notebook Ingestion & Contract Blueprint Traceability

## Phase 1: Central `data/` Consolidation & Data Migration
- [x] Task: Consolidate data structure into a unified top-level `data/` directory
  - [x] Create `data/notebook/`, `data/notebook/annexes/`, `data/notebook/research/`, `data/sheets/`, and `data/drive/`
  - [x] Migrate `src/data/live_synced_data.json` to `data/sheets/live_synced_data.json` (with backward compatibility)
  - [x] Migrate `src/data/weekly_snapshots.json` to `data/drive/weekly_snapshots.json` (with backward compatibility)
  - [x] Update `server.py` and `scripts/ingest_weekly_report.py` to point to `data/` paths
- [x] Task: Phase Verification & Checkpoint (Verify server and data paths)

## Phase 2: Ingestion & Differential Sync Engine (`scripts/sync_notebook.py`)
- [x] Task: Implement NotebookLM RPC client wrapper
  - [x] Create `scripts/notebooklm_client.py` wrapping `ListSources`, `ReadSourceContent`, and `GenerateAnswer`
- [x] Task: Implement differential sync script `scripts/sync_notebook.py`
  - [x] Implement `list_and_catalog_sources` comparing remote timestamps with `data/notebook/sources_catalog.json`
  - [x] Implement `extract_verbatim_text` for Markdown/text sources (e.g. Subcontractor ABN Verification, Readme)
  - [x] Implement `generate_bundle_annex_summaries` mapping Annexes (B, C, D, E, F, G, H, J, K, L) to project bundles
  - [x] Implement `build_bundle_risk_matrix` to cross-reference the 107 risks and 29 issues with governing contract annexes
  - [x] Write `data/notebook/bundle_annex_mapping.json` and `data/notebook/project_briefing.json`
- [x] Task: Write automated test suite for sync and parsing (`tests/test_sync_notebook.py`)
- [x] Task: Execute baseline ingestion run for Notebook `acdbb29b-8632-4fc7-9ba8-2357beeff141`
- [x] Task: Phase Verification & Checkpoint (Verify populated `data/notebook/` artifacts)

## Phase 3: Backend API Integration (`server.py`)
- [x] Task: Implement Notebook Sync API endpoints in `server.py`
  - [x] Implement `GET /api/check-notebook-sync`: Returns source counts, last sync timestamp, and status
  - [x] Implement `POST /api/sync-notebook` and `GET /api/sync-notebook`: Invokes `scripts/sync_notebook.py` and returns updated metadata
  - [x] Update `GET /api/sync-sheet` to bundle notebook sync metadata if requested
- [x] Task: Write automated endpoint tests (`tests/test_server_endpoints.py`)
- [x] Task: Phase Verification & Checkpoint (Verify `curl` API responses)

## Phase 4: Frontend UI Integration & "Sync Workspace" Control (`index.html`)
- [x] Task: Integrate Gemini Notebook into the "Sync Workspace" Modal (`#sheetsModal`)
  - [x] Add "3. Project Knowledge & Contract Blueprints (Gemini Notebook)" section with source counts, sync status, and direct NotebookLM link
  - [x] Hook the "Sync Workspace Now" button to execute both Sheet sync and Notebook sync
- [x] Task: Implement Contextual Blueprint Grounding in Item Detail Modal (`openItemDetailModal`)
  - [x] Render the "Contract & Blueprint Traceability" card showing the governing annex, relevant clause, and direct deep link for each risk/issue
- [x] Task: Implement the dedicated `📚 Blueprint Knowledge` Tab (`#view-blueprints`)
  - [x] Add navigation tab button with badge
  - [x] Render the interactive Bundle Matrix (Bundles A through L) with active risk/issue count badges
  - [x] Add 1-click bundle filtering to jump directly to associated risks in the Risk Matrix
  - [x] Render the Research & Governance repository cards (Subcontractor ABN verification, Supply Chain plan)
- [x] Task: Phase Verification & Checkpoint (Verify browser UI interactions and visual styling)

## Phase 5: End-to-End System Verification & Polish
- [x] Task: Comprehensive end-to-end verification
  - [x] Verify full synchronization flow from the UI modal
  - [x] Verify bidirectional navigation between risks and blueprint annexes
  - [x] Verify error handling and offline fallback
- [x] Task: Phase Verification & Checkpoint (Final Conductor review)
