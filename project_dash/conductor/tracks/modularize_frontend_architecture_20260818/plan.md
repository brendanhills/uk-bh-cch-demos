# Implementation Plan: Modularize `index.html` Frontend Architecture

## Phase 1: Core Foundation, State Management & Pure Analytics Engine
- [x] Task: Create Pure Computation & Analytics Unit Tests (TDD)
  - [x] Write unit tests for score calculations, matrix coordinate mapping, and filter predicates in `tests/test_analytics.py`
  - [x] Write tests verifying state transitions, event notifications, and multi-project routing
- [x] Task: Implement `src/js/state.js` and `src/js/analytics.js`
  - [x] Implement reactive state store with subscriber notifications
  - [x] Extract pure mathematical / data transformation functions into `src/js/analytics.js`
- [x] Task: Implement `src/js/api.js` (Server API & Sync Client)
  - [x] Connect directly to `server.py` endpoints (`/api/sync-sheet`, `/api/ingest-data`, `/api/regenerate-briefing`)
  - [x] Support dynamic multi-project loading (`data/{project}/`) and localStorage caching
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Domain UI Renderers & Component Modules
- [x] Task: Modularize Executive Cockpit, Briefing & Time Machine
  - [x] Implement `src/js/modules/exec_briefing.js` (KPI banner, Google NTK badge, 4 cards, Gemini decision text, podcast player & transcript modal)
  - [x] Implement `src/js/modules/time_machine.js` (historical scrubbing bar, snapshot switcher, modal list)
- [x] Task: Modularize Risk Heatmaps, Charts & Risk Explorer
  - [x] Implement `src/js/charts.js` (Chart.js wrappers, backlog/burndown timeline rendering)
  - [x] Implement `src/js/modules/risk_heatmap.js` (5×5 matrix, rating/status toggles, cell selection, focus rings)
  - [x] Implement `src/js/modules/risk_explorer.js` (risk cards, mitigation accordions, search/filter inputs, inspect buttons)
- [x] Task: Modularize Issues, Trends, Blueprints, Driver Tree & Modals
  - [x] Implement `src/js/modules/issue_register.js` (table rows, sorting, filtering)
  - [x] Implement `src/js/modules/performance_trends.js` (multi-granularity views, drilldown modal)
  - [x] Implement `src/js/modules/blueprint_knowledge.js` (cards, Annex mappings, NotebookLM links)
  - [x] Implement `src/js/modules/driver_tree.js` (milestone gates, deliverable badges)
  - [x] Implement `src/js/modules/modals.js` (universal item inspection modal, sync modal, settings modal)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Bootstrap Entry Point, Router & HTML Shell Modernization
- [x] Task: Implement `src/js/app.js` (Application Bootstrap & Router)
  - [x] Implement URL parameter router (`?project=...&tab=...&view=...`) and global event listeners
- [x] Task: Streamline `index.html` into Clean Semantic HTML Shell
  - [x] Modularize JavaScript into ES6 modules in `src/js/` adhering to `go/tsstyle`
  - [x] Link `<script type="module" src="src/js/app.js"></script>` and verify local runtime with `server.py` on port 9000
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Build Tooling, Container Deployment & CI/CD Pipeline
- [x] Task: Update Container Deployment & Server Static Asset Serving
  - [x] Ensure `deploy/Dockerfile` copies `src/` modules via `COPY src/ /usr/share/nginx/html/src/`
  - [x] Ensure `deploy/nginx.conf` has proper MIME types and caching headers for `application/javascript`
  - [x] Ensure `server.py` seamlessly serves both source modules (local dev) and static assets
  - [x] Verify `deploy/cloudbuild.yaml` automated build and test pipeline for dev (`origin dev`) and production (`project_dash/prod-.*`)
  - [x] Verify 90-day sandbox billing attachment status documented in `deploy/PROD_PROVISIONING_GUIDE.md`
- [x] Task: Comprehensive Test Suite Verification & Quality Audit
  - [x] Run full automated test suite (`python3 -m unittest discover tests`) verifying all 112 tests pass cleanly
  - [x] Test live ingestion and briefing regeneration end-to-end against `server.py` APIs
  - [x] Perform staging build verification in local Docker or Cloud Build test run
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
