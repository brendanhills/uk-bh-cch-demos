# F-DSE Project Dashboard UI Mockup (Phase 1)

An interactive, web-based executive dashboard prototype built with **Streamlit**, **Plotly**, and **Pandas** for the F-DSE Program.

## 📋 Canonical Specification & Requirements
The full specification, including exact customer functional requirements, UI component mapping, and stakeholder notes, is documented in Conductor:
- [Specification (`spec.md`)](../conductor/tracks/dashboard_prototype/spec.md)
- [Implementation Plan (`plan.md`)](../conductor/tracks/dashboard_prototype/plan.md)
- [Product Definition](../conductor/product.md)

## 🚀 Quick Start (Running the Mockup)

Ensure you have Python 3.11+ installed along with the dependencies listed in `pyproject.toml` (`streamlit`, `pandas`, `plotly`).

1. Navigate to the dashboard directory:
   ```bash
   cd project_dashboard
   ```

2. Launch the Streamlit application:
   ```bash
   streamlit run app.py
   ```

3. Open the printed local URL (typically `http://localhost:9000`) in your browser to view and interact with the mockup.

## ✨ Features Included in Phase 1 Mockup
- **Executive KPI Cards & Overall Position:** Active risk counts, open issue counts, and 7-day trend arrows (**Better ↑**, **Worse ↓**, **Same ↔**).
- **5x5 Risk Heatmap & Category Breakdown:** Interactive Plotly heatmap with Likelihood vs. Consequence density + distribution across **Cost**, **Scope**, **Schedule**, and **Other**.
- **Top 5 Critical Risks & Issues:** Tables sorted by criticality/severity with trend direction indicators.
- **7-Day Activity & Escalation Panel:**
  - New items raised in the last 7 days (by Cost, Scope, Schedule).
  - Closed items in the last 7 days.
  - Critical risk updates log.
  - Escalation status changes (**Internal** / **IPF/PSG**).
- **Interactive Driver Tree Explorer:** Select any Driver Tree section (`1.10a Infrastructure Ready`, `1.10b Platform Ready`, `Schedule 5 Governance`, etc.) to view its latest status update and filtered associated risks and issues.

## 🔮 Roadmap: Recommended Future Phases
Based on common Google project reporting and executive governance standards:
- **Phase 2 (Operational & Governance Enhancements):**
  - Live Google Sheets API backend integration with automatic category normalization.
  - **Aging & Stale Risk Radar** (`Open Days > 180` and overdue SLA tracking).
  - **Owner Accountability Matrix (RACI View)** for individual owner workloads.
  - **12-Week Historical Trendlines** & Burn-Down charts.
  - **Cross-Bundle Dependency Graph** (Sankey blocker diagram).
- **Phase 3 (Executive Reporting & AI Automation):**
  - **AI-Assisted Weekly Blurb Generator** (3-bullet executive status synthesis).
  - **Automated Escalation Notifications** (IPF/PSG & Internal alerts).
  - **One-Click Executive Deck & Doc Export** (PDF / Google Docs snapshot).
