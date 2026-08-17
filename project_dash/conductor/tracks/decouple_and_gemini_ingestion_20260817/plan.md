# Implementation Plan: Decouple Dashboard Content for GitHub & Automated Gemini Ingestion Pipeline

## Phase 1: Gemini 3.5 Ingestion Engine & Pre-Computation Suite (TDD)
- [x] Task 1.1: Write unit tests for Gemini 3.5 generation and pre-computation engine
  - [x] Create `tests/test_gemini_generator.py` testing ADC/key credential initialization
  - [x] Test structured JSON validation for multi-tone synthesis, Top 3 actions, and Sleeper Outliers using `gemini-3.5-flash`
  - [x] Create `tests/test_precomputed_analytics.py` validating 5×5 matrix cell coordinates, longitudinal trend series, and burndown calculations
- [x] Task 1.2: Implement `scripts/gemini_generator.py`
  - [x] Build `get_gemini_client()` supporting ADC Vertex AI (`vertexai=True`) with `GEMINI_API_KEY` fallback
  - [x] Implement `generate_executive_synthesis()` using `gemini-3.5-flash` with structured JSON schemas
  - [x] Implement `generate_multispeaker_podcast()` with `MultiSpeakerVoiceConfig` (`Puck` / `Aoede`)
- [x] Task 1.3: Implement Ingestion Pre-Computation Engine in `scripts/precompute_analytics.py`
  - [x] Pre-calculate 5×5 heatmap cell coordinate maps, inherent vs residual counts, and severity band totals
  - [x] Pre-calculate Chart.js time series (Intake, Closures, Backlog, Burndown Score, Cause Categories) across Weekly, Bi-Weekly, and Monthly granularities
  - [x] Pre-calculate solution blueprint bundle-to-risk mappings and active counter badges
  - [x] Pre-calculate schedule squeeze float metrics and full-text search token indexes
- [x] Task 1.4: Update Prompt Templates
  - [x] Refactor `prompts/exec_summary_prompt.md` for JSON schema output compatibility
  - [x] Create `prompts/podcast_prompt.md` for dual-host executive dialogue generation
- [x] Task 1.5: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 2: Master Ingestion Orchestrator (`scripts/ingest_data.py`)
- [x] Task 2.1: Write unit test for project ingestion orchestrator
  - [x] Create `tests/test_ingest_data.py` testing project configuration parsing and multi-stream sync
- [x] Task 2.2: Implement Master Ingestion CLI `scripts/ingest_data.py`
  - [x] Support explicit `--project=<slug>` or default to comma-separated `DEFAULT_PROJECTS` list from `.env` (fallback to `sample`)
  - [x] Iterate through target projects and load `data/<project>/config.json`
  - [x] Ingest configured Google Sheets into `data/<project>/risks.json` and `data/<project>/issues.json`
  - [x] Ingest configured Google Drive reports into `data/<project>/snapshots.json`
  - [x] Ingest configured Gemini Notebooks into `data/<project>/knowledge.json`
  - [x] Trigger `gemini_generator.py` for latest snapshot AI synthesis and multi-speaker audio
  - [x] Trigger `precompute_analytics.py` to generate `data/<project>/precomputed_analytics.json`
- [x] Task 2.3: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: Project Aurora Sample Dataset & Directory Isolation (`data/`)
- [x] Task 3.1: Write data integrity unit test for Project Aurora sample schema
  - [x] Create `tests/test_sample_dataset.py` validating all JSON schema invariants
- [x] Task 3.2: Create `data/sample/config.json`
  - [x] Define Project Aurora branding, titles, theme colors, external URLs, and 4 KPI pillars
  - [x] Configure feature toggle flags for all 8 tabs
- [x] Task 3.3: Create `data/sample/risks.json` & `data/sample/issues.json`
  - [x] Author 25+ realistic 5×5 risk matrix records across Cloud, Security, Data, and Architecture
  - [x] Author 10+ operational blocker issues with remediation plans and target dates
