# Specification: Modularize and Simplify `index.html` Frontend Architecture

## 1. Overview
The monolithic `index.html` file currently spans over 4,800 lines (>310 KB), containing ~1,300 lines of HTML markup and ~3,500 lines of inline JavaScript within a single `<script>` block. This structure creates high cognitive load, increases risk during iterative feature development, complicates code reviews, and hinders automated testing.

This track modularizes `index.html` into a maintainable, domain-driven frontend architecture using Google-standard ES Modules (`import`/`export`) and optional Vite/Rollup production bundling, while strictly preserving 100% feature parity, zero-maintenance runtime portability, Python backend ingestion APIs, and all 102+ passing automated unit tests.

---

## 2. Functional & Architectural Requirements

### 2.1 Server Backend & AI Ingestion Invariant
The Python server components (`server.py`, `scripts/ingest_data.py`, and CLI tooling) remain the authoritative backend engine for:
- Google Drive & Sheets data sync (`/api/sync-sheet`)
- On-demand automated data ingestion (`/api/ingest-data`)
- Dynamic report discovery across `drive_reports/`, `drive_cache/`, `reports/`, and `docs/`
- Gemini 3.5 Pro executive summary synthesis & podcast dialogue generation (`/api/regenerate-briefing`)
- Serving static/modular frontend assets and project JSON data across multiple workspaces (`sample`, `f-dse`).

### 2.2 Domain-Driven JavaScript Architecture (`src/js/`)
Separate the embedded JavaScript into focused, single-responsibility ES modules with canonical `snake_case.js` naming:
1. **`src/js/state.js`**: Centralized reactive application state management:
   - Project configuration (`CONFIG`, active project routing `?project=sample` vs `f-dse`).
   - Active dataset storage (`RAW_DATA`, `LIVE_RISKS`, `LIVE_ISSUES`, `BLUEPRINTS`, `TIME_MACHINE_SNAPSHOTS`).
   - Filter and UI state (`activeTab`, `matrixRating`, `matrixStatus`, `activeCellFilter`, `activeTimeMachineWeek`).
   - Event bus / subscriber callbacks for state change notifications.
2. **`src/js/api.js`**: Data ingestion, syncing, and backend API clients:
   - Dynamic data loader (`loadProjectData(slug)`).
   - Live Google Drive / Sheets sync endpoints (`/api/sync-sheet`, `/api/ingest-data`).
   - Executive briefing regeneration (`/api/regenerate-briefing`).
   - Local caching and fallback resolution.
3. **`src/js/analytics.js`**: Pure, testable calculation functions (matrix scoring, burndown velocity, filter predicates) with zero DOM dependencies.
4. **`src/js/charts.js`**: Chart.js lifecycle management, canvas rendering wrappers, and SVG mappings.
5. **`src/js/modules/`**: Feature-specific UI renderers & event controllers:
   - `exec_briefing.js`: Executive cockpit banner, Google Need-to-Know (NTK) badge, 4 KPI cards, Gemini 3.5 Pro decision briefing, and audio podcast player.
   - `risk_heatmap.js`: 5×5 Risk Heatmap (Inherent vs. Residual toggles, status pills, cell selection, focus rings).
   - `risk_explorer.js`: Live Risk Explorer cards, expandable mitigation accordions, search/filter inputs, inspect button triggers, and bulk controls.
   - `issue_register.js`: Issue Register table, status pills, column sorting, and issue detail modals.
   - `performance_trends.js`: Performance Trends graphs, multi-granularity views (Weekly/Bi-Weekly/Monthly), and timeline drilldown modal.
   - `blueprint_knowledge.js`: Solution Blueprint knowledge cards, Annex mappings, and NotebookLM deep links.
   - `driver_tree.js`: Milestone 2 / CD1 Driver Tree, gate cards, deliverable status badges, and related risk links.
   - `time_machine.js`: Time Machine historical scrubbing bar, modal list, and snapshot state hydration.
   - `modals.js`: Universal item inspection modal (`openItemDetailModal`), Workspace Sync modal, Settings modal, and podcast transcript viewer.
