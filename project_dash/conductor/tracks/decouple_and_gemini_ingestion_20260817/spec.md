# Specification: Decouple Dashboard Content for GitHub & Automated Gemini Ingestion Pipeline

## 1. Overview & Strategic Purpose
This track combines two critical architectural capabilities into a single unified delivery:
1. **GitHub Open-Source Decoupling**: Completely separates the dashboard's high-performance presentation engine from proprietary project content, customer data, and internal infrastructure IDs. It provides a modular, feature-flagged configuration system () and a realistic, production-grade mock dataset (**Project Aurora — Enterprise AI & Cloud Transformation**) in `data/sample/`, enabling seamless sharing and hosting on GitHub.
2. **Automated Ingestion-Time Gemini 3.5 Generation**: Upgrades the weekly ingestion pipeline to automatically generate executive decision syntheses, Top 3 attention items, sleeper outliers, and native multi-speaker dual-host audio briefings using **Gemini 3.5 Flash** (via Google Cloud ADC with API key fallback), saving results into snapshot storage for instantaneous, zero-latency client rendering.

---

## 2. Functional Requirements

### 2.1. Presentation Engine Decoupling (`index.html`)
- **FR 1.1 - Zero Hardcoded Content**: Strip all embedded JavaScript datasets (`LIVE_RISKS`, `LIVE_TEAM_GOOGLE_RISKS`, `NOTEBOOK_CATALOG`, `BUNDLE_ANNEX_MAPPING`, `WEEKLY_SNAPSHOTS`, `PODCAST_SCRIPTS`, `GEMINI_PARAGRAPHS`) and hardcoded project strings from `index.html`.
- **FR 1.2 - Dynamic Client-Side Dataset Loader**: Implement `async function loadDashboardData()` in `index.html` that fetches `config.json` and domain data files (`risks.json`, `issues.json`, `snapshots.json`, `driver_tree.json`, `knowledge.json`).
- **FR 1.3 - Dynamic Project / Sample Selector**: Support runtime dataset switching via query parameters: `?data=sample` (default for GitHub/public) or `?data=local` / `?project=<slug>`.
- **FR 1.4 - Modular Feature-Flagged Tabs**: Render dashboard navigation tabs dynamically based on `config.features[tab].enabled`, supporting optional tabs (Secondary Vendor Matrix, Knowledge Base, Driver Tree, Whole Ledger, and Audio Player).
- **FR 1.5 - Dynamic KPI Pillars & Branding**: Populate global titles, subtitles, logo icons, vendor badge labels, and 4-pillar executive KPIs from `config.json`.

### 2.2. Public Showcase Dataset (`data/sample/` — Project Aurora)
- **FR 2.1 - Realistic Enterprise Scope**: Create a complete, fictional enterprise cloud & AI transformation program dataset (**Project Aurora**) containing:
  - **`config.json`**: Enterprise Cloud Program branding, links, and KPI pillar definitions.
  - **`risks.json`**: 25+ realistic 5×5 risk matrix records across Architecture, Security, Cloud Infrastructure, Data Engineering, Governance, and Sovereign Logistics.
  - **`issues.json`**: 10+ operational blocker tickets with severity ratings, owners, and remediation action plans.
  - **`snapshots.json`**: 6 weeks of historical longitudinal snapshots (`W22`–`W27`) with RAG statuses, KPI movements, baseline diffs, and AI syntheses.
  - **`driver_tree.json`**: Tier 0/1/2/3 capability gates across Capability Drops (CD1 & CD1.5).
  - **`knowledge.json`**: 10 solution blueprints (Security ATO, Vertex AI Enclave, Diode Ingestion, Network Interconnects) mapped to active risks.
  - **`podcast_sample.mp3`**: Showcase audio file and complete dialogue transcript.

