# Specification: Project Dashboard UI Mockup (Phase 1)

## 1. Overview & Purpose
This specification defines the Phase 1 **Project Dashboard UI Mockup** built for the F-DSE Program team. It provides an interactive Streamlit application with in-memory mock data to demonstrate the executive dashboard layout, category heatmaps, trend tracking, and Driver Tree drill-down before live Google Sheets backend integration is built.

---

## 2. Customer Functional Requirements (Exact Specification)
The dashboard directly implements the following customer requirements:

> **What we want in the dashboard:**
>
> - **Overall Position & Heat Map:**
>   - *"what’s our overall position - number of risks (show trends), how many in each category (ie some sort of heat map)"*
> - **Top 5 Critical Issues & Risks with Trends:**
>   - *"5 top issues based on criticality"*
>   - *"5 top risks based on criticality"*
>   - *"What are the trends for each? Better, worse, the same"*
> - **7-Day Activity & Escalation Tracking:**
>   - *"New risks and issues raised in last 7 days (show category - Cost, Scope, Schedule - I think we need to clean up some of the data in the sheet for Cost, Scope, Schedule)"*
>   - *"risks and issues closed in the last 7 days"*
>   - *"Updates in the last week for risks rated 'critical'"*
>   - *"New risks/issues or existing ones that have had their Escalation status changed to - Internal and IPF/PSG"*
> - **Driver Tree Explorer:**
>   - *"Driver tree - show risks and issues assigned to each driver tree item. Click into each section for an update and list of associated issues and risks"*

---

## 3. Dashboard UI Mapping & Architecture (Phase 1 Mockup)

### 3.1. KPI Header & Overall Position
- **Active Risks Metric Card:** Displays total active risks and 7-day net change badge.
- **Open Issues Metric Card:** Displays total open issues and 7-day net change badge.
- **Overall Trajectory Badge:** Directional badge (**Better ↑**, **Worse ↓**, **Same ↔**).
- **5x5 Matrix Heatmap:** Plotly heatmap representing Likelihood (1-5) vs. Consequence (1-5), with Inherent vs. Residual risk toggle.
- **Category Breakdown Chart:** Bar/donut chart showing distribution across **Cost**, **Scope**, **Schedule**, and **Other**.

### 3.2. Top 5 Critical Items by Rating
- **Top 5 Risks Table:** Filtered to active risks ranked by risk rating with trend arrows (**Better ↑**, **Worse ↓**, **Same ↔**).
- **Top 5 Issues Table:** Filtered to active issues ranked by severity/priority rating with trend arrows (**Better ↑**, **Worse ↓**, **Same ↔**).

### 3.3. 7-Day Activity & Escalation Panel
- **New Items (Last 7 Days):** Categorized across **Cost**, **Scope**, and **Schedule** with automated category normalization.
- **Closed Items (Last 7 Days):** Count and summary list of resolved items.
- **Critical Risk Updates (Last 7 Days):** Log of recent comment/status updates for `'Critical'` rated risks.
- **Escalation Status Changes:** Highlight items changed to **Internal** or **IPF/PSG**.

### 3.4. Interactive Driver Tree Explorer
- **Driver Tree Selector:** Dropdown selector for Driver Tree items (`Driver Tree Ref`).
- **Section Drill-Down:** Selecting a Driver Tree section displays:
  1. **Latest Section Status Update** & Section Owners.
  2. **Filtered Associated Risks Table**.
  3. **Filtered Associated Issues Table**.

---

## 4. Future Phase Recommendations (Google Program Reporting Roadmap)
Based on common Google project reporting and executive governance standards, the following capabilities are documented for later phases:

### 4.1. Phase 2: Operational & Governance Enhancements
1. **Stale Item & Aging Radar (`Open Days` & Overdue SLA):**
   - Track aging risks (`Open Days > 180`) and stale critical items with no status update in >14 days.
2. **Owner & Accountability Matrix (RACI View):**
   - View grouped by Risk/Issue Owner showing open critical load, upcoming target dates, and mitigation completion status (`Completed`, `In Progress`, `Overdue`).
3. **12-Week Historical Trendline & Burn-Down:**
   - Time-series charts tracking active vs. closed risks over a 12-week rolling window to show program convergence.
4. **Cross-Bundle & Driver Tree Dependency Graph:**
   - Sankey diagram or interactive network graph mapping blocker relationships across Driver Tree milestones.

### 4.2. Phase 3: Executive Reporting & AI Automation
1. **AI-Assisted Weekly Executive Summary (Blurb Generator):**
   - Automatically synthesize 7-day deltas, critical updates, and Driver Tree status changes into a 3-bullet executive summary for weekly reporting emails and g3docs.
2. **Automated Escalation Alerting (IPF/PSG & Internal):**
   - Trigger automated notifications or sign-off workflows when an item is escalated to **IPF/PSG** or **Internal Google**.
3. **One-Click Executive Deck & Doc Export:**
   - Export filtered KPI cards, Top 5 tables, and 5x5 Heatmaps directly into formatted PDF snapshots or Google Docs/Slides.

---

## 5. Technology Stack
- **Language:** Python 3.11+
- **UI Framework:** Streamlit (`streamlit`)
- **Data Analysis & Visualization:** Pandas (`pandas`), Plotly (`plotly`)
- **Data Source (Phase 1):** In-memory structured mock dataset representing realistic Risk Register and Issue Register entries.

---

## 6. Stakeholder Review & Notes
*Use this section to record team feedback, sheet data cleaning notes, and feature requests during demo review:*

- **Data Cleanup Notes (Cost / Scope / Schedule):**
  - 
- **UI / Layout Feedback:**
  - 
- **Phase 2 Backend Requirements:**
  - 

---

## 7. Acceptance Criteria
- [ ] Application launches cleanly via `streamlit run app.py` with zero external file dependencies.
- [ ] Mock data cleanly renders all required sections of the dashboard.
- [ ] Interactive filters and Driver Tree drill-down operate smoothly.
- [ ] Future phase recommendations are documented for stakeholder roadmap discussions.
