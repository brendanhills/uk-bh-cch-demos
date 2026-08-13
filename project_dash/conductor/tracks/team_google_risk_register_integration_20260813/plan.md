# Implementation Plan: Team Google Risk Register Integration & Multi-Register Governance

## Phase 1: Data Model, Multi-Register Ingestion & Test Harness
- [x] Task: Extend Data Schemas & Sample Datasets
  - [x] Add `teamGoogleRisks` array, register metadata, and source tagging to `src/data/live_synced_data.json`
  - [x] Populate initial representative Team Google risk items with realistic engineering categories, scores, and mitigations
- [x] Task: Update Google Sheets Sync Service & API Endpoints
  - [x] Update `src/utils/googleSheetsService.ts` to support multi-sheet URLs and column aliasing
  - [x] Update `server.py` `/api/sync-sheet` handler to return multi-register and combined payloads
- [x] Task: Author Automated Verification Tests (TDD)
  - [x] Update `tests/test_data_integrity.py` with multi-register schema assertions and source tag validations
  - [x] Update `tests/test_server.py` to verify `/api/sync-sheet` multi-register payloads and tab existence
  - [x] Run test suite to establish green baseline
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: UI View Implementation & Interactive Cockpit
- [x] Task: Tab Navigation Bar Refactoring
  - [x] Update Tab 2 label to "Joint Program Risks (107)"
  - [x] Add Tab 3: "Team Google Risks" with live count badge and `switchTab('team-google')` binding
  - [x] Update URL query parameter handler `checkUrlViewParameters()` to support `?tab=team-google`
- [x] Task: Implement Dedicated Team Google Risk Cockpit (`#view-team-google`)
  - [x] Construct HTML view container mirroring `#view-overview` with Team Google branding and Google Sheet link
  - [x] Implement independent 5×5 Risk Matrix (`renderTeamGoogleHeatmap()`) with Inherent vs. Residual toggles
  - [x] Implement independent Top 3 KPI cards (Critical Exposure, Eventuated, Unactioned)
  - [x] Implement interactive Team Google Risk Explorer with search, category filtering, and detail drawers
- [x] Task: Refactor Executive Summary for Combined Roll-Up
  - [x] Compute aggregate KPI metrics across Joint Program + Team Google risks
  - [x] Update Gemini Decision Briefing synthesis with `[Joint Program]` and `[Team Google]` source badges
  - [x] Merge Top Attention Items and Gap Close Horizon references
- [x] Task: Update Issue Register, Trends & Ledger with Source Filters
  - [x] Add source segmented filter (`All Registers` | `Joint Program` | `Team Google`) across secondary views
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Verification, Edge Case Auditing & Documentation
- [x] Task: Comprehensive Test Suite Verification
  - [x] Execute `python3 -m unittest tests/test_data_integrity.py`
  - [x] Execute `python3 -m unittest tests/test_server.py`
- [x] Task: Manual Visual & UX Verification
  - [x] Verify 5×5 matrix cell click filters on both Joint Program and Team Google tabs
  - [x] Test live text search, category dropdowns, and rating toggles
  - [x] Verify Google Sheet link opens `https://docs.google.com/spreadsheets/d/1lNRf5NEBd6ygc91nNwFA4HWGFfbDK02QkbkVfr4OUoA/edit?gid=0#gid=0`
- [x] Task: Documentation & Showcase Update
  - [x] Update `README.md` and `TEAM_PRESENTATION_GUIDE.md`
- [x] Task: Final Track Verification & Checkpoint (Refer to workflow.md)
