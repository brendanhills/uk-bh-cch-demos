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
- [ ] Task 2.3: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: Project Aurora Sample Dataset & Directory Isolation (`data/`)
- [ ] Task 3.1: Write data integrity unit test for Project Aurora sample schema
  - [x] Create `tests/test_sample_dataset.py` validating all JSON schema invariants
- [ ] Task 3.2: Create `data/sample/config.json`
  - [ ] Define Project Aurora branding, titles, theme colors, external URLs, and 4 KPI pillars
  - [ ] Configure feature toggle flags for all 8 tabs
- [ ] Task 3.3: Create `data/sample/risks.json` & `data/sample/issues.json`
  - [ ] Author 25+ realistic 5×5 risk matrix records across Cloud, Security, Data, and Architecture
  - [ ] Author 10+ operational blocker issues with remediation plans and target dates
- [ ] Task 3.4: Create `data/sample/snapshots.json`, `driver_tree.json`, and `knowledge.json`
  - [ ] Populate 6 weeks of historical longitudinal snapshots (`W22`–`W27`) with AI syntheses
  - [ ] Define 24 contractual capability gates across CD1 and CD1.5
  - [ ] Define 10 solution blueprints mapped to active sample risks
- [ ] Task 3.5: Populate `data/sample/precomputed_analytics.json` & sample audio
  - [ ] Run `ingest_data.py --project=sample` to build baseline pre-computed cache
  - [ ] Add generic sample audio snippet `data/sample/podcast_sample.mp3`
- [ ] Task 3.6: Migrate existing F-DSE project files into isolated `data/f-dse/`
  - [ ] Move proprietary live registers, snapshots, and blueprints into `data/f-dse/`
- [ ] Task 3.7: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 4: Presentation Engine Decoupling & Dynamic Project Routing (`index.html`)
- [ ] Task 4.1: Implement `async function loadDashboardData()` in `index.html`
  - [ ] Parse URL search parameters (`?project=sample`, `?project=f-dse`, `?project=<slug>`)
  - [ ] Load `config.json` and `precomputed_analytics.json` from the target project directory
- [ ] Task 4.2: Strip all embedded static datasets from `index.html`
  - [ ] Remove hardcoded `LIVE_RISKS`, `LIVE_TEAM_GOOGLE_RISKS`, `NOTEBOOK_CATALOG`, `BUNDLE_ANNEX_MAPPING`, `WEEKLY_SNAPSHOTS`, `PODCAST_SCRIPTS`, `GEMINI_PARAGRAPHS`
  - [ ] Bind in-memory global state to loaded JSON datasets
- [ ] Task 4.3: Implement Dynamic Tab Rendering & KPI Pillars
  - [ ] Conditionally render navigation tabs based on `config.features[tab].enabled`
  - [ ] Dynamically render global header branding, vendor badges, and 4 KPI summary cards
- [ ] Task 4.4: Dynamic Executive Briefing & Time Machine Integration
  - [ ] Wire Executive Briefing hero card, tone selector, Top 3 actions, and Sleeper Outliers to active snapshot
  - [ ] Wire neural podcast player and transcript modal to active snapshot dialogue array
  - [ ] Ensure Time Machine history rewinds and restores dynamic snapshots smoothly
- [ ] Task 4.5: AST Syntax and DOM Validation
  - [ ] Validate inline JavaScript using `node -c`
- [ ] Task 4.6: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 5: Backend Server Parameterization & On-Demand APIs (`server.py`)
- [ ] Task 5.1: Write unit tests for server routes
  - [x] Create `tests/test_server_parameterized.py` for `/api/sync-sheet`, `/api/ingest-data`, and `/api/regenerate-briefing`
- [ ] Task 5.2: Parameterize `server.py`
  - [ ] Remove all hardcoded Google Drive IDs, Sheet URLs, and specific folder structures
  - [ ] Read active project directory dynamically from `.env` and `config.json`
- [ ] Task 5.3: Implement `POST /api/ingest-data` & `POST /api/regenerate-briefing` Endpoints
  - [ ] Allow triggering `ingest_data.py` and on-demand AI briefing regeneration from web UI
- [ ] Task 5.4: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 6: Repository Sanitization, Git Hygiene & Documentation
- [ ] Task 6.1: Configure Strict `.gitignore`
  - [ ] Exclude `.env`, private project folders (`data/f-dse/`, `data/local/`), private MP3s, and local sync caches
- [ ] Task 6.2: Create `.env.example`
  - [ ] Document ADC authentication, `ACTIVE_PROJECT`, model options, and project configuration
- [ ] Task 6.3: Rewrite Open-Source `README.md`
  - [ ] Document project architecture, zero-server static hosting, local quickstart, dataset customization, and ingestion pipeline
- [ ] Task 6.4: End-to-End Integration Verification
  - [ ] Run complete test suite: `python3 -m unittest discover tests`
  - [ ] Verify both sample mode (`?project=sample`) and private mode (`?project=f-dse`) execute with zero errors
- [ ] Task 6.5: Final Track Review & Checkpoint