6. **`src/js/app.js`**: Main bootstrap entry point and tab lifecycle coordinator:
   - DOM initialization and event listener bindings.
   - Deep linking and URL hash/query param router (`?project=...&tab=...&view=...`).
   - Global keyboard shortcuts and navigation controllers.

### 2.3 Clean HTML Markup Shell (`index.html`)
- Reduce `index.html` from >4,800 lines down to a clean, semantic ~600–800 line HTML shell.
- Keep structural semantic containers (`<header>`, `<nav>`, `<main>`, tab containers `#tab-exec-briefing`, `#tab-risks`, `#tab-team-google`, `#tab-issues`, `#tab-trends`, `#tab-blueprints`, `#tab-driver-tree`, `#tab-ledger`, and modal backdrops).
- Replace the giant inline `<script>` block with the modular script entry point (`<script type="module" src="src/js/app.js"></script>`).

### 2.4 Build & Development Tooling (Dual-Mode) & Cloud Run Deployment
- **Local Dev (Zero-Build)**: Direct native browser ES module serving via `python3 server.py` on port 9000.
- **Production Container Build & Asset Inclusion (MANDATORY)**:
  - Update `deploy/Dockerfile` to include `COPY src/ /usr/share/nginx/html/src/` so all ES modules are packaged into the Nginx runtime.
  - Configure `deploy/nginx.conf` with MIME types and caching headers for `application/javascript`.
  - Update `deploy/cloudbuild.yaml` and verify automated unit testing and container image generation.
- **Production Release Tagging Protocol**:
  - Release triggers adhere strictly to the tag pattern: `^project_dash/prod-.*$` (e.g. `git tag project_dash/prod-v1.0.0 && git push origin project_dash/prod-v1.0.0`).
- **Operational & Billing Guardrail**:
  - Track 90-day sandbox expiration window to ensure permanent Commonwealth billing accounts are attached in Pantheon Billing for `monaro-risk-prod` and `monaro-risk-dev`.

---

## 3. Non-Functional Requirements & Invariants

1. **Strict 100% Feature Parity**: Every UI interaction, animation, filter, modal, audio player, sync trigger, and time travel capability must function identically to baseline.
2. **Zero Regression on Backend & Tests**: All 102+ existing Python unit tests (`python3 -m unittest discover tests`) must pass cleanly.
3. **Multi-Project Agnosticism**: Dynamic multi-project routing (`?project=sample` vs `?project=f-dse`) must work seamlessly in both dev and production builds.
4. **Clean Code Standards**:
   - Proper ES6+ syntax with explicit imports and exports adhering to Google JavaScript Style Guide (`go/tsstyle`, `go/js-practices`).
   - No implicit global variables leakage.
   - Zero console errors or unhandled promise rejections on page load.

---

## 4. Acceptance Criteria
- [ ] `index.html` reduced from >4,800 lines to <900 lines of clean semantic HTML markup.
- [ ] JavaScript modularized into ~10 structured ES modules under `src/js/` with clear separation of concerns.
- [ ] Pure analytics and score calculations extracted to `src/js/analytics.js` with comprehensive unit tests.
- [ ] `deploy/Dockerfile` updated with `COPY src/ /usr/share/nginx/html/src/` ensuring ES modules are deployed to Cloud Run.
- [ ] Local development workflow verified with both native ES modules (`python3 server.py`) and dev server.
- [ ] Docker container and Cloud Build CI/CD verified with automated build stage across dev and prod release tagging.
- [ ] All 102+ existing Python unit tests pass with zero regressions.
- [ ] Complete manual and automated verification across all 7 dashboard tabs, modals, and Python ingestion APIs.

---

## 5. Out of Scope
- Rewriting the frontend in React, Angular, or Vue (maintaining vanilla HTML5 / Tailwind CSS / Chart.js architecture).
- Redesigning UI visuals or introducing new feature requests (focus is purely on architecture modernization and modularization).
