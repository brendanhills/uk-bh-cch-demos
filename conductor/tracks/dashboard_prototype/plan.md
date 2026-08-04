# Implementation Plan: Project Dashboard Prototype

## Phase 1: Project Setup & Data Ingestion Core
- [ ] **Task 1.1: Environment & Local Cache Setup**
  - Create `data/` directory.
  - Export/populate local CSV cache files (`data/risk_register_cache.csv`, `data/issue_register_cache.csv`) for offline fallback.
- [ ] **Task 1.2: Data Ingestion & Cleaning Module**
  - Implement `src/data_loader.py` with hybrid Google Sheets API / CSV fallback loading.
  - Implement category normalization rules (`Cost`, `Scope`, `Schedule`, `Other`).
  - Write unit tests in `tests/test_data_loader.py`.

## Phase 2: Analytics & Delta Calculation Engine
- [ ] **Task 2.1: Trend, Delta & Escalation Processing**
  - Implement `src/analytics.py` for 7-day window filters (new, closed, critical updates, escalation changes).
  - Implement Top 5 critical risks/issues ranking and rating trend logic (Better, Worse, Same).
  - Write unit tests in `tests/test_analytics.py`.

## Phase 3: Streamlit UI App & Driver Tree Components
- [ ] **Task 3.1: Streamlit Main Layout & KPI Overview**
  - Create `app.py` Streamlit entrypoint.
  - Implement KPI summary cards, Top 5 tables, and 7-day activity panel.
- [ ] **Task 3.2: Visual Risk Heatmap & Category Charts**
  - Implement Plotly 5x5 Risk Heatmap matrix (Likelihood vs Consequence).
  - Implement category distribution bar/pie charts.
- [ ] **Task 3.3: Interactive Driver Tree Explorer**
  - Implement Driver Tree hierarchy selector and drill-down panel showing status updates and linked items.

## Phase 4: Verification & Prototype Handoff
- [ ] **Task 4.1: Automated Unit Testing**
  - Run `pytest` to ensure all data cleaning and analytics tests pass cleanly.
- [ ] **Task 4.2: Prototype Application Launch & Verification**
  - Launch Streamlit app and verify interactive features.
