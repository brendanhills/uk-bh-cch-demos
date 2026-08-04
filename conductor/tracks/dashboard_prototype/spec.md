# Specification: Project Dashboard Prototype

## Overview
The goal of this track is to build an interactive Streamlit prototype of the Project Dashboard for team risk and issue tracking. The prototype allows stakeholders to review overall risk posture, inspect category heatmaps, track 7-day deltas, and explore risks and issues organized by Driver Tree items.

## Technology Stack
- **Language:** Python 3.11+
- **UI Framework:** Streamlit
- **Data Analysis & Visualization:** Pandas, Plotly
- **Data Integration:** Hybrid (Google Sheets API reader + local CSV fallback cache)

## Functional Requirements

### 1. Data Ingestion & Cleaning Pipeline
- **Hybrid Source:** Ingest data from the target Google Sheet (`Risk Register` and `Issue Register` worksheets) with a fallback to local cached CSV files (`data/risk_register_cache.csv` and `data/issue_register_cache.csv`).
- **Category Normalization:** Automatically clean and map heterogeneous category entries into three standard categories: **Cost**, **Scope**, **Schedule**, with an **Other** fallback for uncategorized items.

### 2. Dashboard KPI Header & Overall Position
- **KPI Summary Cards:** Total active risks, open issues, 7-day net changes.
- **Trend Indicators:** Visual status badges showing overall direction (Better, Worse, Same).

### 3. Risk Heatmap & Category Breakdown
- **Matrix View:** 5x5 Likelihood vs. Consequence risk heat map displaying risk density across inherent and residual ratings.
- **Category Breakdown:** Chart displaying risk and issue distribution across Cost, Scope, Schedule, and Other.

### 4. Top 5 Critical Risks & Issues
- **Top 5 Critical Risks Table:** Ranked by risk rating/criticality score with trend arrows (Better ↑, Worse ↓, Same ↔).
- **Top 5 Critical Issues Table:** Ranked by criticality with status, owner, and trend indicators.

### 5. 7-Day Activity & Escalation Tracker
- **New Items (Last 7 Days):** Risks and issues raised in the last 7 days, categorized by Cost, Scope, Schedule.
- **Closed Items (Last 7 Days):** Risks and issues marked as closed within the last 7 days.
- **Critical Risk Updates:** Log of updates applied in the last week to risks rated 'Critical'.
- **Escalation Changes:** Highlight new or existing items whose escalation status changed to `Internal` or `IPF/PSG`.

### 6. Interactive Driver Tree Explorer
- **Hierarchical Tree View:** Visual breakdown of Driver Tree items (`Driver Tree Ref`).
- **Section Detail Drill-down:** Clicking or selecting a Driver Tree section displays:
  - Latest section status update.
  - Filtered list of associated risks and issues.

## Non-Functional Requirements
- **Performance:** Sub-second response for UI interactions using Streamlit `@st.cache_data`.
- **Portability:** Standalone runnable script using standard Python dependencies.

## Out of Scope (For Prototype)
- User authentication / role-based access control.
- Write-back to Google Sheets (read-only for prototype).