- [x] Task 3.4: Create `data/sample/snapshots.json`, `driver_tree.json`, and `knowledge.json`
  - [x] Populate 6 weeks of historical longitudinal snapshots (`W22`–`W27`) with AI syntheses
  - [x] Define 24 contractual capability gates across CD1 and CD1.5
  - [x] Define 10 solution blueprints mapped to active sample risks
- [x] Task 3.5: Populate `data/sample/precomputed_analytics.json` & sample audio
  - [x] Run `ingest_data.py --project=sample` to build baseline pre-computed cache
  - [x] Add generic sample audio snippet `data/sample/podcast_sample.mp3`
- [x] Task 3.6: Migrate existing F-DSE project files into isolated `data/f-dse/`
  - [x] Move proprietary live registers, snapshots, and blueprints into `data/f-dse/`
- [x] Task 3.7: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 4: Presentation Engine Decoupling & Dynamic Project Routing (`index.html`)
- [x] Task 4.1: Implement `async function loadDashboardData()` in `index.html`
  - [x] Parse URL search parameters (`?project=sample`, `?project=f-dse`, `?project=<slug>`)
  - [x] Load `config.json` and `precomputed_analytics.json` from the target project directory
- [x] Task 4.2: Strip all embedded static datasets from `index.html`
  - [x] Remove hardcoded `LIVE_RISKS`, `LIVE_TEAM_GOOGLE_RISKS`, `NOTEBOOK_CATALOG`, `BUNDLE_ANNEX_MAPPING`, `WEEKLY_SNAPSHOTS`, `PODCAST_SCRIPTS`, `GEMINI_PARAGRAPHS`
  - [x] Bind in-memory global state to loaded JSON datasets
- [x] Task 4.3: Implement Dynamic Tab Rendering & KPI Pillars
  - [x] Conditionally render navigation tabs based on `config.features[tab].enabled`
  - [x] Dynamically render global header branding, vendor badges, and 4 KPI summary cards
- [x] Task 4.4: Dynamic Executive Briefing & Time Machine Integration
  - [x] Wire Executive Briefing hero card, tone selector, Top 3 actions, and Sleeper Outliers to active snapshot
  - [x] Wire neural podcast player and transcript modal to active snapshot dialogue array
  - [x] Ensure Time Machine history rewinds and restores dynamic snapshots smoothly
- [x] Task 4.5: AST Syntax and DOM Validation
  - [x] Validate inline JavaScript using `node -c`
- [x] Task 4.6: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 5: Backend Server Parameterization & On-Demand APIs (`server.py`)
- [x] Task 5.1: Write unit tests for server routes
  - [x] Create `tests/test_server_parameterized.py` for `/api/sync-sheet`, `/api/ingest-data`, and `/api/regenerate-briefing`
- [x] Task 5.2: Parameterize `server.py`
  - [x] Remove all hardcoded Google Drive IDs, Sheet URLs, and specific folder structures
  - [x] Read active project directory dynamically from `.env` and `config.json`
- [x] Task 5.3: Implement `POST /api/ingest-data` & `POST /api/regenerate-briefing` Endpoints
  - [x] Allow triggering `ingest_data.py` and on-demand AI briefing regeneration from web UI
- [x] Task 5.4: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 6: Repository Sanitization, Git Hygiene & Documentation
- [x] Task 6.1: Configure Strict `.gitignore`
  - [x] Exclude `.env`, private project folders (`data/f-dse/`, `data/local/`), private MP3s, and local sync caches
- [x] Task 6.2: Create `.env.example`
  - [x] Document ADC authentication, `ACTIVE_PROJECT`, model options, and project configuration
- [x] Task 6.3: Rewrite Open-Source `README.md`
  - [x] Document project architecture, zero-server static hosting, local quickstart, dataset customization, and ingestion pipeline
- [x] Task 6.4: End-to-End Integration Verification
  - [x] Run complete test suite: `python3 -m unittest discover tests`
  - [x] Verify both sample mode (`?project=sample`) and private mode (`?project=f-dse`) execute with zero errors
- [x] Task 6.5: Final Track Review & Checkpoint
