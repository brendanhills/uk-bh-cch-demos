# Specification: Single Product Tech Stack Integration (React + Vite + Google Sheets Sync)

## 1. Overview & Purpose
This specification defines the migration and unification of `project_dash` onto a **Single Canonical Tech Stack**: **React 18 + TypeScript + Vite + Tailwind CSS + Chart.js** (built from the `dash_v1` prototype). It integrates interactive risk/issue management, in-app editing (`DataEntryTab`), data importing (`ImportDataModal`), and **automated live Google Sheets synchronization directly from Google Drive / URL**.

---

## 2. Key Requirements & Architecture

### 2.1. Single Unified Tech Stack Rationale & Architecture
- **Why This Tech Stack:**
  1. **AI Studio Native Parity:** `dash_v1` is the official export format from Google AI Studio App Builder (`https://aistudio-preprod.corp.google.com/apps/`). Standardizing on React + Vite + Tailwind ensures 100% component and layout parity with AI Studio app drafts.
  2. **Type Safety & Maintainability:** TypeScript enforces strict typing across all 36 spreadsheet attributes in the `RiskTicket` schema (`inherentRiskScore`, `residualRiskScore`, `driverTreeRef`, `governanceLevel`), preventing runtime schema mismatches.
  3. **High-Performance Client Interactivity:** React state + Vite provides instant HMR, zero-latency tab navigation, fluid 5x5 heatmap cell inspection, in-app data editing, and Chart.js rendering without server round-trip latency.
- **Framework & Structure:** React 18, TypeScript 5, Vite, Tailwind CSS. Modular structure under `src/components/` (`RiskMatrix`, `CD1DriverTree`, `IssueRegisterView`, `TrendsTab`, `WholeDataTab`, `DataEntryTab`, `ImportDataModal`).

### 2.2. Automated Google Sheets Synchronization (Drive / Sheet URL)
- **Direct Sheet URL & Drive Integration:** Connects directly to an actual Google Sheet from Google Drive or specified Sheet URL (`https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`).
- **Live Auto-Update & Fetch Service:** Retrieves sheet content dynamically on app launch and on a configurable refresh timer using Google Sheets API / Drive fetch workflows.
- **Column Normalization:** Automatically maps Google Sheet headers to `RiskTicket` schema (`id`, `status`, `riskOwner`, `category`, `inherentLikelihood`, `residualLikelihood`, `driverTreeRef`, etc.).
- **Sync Status Indicator:** Displays real-time status (`Live Sync: Google Sheet Connected 🟢`) with a "Refresh from Google Sheet" manual trigger button.

### 2.3. Feature Set Integration from `dash_v1`
- **5x5 Risk Heatmap Matrix:** Rating toggles (`Inherent` vs `Residual`), status filters (`Open`, `Active`, `Eventuated`, `All`), score calculation (1-25), and extreme top risk cards.
- **CD1 Driver Tree Visualizer:** Hierarchical driver tree navigation linked to specific risks and issues.
- **Issue Register View:** Detailed issue list with severity badges, escalation statuses (IPF/PSG/Internal), and action plans.
- **Performance Trends & Analytics:** Chart.js visualizations for category distribution and risk reduction trajectories.
- **Whole Register Ledger:** 36-column searchable spreadsheet view with CSV download.
- **Data Entry & Import Modal:** In-app forms for adding/editing items and importing external files.

---

## 3. Technology Stack Definition
- **Language:** TypeScript 5+ / JavaScript ES6+
- **Build Tool:** Vite (`vite`)
- **Frontend Framework:** React 18 (`react`, `react-dom`)
- **Styling:** Tailwind CSS (`tailwindcss`, `@tailwindcss/vite`)
- **Icons & Visualization:** Lucide React (`lucide-react`), Chart.js (`chart.js`)

---

## 4. Acceptance Criteria
- [ ] Project standardizes on single tech stack (`React 18 + TypeScript + Vite`) with documented rationale.
- [ ] Application launches cleanly via `npm run dev` or `vite`.
- [ ] Direct integration with live Google Sheet (via Google Drive ID or Sheet URL) auto-populates and updates the risk/issue dataset.
- [ ] All 7 core tabs/views (`Overview`, `Trends`, `Driver Tree`, `Issue Register`, `Whole Ledger`, `Data Entry`, `Import Modal`) operate smoothly.
- [ ] Local data editing and export capabilities function accurately.
