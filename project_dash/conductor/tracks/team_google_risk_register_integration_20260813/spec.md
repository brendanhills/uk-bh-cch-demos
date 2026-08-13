# Specification: Team Google Risk Register Integration & Multi-Register Governance

## 1. Overview & Strategic Intent
Integrate the **Team Google Risk Register** ([Google Sheet `1lNRf5NEBd6ygc91nNwFA4HWGFfbDK02QkbkVfr4OUoA`](https://docs.google.com/spreadsheets/d/1lNRf5NEBd6ygc91nNwFA4HWGFfbDK02QkbkVfr4OUoA/edit?gid=0#gid=0)) into the F-DSE Program Governance & Risk Intelligence Platform. This track establishes a multi-register governance architecture that preserves separation between the **Joint Program Register** (cross-team Accenture/Google/Cth governance, 107 risks) and the **Team Google Register** (internal Google engineering tasks and mitigations), while providing a unified executive synthesis.

## 2. Functional Requirements

### 2.1 Tab Navigation & Layout
1. **Executive Summary Tab (`exec-briefing`)**:
   - Combined roll-up displaying aggregate metrics across both registers (total risks, critical severity 18-25 score count, active/closed breakdown).
   - Gemini Decision Briefing synthesizing cross-register priorities with explicit source pills (`[Joint Program]` vs `[Team Google]`).
   - Top 3 Critical Attention Items and Gap Close Horizon tagged by register source.
2. **Joint Program Risks Tab (`overview`)**:
   - Preserved dedicated tab for the 107 Joint Program risks with 5×5 Matrix (Inherent vs Residual), status filters, and Risk Explorer.
3. **Team Google Risks Tab (`team-google`)**:
   - New dedicated tab mirroring the core cockpit architecture:
     - Independent 5×5 Heatmap Matrix with Inherent vs. Residual toggle.
     - Top 3 KPI cards (Critical Exposure 18-25, Active/Closed counts, Unactioned Risks).
     - Interactive Risk Explorer with live text search, category dropdown, score band filters, and expandable drawer.
     - Direct Google Sheet link button (`↗ Open Team Google Sheet`).
4. **Issue Register, Performance Trends & Whole Ledger**:
   - Filter pill (`All Registers` | `Joint Program` | `Team Google`) for targeted cross-register analysis.

### 2.2 Data Ingestion & Google Sheets Sync
1. **Multi-Register Data Store (`src/data/live_synced_data.json`)**:
   - Structured store maintaining `risks` (Joint Program), `teamGoogleRisks` (Team Google), and `issues`.
   - Unified source labeling and collision-proof namespace identifiers.
2. **Backend Sync API (`server.py`)**:
   - `/api/sync-sheet` endpoint supporting multi-register ingestion with `?target=all` or `?target=teamGoogle`.
   - Integration with Google Sheets service adapter (`src/utils/googleSheetsService.ts`) for column aliasing.

## 3. Non-Functional Requirements & Acceptance Criteria
- **Zero Empty States**: All 5×5 heatmap cells, explorer lists, and KPI cards must render valid numbers and cards without undefined errors.
- **Deep-Linking**: Direct URL parameter support (`?tab=team-google` and `?register=teamGoogle`) to open the dedicated view.
- **Automated Test Coverage**: 100% pass rate on `tests/test_data_integrity.py` and `tests/test_server.py`.
