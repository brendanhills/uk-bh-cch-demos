# Implementation Plan: Project Dashboard UI Mockup (Phase 1)

## Phase 1: Streamlit UI Mockup & Interactive Components (Current)
- [ ] **Task 1.1: Mock Dataset & Streamlit Structure (`app.py`)**
  - Implement self-contained realistic mock data for Risks and Issues (with Cost, Scope, Schedule categories, timestamps, ratings, and Driver Tree references).
  - Implement top header KPI summary cards and 7-day net change indicators.
- [ ] **Task 1.2: Visual Charts & Heatmap Components**
  - Implement Plotly 5x5 Inherent / Residual Likelihood vs. Consequence Risk Heatmap.
  - Implement Cost, Scope, Schedule category breakdown chart.
- [ ] **Task 1.3: Top 5 Critical Tables & 7-Day Activity Panel**
  - Implement Top 5 Critical Risks and Top 5 Critical Issues tables with trend arrows (Better ↑, Worse ↓, Same ↔).
  - Implement 7-Day Activity & Escalation panel (New, Closed, Critical updates, Escalations to Internal / IPF/PSG).
- [ ] **Task 1.4: Interactive Driver Tree Explorer**
  - Implement Driver Tree section selector, latest update banner, and linked Risks & Issues tables.

---

## Phase 2: Operational & Governance Enhancements (Roadmap)
- [ ] **Task 2.1: Google Sheets Backend & Caching Layer**
  - Integrate live Google Sheets API connection with automated category normalization for Cost, Scope, Schedule.
- [ ] **Task 2.2: Stale Item & Aging Radar (`Open Days` & Overdue SLA)**
  - Track aging risks (`Open Days > 180`) and stale critical items with no status update in >14 days.
- [ ] **Task 2.3: Owner & Accountability Matrix (RACI View)**
  - Group items by Risk/Issue Owner showing open load, target dates, and mitigation status.
- [ ] **Task 2.4: 12-Week Historical Trendline & Burn-Down**
  - Add time-series charts tracking active vs. closed risks over a 12-week rolling window.
- [ ] **Task 2.5: Cross-Bundle & Driver Tree Dependency Graph**
  - Add Sankey or network diagram mapping blocker relationships across Driver Tree milestones.

---

## Phase 3: Executive Reporting & AI Automation (Roadmap)
- [ ] **Task 3.1: AI-Assisted Weekly Executive Summary (Blurb Generator)**
  - Build automated 3-bullet executive summary generator from 7-day deltas and Driver Tree updates.
- [ ] **Task 3.2: Automated Escalation Alerting**
  - Implement automated notifications for IPF/PSG and Internal Google escalations.
- [ ] **Task 3.3: One-Click Executive Deck & Doc Export**
  - Build PDF/Google Doc snapshot export for governance meetings.
