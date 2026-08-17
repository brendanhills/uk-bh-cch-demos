# Specification: Decouple Dashboard Content for GitHub & Automated Gemini Ingestion Pipeline

## 1. Overview & Strategic Purpose
This track combines two critical architectural capabilities into a single unified delivery:
1. **GitHub Open-Source Decoupling**: Completely separates the dashboard's high-performance presentation engine from proprietary project content, customer data, and internal infrastructure IDs. It establishes a project-based data structure (`data/<project_slug>/`), a modular feature-flagged configuration system (`config.json`), and a realistic, production-grade mock dataset (**Project Aurora**) in `data/sample/`, enabling seamless sharing and hosting on GitHub.
2. **Unified Ingestion-Time Pre-Computation & Gemini 3.5 Generation Pipeline**: Introduces a single master orchestrator (`scripts/ingest_data.py --project=<name>`) that reads project configuration, syncs external streams (Google Sheets, Drive Reports, Gemini Notebooks), runs **Gemini 3.5 Flash** (via Google Cloud ADC) to generate executive briefings and dual-host audio, and **pre-computes all analytical metrics** (5×5 heatmaps, trends, burndown, bundle mappings, search indexes) so the web UI renders with maximum responsiveness and 100% mathematical consistency.

---

## 2. Functional Requirements

### 2.1. Presentation Engine Decoupling (`index.html`)
- **FR 1.1 - Zero Hardcoded Content**: Strip all embedded JavaScript datasets (`LIVE_RISKS`, `LIVE_TEAM_GOOGLE_RISKS`, `NOTEBOOK_CATALOG`, `BUNDLE_ANNEX_MAPPING`, `WEEKLY_SNAPSHOTS`, `PODCAST_SCRIPTS`, `GEMINI_PARAGRAPHS`) and hardcoded project strings from `index.html`.
- **FR 1.2 - Dynamic Client-Side Dataset Loader**: Implement `async function loadDashboardData()` in `index.html` that fetches `config.json` and project data files (`risks.json`, `issues.json`, `snapshots.json`, `driver_tree.json`, `knowledge.json`, `precomputed_analytics.json`).
- **FR 1.3 - Project Selector Query Routing**: Support clean project switching via URL parameter: `?project=sample` (default for GitHub/public) or `?project=f-dse` or custom `?project=<slug>`. When omitted, falls back to `ACTIVE_PROJECT` configured in `.env` (defaulting to `sample`).
- **FR 1.4 - Modular Feature-Flagged Tabs**: Render dashboard navigation tabs dynamically based on `config.features[tab].enabled`, supporting optional tabs (Secondary Vendor Matrix, Knowledge Base, Driver Tree, Whole Ledger, and Audio Player).
- **FR 1.5 - Dynamic KPI Pillars & Branding**: Populate global titles, subtitles, logo icons, vendor badge labels, and 4-pillar executive KPIs dynamically from `config.json`.

### 2.2. Public Showcase Dataset (`data/sample/` — Project Aurora)
- **FR 2.1 - Realistic Enterprise Scope**: Create a complete, fictional enterprise cloud & AI transformation program dataset (**Project Aurora**) containing:
  - **`config.json`**: Enterprise Cloud Program branding, external links, KPI pillars, and feature flags.
  - **`risks.json`**: 25+ realistic 5×5 risk matrix records across Architecture, Security, Cloud Infrastructure, Data Engineering, Governance, and Sovereign Logistics.
  - **`issues.json`**: 10+ operational blocker tickets with severity ratings, owners, and remediation action plans.
  - **`snapshots.json`**: 6 weeks of historical longitudinal snapshots (`W22`–`W27`) with RAG statuses, KPI movements, baseline diffs, and AI syntheses.
  - **`driver_tree.json`**: Tier 0/1/2/3 capability gates across Capability Drops (CD1 & CD1.5).
  - **`knowledge.json`**: 10 solution blueprints (Security ATO, Vertex AI Enclave, Diode Ingestion, Network Interconnects) mapped to active risks.
  - **`podcast_sample.mp3`**: Showcase audio file and complete dialogue transcript.
  - **`precomputed_analytics.json`**: Pre-computed 5×5 matrices, velocity charts, and search indexes.

### 2.3. Unified Ingestion-Time Pre-Computation Suite
To maximize UI responsiveness and eliminate runtime mathematical variance, the ingestion pipeline will pre-compute and store analytical models into `precomputed_analytics.json`:
- **FR 3.1 - 5×5 Matrix Aggregation & Coordinate Mapping**: Pre-computes cell maps `(likelihood, consequence) -> [item_ids]`, inherent vs residual counts, and severity band totals (Critical ≥18, High, Medium, Low) for all registers.
- **FR 3.2 - Longitudinal Trend Series & Burndown Cache**: Pre-computes Chart.js-ready data series for Backlog Volume, Intake vs Closures, Net Burndown Score (Inherent vs Residual), and Cause Category distributions across Weekly, Bi-Weekly, and Monthly intervals.
- **FR 3.3 - Blueprint Bundle Risk Mapping & Counter Cache**: Pre-computes bidirectional mappings between solution blueprints (Bundles A through L) and active risk IDs with active counter badges.
- **FR 3.4 - Schedule Squeeze & Gate Float Metrics**: Pre-computes timeline compression days, milestone variances, and baseline shift diffs between reporting weeks.
- **FR 3.5 - Pre-Indexed Search Tokens & CSV Export Data**: Pre-indexes searchable fields for instant filtering and caches pre-formatted CSV ledger exports.

