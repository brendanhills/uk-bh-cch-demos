# F-DSE Program Governance & Risk Intelligence Platform

Interactive Executive Cockpit and Risk Intelligence Platform built for the **Future Data Science Environment (F-DSE)** governance lifecycle.

---

## 🌟 Key Architecture & Capabilities

1. **Single Product Vanilla Architecture**:
   - High-performance, zero-build single-file SPA (`index.html`) using Tailwind CSS and Chart.js.
   - Sub-millisecond tab switching and native browser history (`pushState` / `popstate`).
2. **Executive Decision Briefing (Gemini 3.5 Pro)**:
   - Exception-first synthesis highlighting Top 3 Critical Action items, Early Warning Sleeper Outlier (`Ref 1.15`), and schedule squeeze alerts.
   - Neural Australian Audio Briefing (`en-AU-Neural2-A` & `B`) with speed controls, animated waveform, and direct download.
3. **Interactive 5×5 Risk Heatmap & Issue Cockpit**:
   - Dynamic Inherent vs. Residual matrix toggling, active focus rings, and granular 1-click citation jumps (`↗`).
4. **Performance Trends & Velocity**:
   - Dynamic Burndown and Risk Cause Category distribution with `Weekly`, `Bi-Weekly`, and `Monthly` granularity.
5. **Contractual Delivery & Gap Close Horizon**:
   - CD1 Driver Tree linking Level 2 Contractual Milestones to high-priority remediation plans.
6. **Live Google Drive & Sheets Sync API**:
   - Local Python server (`server.py`) handling real-time Google Sheets sync, weekly PDF report ingestion, and Time Machine historical snapshots.

---

## 🚀 Quickstart

```bash
# Run server on port 9000
uv run python server.py

# Open in browser
http://localhost:9000
```

---

## 📁 Repository Layout

```
project_dash/
├── index.html                  # Core Single-Page Application (HTML5 / Tailwind / Chart.js)
├── server.py                   # Python server with Drive sync and ingestion APIs
├── README.md                   # Project documentation
├── assets/                     # Audio assets (podcast_w26.mp3, podcast_w26.wav)
├── prompts/                    # Gemini prompt templates (exec_summary_prompt.md)
├── scripts/                    # Report ingestion utilities (ingest_weekly_report.py)
├── src/data/                   # Weekly snapshots and live sync data
├── archive/                    # Archived Streamlit prototype files
├── dash_v1/                    # Reference React/Vite v1 prototype
└── conductor/                  # Conductor SDD tracks, specs, and implementation plans
```
