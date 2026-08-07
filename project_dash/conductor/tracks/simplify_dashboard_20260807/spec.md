# Specification: Simplify Dashboard (Single Unified 4-View Architecture with URL-Driven A/B Testing)

## 1. Overview & Objective
Transform the F-DSE Program Governance Dashboard into an ultra-streamlined, exception-first cockpit featuring a clean 4-tab interface designed to serve BOTH Project Managers and Executives. To allow live A/B testing with the PM without polluting the user interface with extra toggle buttons, support a clean URL parameter (`?view=pm` or `?ledger=true`) that dynamically reveals the 5th "Whole Register Ledger" tab, while defaulting to the streamlined 4-tab view when unparameterized (`/`).

---

## 2. Guiding Principles
- **One Unified View by Default**: Default to a clean 4-tab interface (`✨ Executive Summary`, `📊 Risk & Issue Cockpit`, `📈 Performance Trends`, `🌳 CD1 Driver Tree & Horizon`).
- **Zero UI Pollution A/B Testing**:
  - Unparameterized (`http://localhost:9000`): Clean 4-tab cockpit with progressive disclosure and `"Open Sheet ↗"`.
  - PM Review Mode (`http://localhost:9000/?view=pm` or `?ledger=true`): Dynamically unlocks and renders Tab 5 (`📋 Whole Register Ledger`) with full 107-risk / 29-issue tables.
- **"No News is Good News"**: Highlight only items requiring executive action or exposing the project to cost/schedule risk.
- **Progressive Disclosure**: Surface top critical items on screen (max 6) with deep links for exhaustive tabular data.
- **Preservation of Reference Baseline**: Never delete or purge `project_dash/dash_v1/`.

---

## 3. 4 Core Views (+ 1 Conditional PM View)
1. **✨ Executive Summary**: Decision Cockpit, Top 3 Attention Items, Sleeper Outlier (`Ref 1.15`), and Neural Australian Audio Briefing.
2. **📊 Risk & Issue Cockpit**: Side-by-side 5x5 Risk Heatmap & Issue Status overview, with unified exception explorer and 3 quick filters.
3. **📈 Performance Trends**: Dynamic burndown timeline and Risk Cause Category distribution.
4. **🌳 CD1 Driver Tree & Delivery Horizon**: Strategic architecture and Level 2 contractual gate progression.
5. **📋 Whole Register Ledger** *(Revealed only when `?view=pm` or `?ledger=true` is present in URL)*.
