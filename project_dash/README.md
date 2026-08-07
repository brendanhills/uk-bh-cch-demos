# F-DSE Program Governance Dashboard (`project_dash`)

A modern, high-contrast, exception-first executive governance platform for the F-DSE Program. Built with single-tech-stack vanilla HTML5, Tailwind CSS, Chart.js, and a native Python HTTP server with Google Drive report ingestion APIs.

---

## 🚀 Quick Start (Port 9000)

```bash
# Run server
cd project_dash
uv run python server.py
```
Open **`http://localhost:9000`** in your browser (or forward port 9000 via SSH: `ssh -L 9000:localhost:9000 <host>`).

---

## 🏛️ Core Architecture & Tabs

1. **✨ Executive Summary (Tab 1)**:
   - Exception-first Gemini 3.5 Pro Briefing, Top 3 Attention Items, Early Warning Sleeper Outlier (`Ref 1.15 PDR`), and Schedule Squeeze Warnings.
   - Dual-host NotebookLM podcast player with neutral Australian voices (`en-AU-Neural2-A` & `B`), speed toggle, and direct audio download.
   - Active Escalations 2×2 grid with 1-Cycle Resolution banner (`#3 I-129`) and real-time temporal clock.

2. **📊 Risk Dashboard & Live Explorer (Tab 2)**:
   - 5×5 Risk Heatmap Matrix (Inherent vs Residual toggle), quick preset chips (`📋 All Risks`, `🔴 Score ≥ 18`, `📈 Trending Worse`, `⚠️ Eventuated Issues`, `🏛️ Joint Exec Escalations`), and live search.

3. **⚠️ Issue Register (Tab 3)**:
   - Complete 29-issue register with root causes, priority badges, and active remediation plans.

4. **📈 Performance Trends (Tab 4)**:
   - Weekly, Bi-Weekly, and Monthly granularity burndown charts, and dynamic Risk Cause Category Concentration horizontal bar chart.

5. **🌳 CD1 Driver Tree & Gap Close Horizon (Tab 5)**:
   - Enterprise light theme Strategic Architecture overview (Pages 3–5 reference), Level 2 & 3 deliverable decomposition, and Gap Close Horizon cards.

6. **📋 Whole Register Ledger (Tab 6)**:
   - Searchable, exportable CSV table of the complete 107-risk register.
