# Implementation Plan: Gemini Notebook Ingestion & Contract Blueprint Traceability

## Phase 1: Central `data/` Consolidation & Data Migration
- [ ] Task: Consolidate data structure into a unified top-level `data/` directory
  - [ ] Create `data/notebook/`, `data/notebook/annexes/`, `data/notebook/research/`, `data/sheets/`, and `data/drive/`
  - [ ] Migrate `src/data/live_synced_data.json` to `data/sheets/live_synced_data.json` (with backward compatibility)
  - [ ] Migrate `src/data/weekly_snapshots.json` to `data/drive/weekly_snapshots.json` (with backward compatibility)
  - [ ] Update `server.py` and `scripts/ingest_weekly_report.py` to point to `data/` paths
- [ ] Task: Phase Verification & Checkpoint (Verify server and data paths)

## Phase 2: Ingestion & Differential Sync Engine (`scripts/sync_notebook.py`)
- [ ] Task: Implement NotebookLM RPC client wrapper
  - [ ] Create `scripts/notebooklm_client.py` wrapping `ListSources`, `ReadSourceContent`, and `GenerateAnswer`
- [ ] Task: Implement differential sync script `scripts/sync_notebook.py`
  - [ ] Implement `list_and_catalog_sources` comparing remote timestamps with `data/notebook/sources_catalog.json`
  - [ ] Implement `extract_verbatim_text` for Markdown/text sources (e.g. Subcontractor ABN Verification, Readme)
  - [ ] Implement `generate_bundle_annex_summaries` mapping Annexes (B, C, D, E, F, G, H, J, K, L) to project bundles
  - [ ] Implement `build_bundle_risk_matrix` to cross-reference the 107 risks and 29 issues with governing contract annexes
  - [ ] Write `data/notebook/bundle_annex_mapping.json` and `data/notebook/project_briefing.json`
- [ ] Task: Write automated test suite for sync and parsing (`tests/test_sync_notebook.py`)
- [ ] Task: Execute baseline ingestion run for Notebook `acdbb29b-8632-4fc7-9ba8-2357beeff141`
- [ ] Task: Phase Verification & Checkpoint (Verify populated `data/notebook/` artifacts)

## Phase 3: Backend API Integration (`server.py`)
- [ ] Task: Implement Notebook Sync API endpoints in `server.py`
  - [ ] Implement `GET /api/check-notebook-sync`: Returns source counts, last sync timestamp, and status
  - [ ] Implement `POST /api/sync-notebook` and `GET /api/sync-notebook`: Invokes `scripts/sync_notebook.py` and returns updated metadata
  - [ ] Update `GET /api/sync-sheet` to bundle notebook sync metadata if requested
- [ ] Task: Write automated endpoint tests (`tests/test_server_endpoints.py`)
- [ ] Task: Phase Verification & Checkpoint (Verify `curl` API responses)

## Phase 4: Frontend UI Integration & "Sync Workspace" Control (`index.html`)
- [ ] Task: Integrate Gemini Notebook into the "Sync Workspace" Modal (`#sheetsModal`)
  - [ ] Add "3. Project Knowledge & Contract Blueprints (Gemini Notebook)" section with source counts, sync status, and direct NotebookLM link
  - [ ] Hook the "Sync Workspace Now" button to execute both Sheet sync and Notebook sync
- [ ] Task: Implement Contextual Blueprint Grounding in Item Detail Modal (`openItemDetailModal`)
  - [ ] Render the "Contract & Blueprint Traceability" card showing the governing annex, relevant clause, and direct deep link for each risk/issue
- [ ] Task: Implement the dedicated `📚 Blueprint Knowledge` Tab (`#view-blueprints`)
  - [ ] Add navigation tab button with badge
  - [ ] Render the interactive Bundle Matrix (Bundles A through L) with active risk/issue count badges
  - [ ] Add 1-click bundle filtering to jump directly to associated risks in the Risk Matrix
  - [ ] Render the Research & Governance repository cards (Subcontractor ABN verification, Supply Chain plan)
- [ ] Task: Phase Verification & Checkpoint (Verify browser UI interactions and visual styling)

## Phase 5: End-to-End System Verification & Polish
- [ ] Task: Comprehensive end-to-end verification
  - [ ] Verify full synchronization flow from the UI modal
  - [ ] Verify bidirectional navigation between risks and blueprint annexes
  - [ ] Verify error handling and offline fallback
- [ ] Task: Phase Verification & Checkpoint (Final Conductor review)
