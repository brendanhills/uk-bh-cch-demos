# Specification: Dynamic Data Generation & Visualization Audit across All Tabs

## 1. Overview & Strategic Intent
Conduct a comprehensive audit and refactor across all 6 dashboard views in `project_dash` to ensure that every single chart, graph, KPI card, list, table, and header indicator is 100% dynamically bound to live in-memory datasets (`LIVE_RISKS`, `LIVE_ISSUES`, `DRIVER_TREE_ITEMS`, `TIME_MACHINE_SNAPSHOTS`, `DRIVE_REPORTS`) with zero empty states or hardcoded fallback values.

## 2. Scope & Functional Requirements

### Phase 1: Empty / Static Inventory Audit
- Audit all components across the 6 views:
  1. **Executive Summary & Cockpit (`view-exec-briefing`)**:
     - Gemini AI Executive Decision Briefing (`#geminiSummaryText`)
     - Top 3 Critical Executive Attention Items (`#top3ThingsContainer`)
     - Early Warning Sleeper Outlier Card (`Ref 1.15`)
     - Executive 4-KPI Banner (Commercial, Milestone 2 IBR, ATO-C Security, Escalations)
     - Gap Close Horizon Cards (#1-#5) with baseline diffing and delta notes
     - Synthesis counts footer & copy clipboard actions
  2. **Risk Dashboard & 5x5 Heatmap Matrix (`view-overview`)**:
     - 5x5 Heatmap Grid cells (counts, scores, background classes, cell click filter)
     - Heatmap status count filter buttons (`Open`, `Active`, `Eventuated`, `Closed`, `All`)
     - Top 3 KPI Cards (Critical Exposure 18-25, Eventuated Issues, Unactioned Risks)
     - Live Risk Explorer & Triage cards and compact table rows with search/category filters
  3. **Issue Register Dashboard (`view-issues`)**:
     - Interactive Issue Table with live search filtering, severity badges, priority ratings, governance levels, and Google Sheet links
  4. **Performance Trends & Timeline Analytics (`view-trends`)**:
     - Backlog Timeline Chart (Active Risk Trend, Active Risks, New Risks Opened, Risks Closed)
     - Burndown Timeline Chart (Inherent vs Residual score burndown)
     - Risk Cause Category Concentration horizontal bar chart
     - Risk Severity Profile 5x5 score band breakdown cards
     - Dynamic Period Badge tracking
  5. **CD1 Driver Tree Hierarchy (`view-driver-tree`)**:
     - Tier 0 Objective & Tier 1 Capability Drops header
     - Header deck link and reference badge
     - 24 Deliverable Cards (Refs 1.1 to 5.3) with progress bars, RAG badges, schedule shifts, and linked risk/issue counts
     - Level filter count badges (Level 2 vs Level 3 vs All)
  6. **Whole Register Ledger (`view-ledger`)**:
     - Table rows for all 107 risks with scores, owners, and target dates
     - Dynamic CSV Export utility

### Phase 2: Dynamic Pipeline Refactoring
- Refactor `renderTrendsCharts()` to dynamically compute multi-week timeline data directly from `TIME_MACHINE_SNAPSHOTS` across Weekly, Bi-Weekly, and Monthly views.
- Ensure that Category Concentration and Severity Profile charts dynamically calculate from live `LIVE_RISKS` fields.
- Reconcile all snapshot accessors with defensive fallbacks (`snap.week || snap.weekLabel || ('Week ' + snap.weekNumber)`).

## 3. Non-Functional Requirements & Acceptance Criteria
- **Zero Empty States:** No chart canvas, table body, or card container shall render blank or empty.
- **Visual Integrity:** Maintain 100% adherence to Google Material 3 / Tailwind CSS design guidelines.
- **Automated Verification:** All unit tests in `tests/test_server.py` must pass cleanly.
