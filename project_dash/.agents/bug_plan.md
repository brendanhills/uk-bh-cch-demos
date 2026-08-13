# Phased Bug Implementation Plan (`bug_plan.md`)

## Executive Summary
This implementation plan establishes a phased, risk-balanced roadmap for addressing the open bugs and feature enhancements in **Project Dash**. The strategy prioritizes core interactive drill-down fixes and filter ergonomics in **Phase 1**, multi-stream workspace synchronization and executive briefing synthesis in **Phase 2**, and navigation and widescreen layout expansion in **Phase 3**.

---

## 🎯 Phased Implementation Roadmap

### 🚀 Phase 1: Core Filter & Drill-Down Interactivity
*Focus: Resolving broken filter state combinations, enabling relational Blueprint queries, and unlocking full card drill-downs.*

| Bug ID | Priority | Impact | Risk | Title | Fix Strategy |
| :---: | :---: | :---: | :---: | :--- | :--- |
| **#30** | **P1** | High | Low | **5x5 Heatmap Cell Filter Stale Query Conflict** | Reset `explorerSearchInput` and conflicting category filters upon clicking any matrix cell to ensure exact cell risk display. |
| **#33** | **P1** | High | Low | **Blueprint 'Filter Risk Matrix' Yields Empty List** | Match bundle key against `BUNDLE_ANNEX_MAPPING[key].jointRisks` and synchronize `filterBundleSelect`. |
| **#34** | **P1** | Medium | Low | **Team Google Risk Cards Lack Drill-Down / Modal** | Add `onclick="openItemDetailModal('risk', id)"` and expandable in-line detail sections to Team Google risk cards. |
| **#31** | **P1** | Medium | Low | **Team Google 5x5 Matrix Layout Standardization** | Standardize matrix layout to match primary 5x5 heatmap design (large scores, circular badges, axis headers) with Google Blue accents. |

---

### 🔄 Phase 2: Unified Multi-Stream Sync & Executive Synthesis
*Focus: Consolidating external data streams into a single pane of glass and enriching the executive briefing with Team Google and Blueprint intelligence.*

| Bug ID | Priority | Impact | Risk | Title | Fix Strategy |
| :---: | :---: | :---: | :---: | :--- | :--- |
| **#28 & #35** | **P1** | High | Low | **Unify Google Risk Sheet & NotebookLM in Sync Modal** | Rebuild `#sheetsModal` into a 4-stream sync hub (Joint Sheet, Team Google Sheet `1lNRf5NEBd...`, Drive Reports, and Contract Notebook `acdbb29b...`). |
| **#27** | **P1** | High | Low | **Enrich Executive Summary with Team Google & Blueprints** | Update `renderExecBriefing()` to compute multi-stream roll-ups, spotlight Google engineering milestones, and link governing contract Annexes. |

---

### 🎨 Phase 3: Interactive Navigation & Viewport Layout Polish
*Focus: Maximizing widescreen monitor usability and making all executive cockpit indicators interactive.*

| Bug ID | Priority | Impact | Risk | Title | Fix Strategy |
| :---: | :---: | :---: | :---: | :--- | :--- |
| **#29** | **P2** | Medium | Low | **Make Executive Cockpit Top Banner & KPIs Clickable** | Wire click handlers for Time Machine snapshot modal, Driver Tree gates (Refs 1.1, 1.2b, 1.6 GFF), and Issue Register. |
| **#26** | **P2** | Medium | Low | **Widescreen Display Margins Too Large** | Expand container classes from `max-w-7xl` to responsive `max-w-[1750px] w-full px-6` to eliminate wasted screen real estate. |
| **#32** | **P2** | Low | Low | **Issue Register Table Vertical Height Expansion** | Update table container styling to `min-h-[calc(100vh-260px)]` with sticky table headers and smooth auto-scrolling. |

---

## 🧪 Verification & Quality Flywheel
For every bug fix:
1. Develop an automated reproduction test demonstrating failure before modification.
2. Implement targeted code changes.
3. Validate that reproduction tests and existing test suites pass cleanly:
   ```bash
   python3 -m unittest tests/test_data_integrity.py tests/test_server.py
   ```
4. Verify interactive DOM execution with Node.js AST validation (`scratch/test_runtime_js.py`).
