# UK BH Experiments Repository

Various experiments, training, learning, and customer demos.

## 📊 Projects & Demos

### 1. Project Dashboard UI Mockup (`project_dashboard/`)
- **Description:** Executive and operational risk/issue dashboard mockup built with Streamlit, Plotly, and Pandas.
- **Key Features:**
  - Executive KPI cards and 7-day trend arrows.
  - Interactive 5x5 Likelihood vs. Consequence Risk Heatmap.
  - Top 5 Critical Risks & Top 5 Critical Issues tables.
  - 7-Day Activity & Escalation Tracker (Internal & IPF/PSG).
  - Interactive Driver Tree Explorer.
- **Specification:** [`conductor/tracks/dashboard_prototype/spec.md`](./conductor/tracks/dashboard_prototype/spec.md)
- **Quick Start:**
  ```bash
  cd project_dashboard
  uv run streamlit run app.py
  ```
