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

## 🚀 Remote Deployment & AI Studio Collaboration (`c4astart`)

To deploy this dashboard internally without running it on your laptop, and to allow colleagues (including Extended Workforce / xWF) to modify it via **Google AI Studio**:

### 1. Deploy to Internal Google Cloud Run via `c4astart`
```bash
# 1. Package the dashboard directory
zip -r dashboard_app.zip . -x "*.git*" "*/node_modules/*" "*/.venv/*" "dist/*"

# 2. Deploy to C4A Starter
python3 ../.agents/skills/c4astart/scripts/upload_zip.py \
  dashboard_app.zip \
  --repo-name project-dashboard \
  --application-name "F-DSE Project Dashboard"
```

- **Live URL:** `https://start.c4a.corp.goog/applications?focus=<applicationId>` (secured with Corp SSO / `gosso`).
- **Auto-Generated Repo:** `git@depot.code.corp.goog:<org>/project-dashboard.git`.

### 2. Colleague AI Studio Collaboration
1. Colleague clones the GitHub Enterprise repo (`depot.code.corp.goog`).
2. Iterates in **Google AI Studio** (`aistudio.google.com`) on components/prompts.
3. Commits and pushes changes directly to the **`dev`** branch (we always push to `dev`, never pushing feature branches to origin):
   ```bash
   git checkout dev
   # apply updated files
   git add .
   git commit -m "feat: updated dashboard components from AI Studio"
   git push origin dev
   ```
4. Pushing to `dev` automatically triggers a build and redeploys the live application.
5. Pull updates back into your local Jetski environment with `git pull origin dev`.

---

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
