# Implementation Plan: Single Product Tech Stack Integration & Google Sheets Sync

## Phase 1: Tech Stack Migration & Build Setup
- [x] **Task 1.1: Project Environment & Build Configuration**
  - Standardize `project_dash` root on React 18 + TypeScript + Vite + Tailwind CSS (`package.json`, `vite.config.ts`, `tsconfig.json`).
  - Configure `uv` / `npm` scripts for launching dev server (`npm run dev` / `uv run ...`).

## Phase 2: React Component & State Integration
- [x] **Task 2.1: Port `dash_v1` Core Components & Data Structures**
  - Copy and verify `src/types.ts` (36-column `RiskTicket` schema).
  - Port `RiskMatrix.tsx`, `CD1DriverTree.tsx`, `IssueRegisterView.tsx`, `TrendsTab.tsx`, `WholeDataTab.tsx`, `DataEntryTab.tsx`, and `ImportDataModal.tsx`.
- [x] **Task 2.2: Modular View Architecture & Executive Briefing Extension Slot**
  - Wire main navigation bar to switch smoothly between tabs/views.
  - Expose clean React component slot and state hooks for `ExecutiveBriefingView` to seamlessly plug in next.

## Phase 3: Direct Google Sheets (Drive / URL) Integration
- [x] **Task 3.1: Google Sheets Fetch & Parsing Service**
  - Implement Google Sheets URL / Drive Sheet ID reader (`src/utils/googleSheetsService.ts`).
  - Implement automatic header mapping to `RiskTicket` schema.
  - Implement live sync status indicator (`Live Sync: Google Sheet Connected 🟢`) and auto-refresh timer.

## Phase 4: Verification & Final Handshake
- [ ] **Task 4.1: Verification & Checkpoint**
  - Verify `npm run dev` / Vite build launches cleanly.
  - Test live Google Sheets sync, in-app editing, and CSV exports.
