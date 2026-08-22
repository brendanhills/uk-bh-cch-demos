# Implementation Plan: Simplify & Harden Platform for Turnkey Handover

## Phase 1: Consolidated Unified Pipeline Engine (`scripts/pipeline.py`)
- [x] Task: Author automated unit tests in `tests/test_pipeline.py` (TDD)
  - [x] Test flexible week & date extraction from non-standard filenames (`Week 29.pdf`, `W29_Deck.pdf`, `Status_Report.pdf`)
  - [x] Test graceful fallback when Gemini API key is missing/unauthenticated
  - [x] Test multi-project snapshot creation and metric computation
- [x] Task: Implement `scripts/pipeline.py`
  - [x] Consolidate Sheets reading, Drive report parsing, and Gemini synthesis into a single entrypoint
  - [x] Add CLI interface with `--sync`, `--ingest-report`, and `--regenerate-briefing` flags
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Server API Rationalization & REST Consolidation (`server.py`)
- [x] Task: Author unit tests in `tests/test_server_rationalized.py`
  - [x] Test `GET /api/status` returns unified health across Sheets, Drive, Notebooks
  - [x] Test `POST /api/sync` executes multi-stream sync
  - [x] Test `POST /api/ingest` and `POST /api/briefing/generate`
  - [x] Test backward compatibility for legacy endpoint aliases
- [x] Task: Refactor `server.py` Request Handlers
  - [x] Implement consolidated REST handlers (`handle_status`, `handle_sync`, `handle_ingest`, `handle_briefing`)
  - [x] Delegate core logic directly to `scripts.pipeline`
  - [x] Maintain alias mapping for legacy endpoints (`/api/sync-sheet`, `/api/check-drive-sync`, etc.)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Frontend Client Integration & Resilient Error UX
- [x] Task: Update `src/js/app.js` and `index.html`
  - [x] Connect Workspace Sync modal to `/api/status` and `/api/sync`
  - [x] Ensure toast messages surface human-readable status and clear error feedback
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Full System Verification & Handover Documentation Polish
- [x] Task: Run full test suite (`python3 -m pytest tests/`) and verify 100% pass rate
- [x] Task: Update `docs/HANDOVER_GUIDE.md` with step-by-step non-technical operator manual
- [x] Task: Update Bug Registry: close Bug #79 as resolved
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)
