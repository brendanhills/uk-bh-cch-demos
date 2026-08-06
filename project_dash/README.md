# F-DSE Project Dashboard (Unified v1 & v2 App)

Interactive executive dashboard application built with **Streamlit**, **Plotly**, and **Pandas** for the F-DSE Program.

Both **v1 (Baseline Customer Specification)** and **v2 (Advanced Program Reporting Roadmap)** are served directly from the same single application with instant URL routing!

---

## 🚀 Running the App (Port 9000)

```bash
cd /usr/local/google/home/brendanhills/dev/uk-bh-experiments/project_dash
uv run streamlit run app.py
```

### 🔗 URL Paths & Query Parameter Direct Links
- **Default / Baseline View (v1):**  
  👉 **`http://localhost:9000/?version=v1`**  
  *(Contains 5x5 Heatmap, Top 5 Critical Tables with trend arrows, 7-Day Activity & Escalation Panel, and Driver Tree Explorer)*

- **Advanced Roadmap View (v2):**  
  👉 **`http://localhost:9000/?version=v2`**  
  *(Contains AI Executive Summary Generator, Stale SLA & Aging Risk Radar, Owner RACI Workload Matrix, 12-Week Trendlines, Sankey Dependency Graph, and 1-Click Deck Export)*

*Note: Users can also seamlessly toggle between **v1** and **v2** using the top radio selector in the sidebar at any time.*
