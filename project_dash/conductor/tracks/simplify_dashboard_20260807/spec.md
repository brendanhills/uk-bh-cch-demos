# Specification: Simplify Dashboard (4-View Architecture & Progressive Disclosure)

## 1. Overview & Objective
Transform the F-DSE Program Governance Dashboard into an ultra-streamlined, exception-first cockpit that never overwhelms the PM or Executive with wall-to-wall data. Consolidate fragmented tabs into 4 clear operational views, enforce strict progressive disclosure (capping on-screen exception cards), and provide direct 1-click deep links to Google Drive / Sheets for exhaustive line-item lookups.

---

## 2. Guiding Principles
- **No News is Good News**: Highlight only items requiring executive action, decision, or exposing the project to cost/schedule risk.
- **Progressive Disclosure**: Surface top critical items (max 4–6) on screen with one-click toggles and external Drive links for deep details.
- **4 Streamlined Views**:
  1. **Executive Decision Briefing**: Top 3 actions, sleeper leading indicators, and active escalations.
  2. **Risk & Issue Cockpit**: Harmonized 5x5 heatmap and issue overview with unified exception explorer.
  3. **Performance Trends**: Clean burndown trajectory and cause concentration.
  4. **CD1 Driver Tree & Delivery Horizon**: Strategic architecture and gate status.

---

## 3. Functional Requirements
1. **4-Tab Navigation Bar**:
   - Tab 1: `✨ Executive Summary`
   - Tab 2: `📊 Risk & Issue Cockpit`
   - Tab 3: `📈 Performance Trends`
   - Tab 4: `🌳 CD1 Driver Tree & Delivery Horizon`
2. **Header Home Link**: Make dashboard title/logo clickable to return to Executive Summary from any tab.
3. **Unified Risk & Issue Cockpit**:
   - Merge Tab 2 (Risk Dashboard) and Tab 3 (Issue Register) into a single cohesive cockpit.
   - Side-by-side visual summary (5x5 Risk Heatmap + Issue Severity breakdown).
   - Unified exception search and streamlined preset filters (`All Exceptions`, `Score ≥ 18`, `Eventuated Issues`).
4. **Visual & Layout De-Cluttering**:
   - Fix ATO-C Security Gate status styling (`AMBER` text in yellow font).
   - Fix Trends burndown line chart rendering and container sizing.
   - Embed horizontal weekly scrubbing ribbon in Time Machine banner.