### 2.4. Automated Gemini 3.5 Generation Engine (`scripts/gemini_generator.py`)
- **FR 4.1 - ADC-First Authentication**: Authenticates via Google Cloud Application Default Credentials (`genai.Client(vertexai=True)`), with secondary fallback to `GEMINI_API_KEY`. Clear diagnostic error logging if credentials are missing.
- **FR 4.2 - Gemini 3.5 Flash Model**: Uses `gemini-3.5-flash` as default (configurable via `GEMINI_MODEL` in `.env`, with support for `gemini-3.1-pro-preview`).
- **FR 4.3 - Multi-Tone Executive Synthesis**: Automatically parses weekly metrics, calculates Inherent ➔ Residual score compression (Δ), compares with preceding baseline week, and generates structured JSON with Executive, Technical, and Governance summaries.
- **FR 4.4 - Critical Attention Items & Sleeper Outlier**: Generates Top 3 actionable priorities with deliverable citation references (e.g. `Ref 1.10b ↗`) and flags high-risk green-to-red leading indicators.
- **FR 4.5 - Native Multi-Speaker Audio Briefing**: Generates dual-host dialogue transcript (`Alex` and `Jordan`) and native multi-speaker audio using `types.SpeechConfig(multi_speaker_voice_config=...)` with prebuilt voices `Puck` and `Aoede`, saving to `data/<project>/assets/podcast_w<N>.mp3`.

### 2.5. Project-Scoped Master Ingestion Orchestrator (`scripts/ingest_data.py`)
- **FR 5.1 - Unified Multi-Project Ingestion CLI**: Implement `scripts/ingest_data.py` supporting single or batch multi-project ingestion:
  - **Explicit Project**: `--project=<slug>` targets a specific project (e.g. `--project=f-dse`).
  - **Default Projects from .env**: When `--project` is omitted, it reads `DEFAULT_PROJECTS` (or `PROJECTS`, e.g. `DEFAULT_PROJECTS="f-dse,sample"`) from `.env` and ingests all configured projects sequentially in one command. If unconfigured, falls back to `sample`.
  - **Execution Steps Per Project**:
    1. Reads `data/<project>/config.json` to identify external data sources (Google Sheet IDs, Drive folder IDs, Gemini Notebook IDs).
    2. Ingests and synchronizes all project datasets into `data/<project>/`.
    3. Executes the Gemini 3.5 generation pipeline for the latest reporting week.
    4. Runs the Ingestion Pre-Computation Suite to build `data/<project>/precomputed_analytics.json`.
- **FR 5.2 - Backend Ingestion & Regeneration APIs (`server.py`)**:
  - `POST /api/ingest-data`: Webhook triggering full ingestion for a given project slug.
  - `POST /api/regenerate-briefing`: Allows 1-click on-demand AI briefing re-generation for any week directly from the dashboard web UI.
- **FR 5.3 - Parameterized Sync Endpoints**: Refactor `/api/sync-sheet`, `/api/check-drive-sync`, and `/api/sync-notebook` in `server.py` to operate on the active project directory.

### 2.6. Repository Sanitization & Git Hygiene
- **FR 6.1 - Private Data Exclusion**: Update `.gitignore` to strictly exclude `.env`, private project folders (e.g. `data/f-dse/`), private audio MP3s, and internal sync caches (`data/drive/`, `data/sheets/`).
- **FR 6.2 - Environment Template**: Provide documented `.env.example` with ADC and API key configuration guides.
- **FR 6.3 - Open Source Documentation**: Provide a clean, comprehensive `README.md` detailing architecture, setup, dataset schemas, and customization.

---

## 3. Non-Functional & Quality Requirements
- **NFR 1 - Zero-Build Architecture**: Frontend remains a pure HTML5/Tailwind/Chart.js single-page application requiring zero node/npm build steps.
- **NFR 2 - Instant Page Load (<5ms)**: All client navigation, Time Machine time-travel, heatmap rendering, and tab switching execute instantly using pre-computed analytics without runtime calculation lag.
- **NFR 3 - Strict Credential Handling**: Ingestion requires valid ADC credentials (or `GEMINI_API_KEY`) for AI synthesis, logging clear error diagnostics if credentials fail.
- **NFR 4 - AST / JavaScript Syntax Guard**: All inline scripts inside `index.html` must pass `node -c` syntax validation with zero template literal escaping bugs.

---

## 4. Acceptance Criteria
- [ ] `index.html` contains zero hardcoded project strings or risk data arrays.
- [ ] Running `python3 scripts/ingest_data.py --project=sample` ingests sample sources, runs Gemini 3.5 synthesis, and builds `precomputed_analytics.json`.
- [ ] Running `python3 scripts/ingest_data.py --project=f-dse` executes full ingestion for the F-DSE project using its dedicated `data/f-dse/config.json`.
- [ ] Loading `index.html?project=sample` renders the **Project Aurora** sample dataset flawlessly across all 8 tabs.
- [ ] Loading `index.html?project=f-dse` loads the complete F-DSE project dataset.
- [ ] 5×5 matrices, trends, and burndown charts render instantaneously from pre-computed analytical caches.
- [ ] `scripts/gemini_generator.py` successfully initializes with ADC and generates structured synthesis using `gemini-3.5-flash`.
- [ ] Automated test suite verifies ingestion orchestration, sample dataset integrity, ADC handling, and server routes.
- [ ] `.gitignore` and `.env.example` ensure zero leakage of private project data.
