# Implementation Plan: Simplify & Harden Platform for Turnkey Handover

## Phase 1: Consolidated Unified Pipeline Engine (`scripts/pipeline.py`)
- [ ] Task: Author automated unit tests in `tests/test_pipeline.py` (TDD)
  - [ ] Test flexible week & date extraction from non-standard filenames (`Week 29.pdf`, `W29_Deck.pdf`, `Status_Report.pdf`)
  - [ ] Test graceful fallback when Gemini API key is missing/unauthenticated
  - [ ] Test multi-project snapshot creation and metric computation
- [ ] Task: Implement `scripts/pipeline.py`
  - [ ] Consolidate Sheets reading, Drive report parsing, and Gemini synthesis into a single entrypoint
  - [ ] Add CLI interface with `--sync`, `--ingest-report`, and `--regenerate-briefing` flags
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Server API Rationalization & REST Consolidation (`server.py`)
- [ ] Task: Author unit tests in `tests/test_server_rationalized.py`
  - [ ] Test `GET /api/status` returns unified health across Sheets, Drive, Notebooks
  - [ ] Test `POST /api/sync` executes multi-stream sync
  - [ ] Test `POST /api/ingest` and `POST /api/briefing/generate`
  - [ ] Test backward compatibility for legacy endpoint aliases
- [ ] Task: Refactor `server.py` Request Handlers
  - [ ] Implement consolidated REST handlers (`handle_status`, `handle_sync`, `handle_ingest`, `handle_briefing`)
  - [ ] Delegate core logic directly to `scripts.pipeline`
  - [ ] Maintain alias mapping for legacy endpoints (`/api/sync-sheet`, `/api/check-drive-sync`, etc.)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Frontend Client Integration & Resilient Error UX
- [ ] Task: Update `src/js/app.js` and `index.html`
  - [ ] Connect Workspace Sync modal to `/api/status` and `/api/sync`
  - [ ] Ensure toast messages surface human-readable status and clear error feedback
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Full System Verification & Handover Documentation Polish
- [ ] Task: Run full test suite (`python3 -m pytest tests/`) and verify 100% pass rate
- [ ] Task: Update `docs/HANDOVER_GUIDE.md` with step-by-step non-technical operator manual
- [ ] Task: Update Bug Registry: close Bug #79 as resolved
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
