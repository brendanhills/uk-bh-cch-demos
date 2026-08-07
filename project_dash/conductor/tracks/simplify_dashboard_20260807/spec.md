# Specification: Simplify Dashboard & Unified Bug Resolution

## 1. Overview & Strategic Objective
Transform the F-DSE Program Governance Dashboard into an ultra-streamlined, exception-first cockpit that never overwhelms the PM or Executive with wall-to-wall data. Consolidate fragmented views into 4 operational tabs, enforce strict progressive disclosure (capping on-screen exception cards), harness multi-week historical Drive snapshots for true analytics, provide human-readable Drive/Sheet resource management, and resolve all outstanding defect and feature tickets.

---

## 2. Core Architectural Invariants
- **"No News is Good News"**: Highlight only items requiring executive action, decision, or exposing the project to cost/schedule risk.
- **Progressive Disclosure**: Surface top critical items (max 4–6) on screen with one-click toggles and external Drive links (`Open Sheet ↗`) for deep line-item inspection.
- **Preservation of Reference Baseline**: Never delete or purge `project_dash/dash_v1/` during refactoring or cleanup.
- **Unified Single-Stack SPA**: Clean vanilla HTML5 / Tailwind / Chart.js architecture with zero build step and sub-millisecond tab routing.

---

## 3. Scope & Ticket Mapping

### Domain 1: Navigation & Information Architecture
- **FR #10**: Make dashboard header title and logo clickable to return to Executive Summary home view.
- **Bug #5**: Fix ATO-C Security Gate status styling so the text `AMBER` renders in amber font (`text-amber-500`) instead of green.
- **Tab Consolidation**: Streamline navigation bar from 6 tabs down to 4 core views:
  1. `✨ Executive Summary`
  2. `📊 Risk & Issue Cockpit`
  3. `📈 Performance Trends`
  4. `🌳 CD1 Driver Tree & Delivery Horizon`
- **Ledger Elimination**: Remove standalone Ledger tab and embed direct Google Sheet deep links.

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
