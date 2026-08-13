# Implementation Plan: Team Google Risk Register Integration & Multi-Register Governance

## Phase 1: Data Model, Multi-Register Ingestion & Test Harness
- [ ] Task: Extend Data Schemas & Sample Datasets
  - [ ] Add `teamGoogleRisks` array, register metadata, and source tagging to `src/data/live_synced_data.json`
  - [ ] Populate initial representative Team Google risk items with realistic engineering categories, scores, and mitigations
- [ ] Task: Update Google Sheets Sync Service & API Endpoints
  - [ ] Update `src/utils/googleSheetsService.ts` to support multi-sheet URLs and column aliasing
  - [ ] Update `server.py` `/api/sync-sheet` handler to return multi-register and combined payloads
- [ ] Task: Author Automated Verification Tests (TDD)
  - [ ] Update `tests/test_data_integrity.py` with multi-register schema assertions and source tag validations
  - [ ] Update `tests/test_server.py` to verify `/api/sync-sheet` multi-register payloads and tab existence
  - [ ] Run test suite to establish green baseline
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: UI View Implementation & Interactive Cockpit
- [ ] Task: Tab Navigation Bar Refactoring
  - [ ] Update Tab 2 label to "Joint Program Risks (107)"
  - [ ] Add Tab 3: "Team Google Risks" with live count badge and `switchTab('team-google')` binding
  - [ ] Update URL query parameter handler `checkUrlViewParameters()` to support `?tab=team-google`
- [ ] Task: Implement Dedicated Team Google Risk Cockpit (`#view-team-google`)
  - [ ] Construct HTML view container mirroring `#view-overview` with Team Google branding and Google Sheet link
  - [ ] Implement independent 5×5 Risk Matrix (`renderTeamGoogleHeatmap()`) with Inherent vs. Residual toggles
  - [ ] Implement independent Top 3 KPI cards (Critical Exposure, Eventuated, Unactioned)
  - [ ] Implement interactive Team Google Risk Explorer with search, category filtering, and detail drawers
- [ ] Task: Refactor Executive Summary for Combined Roll-Up
  - [ ] Compute aggregate KPI metrics across Joint Program + Team Google risks
  - [ ] Update Gemini Decision Briefing synthesis with `[Joint Program]` and `[Team Google]` source badges
  - [ ] Merge Top Attention Items and Gap Close Horizon references
- [ ] Task: Update Issue Register, Trends & Ledger with Source Filters
  - [ ] Add source segmented filter (`All Registers` | `Joint Program` | `Team Google`) across secondary views
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Verification, Edge Case Auditing & Documentation
- [ ] Task: Comprehensive Test Suite Verification
  - [ ] Execute `python3 -m unittest tests/test_data_integrity.py`
  - [ ] Execute `python3 -m unittest tests/test_server.py`
- [ ] Task: Manual Visual & UX Verification
  - [ ] Verify 5×5 matrix cell click filters on both Joint Program and Team Google tabs
  - [ ] Test live text search, category dropdowns, and rating toggles
  - [ ] Verify Google Sheet link opens `https://docs.google.com/spreadsheets/d/1lNRf5NEBd6ygc91nNwFA4HWGFfbDK02QkbkVfr4OUoA/edit?gid=0#gid=0`
- [ ] Task: Documentation & Showcase Update
  - [ ] Update `README.md` and `TEAM_PRESENTATION_GUIDE.md`
- [ ] Task: Final Track Verification & Checkpoint (Refer to workflow.md)
