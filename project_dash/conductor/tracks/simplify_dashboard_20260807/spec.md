# Specification: Simplify Dashboard & Unified Bug Resolution (URL-Driven PM View)

## 1. Overview & Strategic Objective
Transform the F-DSE Program Governance Dashboard into an ultra-streamlined, exception-first cockpit that never overwhelms executives with raw data. Keep the UI 100% clean and unpolluted by defaulting to a 4-tab executive layout, while providing a clean URL parameter (`?view=pm` or `?ledger=true`) to dynamically unlock the 5th "Whole Register Ledger" tab for PM detailed reviews and A/B testing.

---

## 2. Core Architectural Invariants
- **"No News is Good News"**: Highlight only items requiring executive action, decision, or exposing the project to cost/schedule risk.
- **Zero-Pollution URL-Driven Views**:
  - **Default Executive Mode (`/`)**: Clean 4-tab view (`✨ Executive Summary`, `📊 Risk & Issue Cockpit`, `📈 Performance Trends`, `🌳 CD1 Driver Tree & Horizon`) with direct links to Google Drive (`Open Sheet ↗`). No extra toggle pills polluting the header.
  - **PM Exhaustive Mode (`/?view=pm`)**: Dynamically exposes Tab 5 (`📋 Whole Register Ledger`) with full 107-risk / 29-issue tables.
- **Preservation of Reference Baseline**: Never delete or purge `project_dash/dash_v1/`.
- **Unified Single-Stack SPA**: Clean vanilla HTML5 / Tailwind / Chart.js architecture.

---

## 3. Scope & Ticket Mapping

### Domain 1: Navigation & Information Architecture
- **FR #10**: Make dashboard header title and logo clickable to return to Executive Summary home view.
- **Bug #5**: Fix ATO-C Security Gate status styling so the text `AMBER` renders in amber font (`text-amber-500`) instead of green.
- **4-Tab Navigation & URL Param**: Default to 4 core tabs; check `URLSearchParams` on page load to conditionally reveal Tab 5 (`?view=pm`).

### Domain 2: Risk & Issue Cockpit Harmonization
- **FR #14**: Unify Risk Heatmap and Issue Register into a single cohesive cockpit with side-by-side visual summary (5x5 Matrix + Issue Severity/Aging breakdown).
- **Bug #7**: Reconcile 5x5 heatmap cell click-through with active visual focus ring (`ring-2 ring-indigo-500`) and smooth filter scrolling.
- **Filter Simplification**: Streamline quick filters to 3 essential preset chips (`All Exceptions`, `Score ≥ 18`, `Eventuated Issues`).

### Domain 3: Dynamic Trends, Analytics & Time Travel
- **Bug #8**: Ensure `<canvas id="chartBurndownBurnup">` has a fixed min-height container (`h-64`) and renders reliably across all tabs.
- **FR #13**: Dynamically parse multi-week Drive snapshots (`src/data/weekly_snapshots.json`) across Weeks 22–26 to compute true net risk velocity and burndown trajectories.
- **FR #9**: Embed a persistent horizontal weekly scrubbing ribbon (`W22`, `W23`, `W24`, `W25`, `W26 Live`) across the top of the Time Machine banner.

### Domain 4: Enterprise Settings, Drive Management & Tools
- **FR #16**: Build a human-readable Sheet & Drive Folder switcher in the Settings modal displaying clear document titles rather than technical IDs.
- **FR #6**: Add an in-dashboard Gemini prompt editor tab with live token counter and "Save & Re-synthesize" trigger.
- **Bug #1**: Implement client-side PDF export (via `jspdf` / print) and valid presentation generator.
