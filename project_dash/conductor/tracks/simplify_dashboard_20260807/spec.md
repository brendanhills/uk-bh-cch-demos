# Specification: Simplify Dashboard (Single Unified 4-View Architecture)

## 1. Overview & Objective
Transform the F-DSE Program Governance Dashboard into an ultra-streamlined, exception-first cockpit featuring a single unified 4-tab interface designed to serve BOTH Project Managers and Executives without compromise. Consolidate fragmented views, enforce progressive disclosure (capping on-screen exception cards at 6), provide direct 1-click links to Google Sheets/Drive for deep inspection, and resolve all outstanding defect and feature tickets.

---

## 2. Guiding Principles
- **One Unified View for All**: Single clean interface optimized for both high-level executive decision-making and operational PM governance.
- **"No News is Good News"**: Highlight only items requiring executive action, decision, or exposing the project to cost/schedule risk.
- **Progressive Disclosure**: Surface top critical items on screen with direct Google Sheets deep links (`Open Sheet ↗`) for exhaustive tabular data.
- **Zero UI Clutter**: Clean header, streamlined navigation, no superfluous mode switchers.
- **Preservation of Reference Baseline**: Never delete or purge `project_dash/dash_v1/`.

---

## 3. 4 Core Views
1. **✨ Executive Summary**: Decision Cockpit, Top 3 Attention Items, Sleeper Outlier (`Ref 1.15`), and Neural Australian Audio Briefing.
2. **📊 Risk & Issue Cockpit**: Side-by-side 5x5 Risk Heatmap & Issue Status overview, with unified exception explorer and 3 quick filters.
3. **📈 Performance Trends**: Dynamic burndown timeline and Risk Cause Category distribution.
4. **🌳 CD1 Driver Tree & Delivery Horizon**: Strategic architecture and Level 2 contractual gate progression.