### 2.3. Automated Ingestion-Time Gemini 3.5 Generation (`scripts/gemini_generator.py`)
- **FR 3.1 - ADC-First Authentication**: Primary authentication uses Google Cloud Application Default Credentials (`genai.Client(vertexai=True)`), with secondary fallback to `GEMINI_API_KEY` and tertiary rule-based offline synthesis.
- **FR 3.2 - Gemini 3.5 Flash Model**: Uses `gemini-3.5-flash` as default (configurable via `GEMINI_MODEL` in `.env`, with support for `gemini-3.1-pro-preview`).
- **FR 3.3 - Multi-Tone Executive Synthesis**: Automatically parses weekly metrics, calculates Inherent ➔ Residual score compression (Δ), compares with preceding baseline week, and generates structured JSON with Executive, Technical, and Governance summaries.
- **FR 3.4 - Critical Attention Items & Sleeper Outlier**: Generates Top 3 actionable priorities with deliverable citation references (e.g. `Ref 1.10b ↗`) and flags high-risk green-to-red leading indicators.
- **FR 3.5 - Native Multi-Speaker Audio Briefing**: Generates dual-host dialogue transcript (`Alex` and `Jordan`) and native multi-speaker audio using `types.SpeechConfig(multi_speaker_voice_config=...)` with prebuilt voices `Puck` and `Aoede`, saving to `assets/podcast_w<N>.mp3`.

### 2.4. Ingestion Server & Management Tools (`server.py` & CLI)
- **FR 4.1 - Parameterized Sync & Ingestion Endpoints**: Refactor `/api/sync-sheet`, `/api/check-drive-sync`, `/api/sync-notebook`, and `/api/ingest-report` in `server.py` to read external IDs and credentials dynamically from `.env` and target project directories.
- **FR 4.2 - On-Demand Regeneration API**: Add `POST /api/regenerate-briefing` to re-synthesize AI summaries for any target week directly from the dashboard web UI.
- **FR 4.3 - Project-Scoped CLI Tools**: Update `scripts/ingest_weekly_report.py` and `scripts/sync_notebook.py` with `--project` and `--data-dir` flags.

### 2.5. Repository Sanitization & Git Hygiene
- **FR 5.1 - Private Data Exclusion**: Update `.gitignore` to strictly exclude `.env`, `data/local/`, private audio MP3s, and internal sync caches (`data/drive/`, `data/sheets/`).
- **FR 5.2 - Environment Template**: Provide documented `.env.example` with ADC and API key configuration guides.
- **FR 5.3 - Open Source Documentation**: Provide a clean, comprehensive `README.md` detailing architecture, setup, dataset schemas, and customization.

---

## 3. Non-Functional & Quality Requirements
- **NFR 1 - Zero-Build Architecture**: Frontend remains a pure HTML5/Tailwind/Chart.js single-page application requiring zero node/npm build steps.
- **NFR 2 - Instant Page Load**: All client navigation, Time Machine time-travel, and tab switching execute locally in <5ms without blocking on external LLM API calls.
- **NFR 3 - Offline Resilience**: If no internet connection or Gemini API credentials are provided, ingestion and the dashboard operate 100% reliably with deterministic rule-based summaries.
- **NFR 4 - AST / JavaScript Syntax Guard**: All inline scripts inside `index.html` must pass `node -c` syntax validation with zero template literal escaping bugs.

---

## 4. Acceptance Criteria
- [ ] `index.html` contains zero hardcoded project strings or risk data arrays.
- [ ] Loading `index.html` without query parameters renders the **Project Aurora** sample dataset flawlessly across all 8 tabs.
- [ ] Loading `index.html?data=local` loads private project data seamlessly from `data/local/`.
- [ ] `scripts/gemini_generator.py` successfully initializes with ADC (and key fallback) and generates structured synthesis using `gemini-3.5-flash`.
- [ ] Running `scripts/ingest_weekly_report.py` ingests a report, computes risk score deltas, calls Gemini, and saves enriched snapshot into `snapshots.json`.
- [ ] Automated test suite verifies data loading, sample dataset integrity, ADC/fallback handling, and server routes.
- [ ] `.gitignore` and `.env.example` prevent any leakage of proprietary project data or credentials.
