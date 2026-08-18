# Implementation Plan: Modularize `index.html` Frontend Architecture

## Phase 1: Core Foundation, State Management & Pure Analytics Engine
- [ ] Task: Create Pure Computation & Analytics Unit Tests (TDD)
  - [ ] Write unit tests for score calculations, matrix coordinate mapping, and filter predicates in `tests/test_analytics.py`
  - [ ] Write tests verifying state transitions, event notifications, and multi-project routing
- [ ] Task: Implement `src/js/state.js` and `src/js/analytics.js`
  - [ ] Implement reactive state store with subscriber notifications
  - [ ] Extract pure mathematical / data transformation functions into `src/js/analytics.js`
- [ ] Task: Implement `src/js/api.js` (Server API & Sync Client)
  - [ ] Connect directly to `server.py` endpoints (`/api/sync-sheet`, `/api/ingest-data`, `/api/regenerate-briefing`)
  - [ ] Support dynamic multi-project loading (`data/{project}/`) and localStorage caching
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Domain UI Renderers & Component Modules
- [ ] Task: Modularize Executive Cockpit, Briefing & Time Machine
  - [ ] Implement `src/js/modules/exec_briefing.js` (KPI banner, 4 cards, Gemini decision text, podcast player & transcript modal)
  - [ ] Implement `src/js/modules/time_machine.js` (historical scrubbing bar, snapshot switcher, modal list)
- [ ] Task: Modularize Risk Heatmaps, Charts & Risk Explorer
  - [ ] Implement `src/js/charts.js` (Chart.js wrappers, backlog/burndown timeline rendering)
  - [ ] Implement `src/js/modules/risk_heatmap.js` (5×5 matrix, rating/status toggles, cell selection, focus rings)
  - [ ] Implement `src/js/modules/risk_explorer.js` (risk cards, mitigation accordions, search/filter inputs)
- [ ] Task: Modularize Issues, Trends, Blueprints, Driver Tree & Modals
  - [ ] Implement `src/js/modules/issue_register.js` (table rows, sorting, filtering)
  - [ ] Implement `src/js/modules/performance_trends.js` (multi-granularity views, drilldown modal)
  - [ ] Implement `src/js/modules/blueprint_knowledge.js` (cards, Annex mappings, NotebookLM links)
  - [ ] Implement `src/js/modules/driver_tree.js` (milestone gates, deliverable badges)
  - [ ] Implement `src/js/modules/modals.js` (universal item inspection modal, sync modal, settings modal)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Bootstrap Entry Point, Router & HTML Shell Modernization
- [ ] Task: Implement `src/js/app.js` (Application Bootstrap & Router)
  - [ ] Implement URL parameter router (`?project=...&tab=...&view=...`) and global event listeners
- [ ] Task: Streamline `index.html` into Clean Semantic HTML Shell
  - [ ] Strip ~3,700 lines of inline JS from `index.html` down to ~600-800 lines of clean semantic HTML markup
  - [ ] Link `<script type="module" src="src/js/app.js"></script>` and verify local runtime with `server.py` on port 9000
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Build Tooling, Bundler Configuration & CI/CD Pipeline
- [ ] Task: Configure Production Bundler (Vite / Rollup) & Server Static Asset Serving
  - [ ] Configure `vite.config.js` / `package.json` for optional production bundling to `dist/`
  - [ ] Ensure `server.py` seamlessly serves both source modules (local dev) and bundled assets (production container)
  - [ ] Update `Dockerfile` and `deploy/cloudbuild.yaml`
- [ ] Task: Comprehensive Test Suite Verification & Quality Audit
  - [ ] Run full automated test suite (`python3 -m unittest discover tests`) verifying all 85+ tests pass cleanly
  - [ ] Test live ingestion and briefing regeneration end-to-end against `server.py` APIs
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
