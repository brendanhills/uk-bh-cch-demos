# Implementation Plan: Decouple Dashboard Content for GitHub & Automated Gemini Ingestion Pipeline

## Phase 1: Gemini 3.5 Ingestion Engine & Prompt Orchestration (TDD)
- [ ] Task 1.1: Write unit tests for Gemini 3.5 generation, ADC client init, and offline fallback
  - [ ] Create `tests/test_gemini_generator.py` testing ADC/key credential hierarchy
  - [ ] Test structured JSON validation for multi-tone synthesis, Top 3 actions, and Sleeper Outliers
  - [ ] Test multi-speaker audio generation configuration and offline fallback behavior
- [ ] Task 1.2: Implement `scripts/gemini_generator.py`
  - [ ] Build `get_gemini_client()` supporting ADC Vertex AI (`vertexai=True`) with `GEMINI_API_KEY` fallback
  - [ ] Implement `generate_executive_synthesis()` using `gemini-3.5-flash` with structured JSON schemas
  - [ ] Implement `generate_multispeaker_podcast()` with `MultiSpeakerVoiceConfig` (`Puck` / `Aoede`)
  - [ ] Implement deterministic rule-based offline fallback synthesizer
- [ ] Task 1.3: Update Prompt Templates
  - [ ] Refactor `prompts/exec_summary_prompt.md` for JSON schema output compatibility
  - [ ] Create `prompts/podcast_prompt.md` for dual-host executive dialogue generation
- [ ] Task 1.4: Integrate Gemini generation into `scripts/ingest_weekly_report.py`
  - [ ] Calculate live risk score deltas (Inherent vs Residual), eventuated counts, and baseline shifts
  - [ ] Call `gemini_generator.py` during ingestion and enrich the new snapshot entry
  - [ ] Save output into target project snapshot JSON and write audio to `assets/podcast_w<N>.mp3`
- [ ] Task 1.5: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 2: Public Showcase Dataset Creation (`data/sample/` - Project Aurora)
- [ ] Task 2.1: Write data integrity unit test for Project Aurora sample schema
  - [ ] Create `tests/test_sample_dataset.py` validating all JSON schema invariants
- [ ] Task 2.2: Create `data/sample/config.json`
  - [ ] Define Project Aurora branding, titles, theme colors, external URLs, and 4 KPI pillars
  - [ ] Configure feature toggle flags for all 8 tabs
- [ ] Task 2.3: Create `data/sample/risks.json` & `data/sample/issues.json`
  - [ ] Author 25+ realistic 5×5 risk matrix records across Cloud, Security, Data, and Architecture
  - [ ] Author 10+ operational blocker issues with remediation plans and target dates
- [ ] Task 2.4: Create `data/sample/snapshots.json`
  - [ ] Populate 6 weeks of historical longitudinal snapshots (`W22`–`W27`)
  - [ ] Include multi-tone AI syntheses, Top 3 actions, Sleeper Outliers, and podcast transcripts
- [ ] Task 2.5: Create `data/sample/driver_tree.json` & `data/sample/knowledge.json`
  - [ ] Define 24 contractual capability gates across CD1 and CD1.5
  - [ ] Define 10 solution blueprints mapped to active sample risks
- [ ] Task 2.6: Provide sample audio briefing
  - [ ] Add generic sample audio snippet `data/sample/podcast_sample.mp3`
- [ ] Task 2.7: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: Presentation Engine Decoupling & Dynamic Client Loader (`index.html`)
- [ ] Task 3.1: Implement `async function loadDashboardData()` in `index.html`
  - [ ] Parse URL search parameters (`?data=sample`, `?data=local`, `?project=<slug>`)
  - [ ] Fetch `config.json` and domain data files asynchronously with error fallback
- [ ] Task 3.2: Strip all embedded static datasets from `index.html`
  - [ ] Remove hardcoded `LIVE_RISKS`, `LIVE_TEAM_GOOGLE_RISKS`, `NOTEBOOK_CATALOG`, `BUNDLE_ANNEX_MAPPING`, `WEEKLY_SNAPSHOTS`, `PODCAST_SCRIPTS`, `GEMINI_PARAGRAPHS`
  - [ ] Bind in-memory global state to loaded JSON datasets
- [ ] Task 3.3: Implement Dynamic Tab Rendering & KPI Pillars
  - [ ] Conditionally render navigation tabs based on `config.features[tab].enabled`
  - [ ] Dynamically render global header branding, vendor badges, and 4 KPI summary cards
- [ ] Task 3.4: Dynamic Executive Briefing & Time Machine Integration
  - [ ] Wire Executive Briefing hero card, tone selector, Top 3 actions, and Sleeper Outliers to active snapshot
  - [ ] Wire neural podcast player and transcript modal to active snapshot dialogue array
  - [ ] Ensure Time Machine history rewinds and restores dynamic snapshots smoothly
- [ ] Task 3.5: AST Syntax and DOM Validation
  - [ ] Validate inline JavaScript using `node -c`
- [ ] Task 3.6: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 4: Backend Server Parameterization & On-Demand APIs (`server.py`)
- [ ] Task 4.1: Write unit tests for server routes
  - [ ] Create `tests/test_server_parameterized.py` for `/api/sync-sheet`, `/api/ingest-report`, and `/api/regenerate-briefing`
- [ ] Task 4.2: Parameterize `server.py`
  - [ ] Remove all hardcoded Google Drive IDs, Sheet URLs, and specific folder structures
  - [ ] Read active project directory and credentials dynamically from `.env` and `config.json`
- [ ] Task 4.3: Implement `POST /api/regenerate-briefing` Endpoint
  - [ ] Allow 1-click on-demand AI briefing re-generation for any week from the web UI
- [ ] Task 4.4: Update CLI scripts (`scripts/sync_notebook.py` & `scripts/ingest_weekly_report.py`)
  - [ ] Add `--project` and `--data-dir` arguments
- [ ] Task 4.5: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 5: Repository Sanitization, Git Hygiene & Documentation
- [ ] Task 5.1: Configure Strict `.gitignore`
  - [ ] Exclude `.env`, `data/local/`, private MP3s, and local sync caches
- [ ] Task 5.2: Create `.env.example`
  - [ ] Document ADC authentication, `GEMINI_API_KEY`, model options, and project configuration
- [ ] Task 5.3: Rewrite Open-Source `README.md`
  - [ ] Document project architecture, zero-server static hosting, local quickstart, dataset customization, and ingestion pipeline
- [ ] Task 5.4: End-to-End Integration Verification
  - [ ] Run complete test suite: `python3 -m unittest discover tests`
  - [ ] Verify both sample mode and local mode execute with zero errors
- [ ] Task 5.5: Final Track Review & Checkpoint
