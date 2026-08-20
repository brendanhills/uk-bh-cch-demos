# System Specification & Architecture Design Document (SDD)
# Project Dash — Decoupled Risk Intelligence & Governance Platform

> **Document Status:** Draft for Manual Review  
> **Target Version:** 2.0 (Post-Baseline Multi-Project Release)  
> **Last Updated:** 2026-08-19  
> **Primary Stakeholders:** Allison Innes (`allins@google.com`), Steve Deacon (`sdeacon@google.com`), Wayne Davis (`waynedavis@google.com`), Brendan Hills (`brendanhills@google.com`)

---

## 1. Executive Summary & Vision

### 1.1 Purpose & Data Confidentiality Invariant
**Project Dash** is an ultra-responsive, decoupled executive governance and operational risk intelligence platform. It unifies fragmented weekly PDF reports, Google Sheets risk registers, contractual milestones, and NotebookLM knowledge documents into an interactive, real-time decision cockpit — providing comprehensive 5×5 risk matrices, longitudinal burndown analytics, contractual delivery driver trees, and integrated **Google Gemini AI** executive decision briefings.

### 1.2 Mandatory Architectural & Operational Invariants
1. **Turnkey Self-Service Handover (Zero Author On-Call)**:
   - The platform MUST be fully operable and maintainable by the Monaro / F-DSE team (`allins@`, `sdeacon@`, `waynedavis@`) after handover without requiring ongoing support, on-call maintenance, or code changes from the author (`brendanhills@`).
   - **Self-Service User Management**: Adding or removing stakeholders is performed directly in the [Google Groups UI](https://groups.google.com/a/google.com/g/monaro-risk-dev), instantly updating IAP authentication without touching GCP IAM.
   - **Self-Service Ingestion**: Weekly reports and Google Sheets updates are ingested directly through the web UI with zero CLI requirements.
   - **Operator Documentation**: Supported by a complete operator manual ([`docs/HANDOVER_GUIDE.md`](./docs/HANDOVER_GUIDE.md)) and stakeholder presentation guide ([`docs/TEAM_PRESENTATION_GUIDE.md`](./docs/TEAM_PRESENTATION_GUIDE.md)).
   - **Automated CI/CD**: Cloud Build automatically builds, tests, and deploys updates on git push, eliminating manual container or server management.
2. **Mandatory Data Confidentiality & Access Restriction**:
   - The Monaro / F-DSE dataset contains sensitive and proprietary governance, contractual, and risk data. It **MUST ONLY** be accessible to individuals explicitly allowlisted in the authorized Google Groups (`monaro-risk-prod@google.com` / `monaro-risk-dev@google.com`) and authenticated via corporate Google SSO through Identity-Aware Proxy (IAP). Proprietary project directories (`data/f-dse/`) and environment keys are strictly excluded from version control (`.gitignore`).
3. **Safe Public Showcases (Decoupled Multi-Project Routing)**:
   - The codebase must support parameter-based project isolation (`?project=sample` vs `?project=f-dse`) so the team can demo, test, and showcase the platform publicly using sanitized sample data (Project Aurora) without exposing confidential Monaro project content.

### 1.3 Core Functional Capabilities
1. **Executive Decision Synthesis (Gemini AI)**: Exception-first synthesis with 3 stakeholder perspective toggles (Executive, Technical, Governance), Top 3 Critical Action cards, Early Warning Sleeper Outliers, and a Schedule Squeeze Barometer.
2. **Dual-Speaker Audio Podcast Briefing (Gemini TTS)**: Multi-speaker podcast discussion (`Puck` and `Aoede` voices) with an interactive waveform scrubber, variable playback speed, synced auto-scrolling transcript, and direct MP3 export.
3. **Interactive 5×5 Risk & Issue Matrix**: Inherent vs. Residual risk toggling with active cell focus rings, status filtering, and 1-click citation deep links (`↗`) into a comprehensive Item Detail Modal.
4. **Dedicated Team Google Risk Register**: Scoped register tracking Google-specific deliverable risks and mitigations.
5. **Contractual Horizon (CD1) Driver Tree**: Level 2 Contractual Milestones (`1.7a DevSecOps`, `1.10b Test/Dev`, `1.13 IBR`, `1.14 SRR`) with clickable related risk and issue badges that filter the active ledgers.
6. **Longitudinal Performance Trends & Time Machine**: Inherent vs. Residual Burndown curves with multi-granularity switching (Weekly, Bi-Weekly, Monthly), Net Backlog Velocity tracking, and an interactive historical Time Machine ribbon (`W22`–`W27`).
7. **Knowledge Base & Solution Blueprints**: Solution blueprints mapped to contract annexes with deep links to Gemini NotebookLM notebooks.
8. **Decoupled Multi-Project Routing**: Dynamic project dataset switching via URL query parameters.

---

## 2. System Architecture & Technical Invariants

### 2.1 Decoupled SPA & Backend Architecture
* **Frontend Presentation Engine (`index.html`)**: High-performance, decoupled Single Page Application utilizing Tailwind CSS and Chart.js.
* **Integrated Backend & Ingestion Engine (`server.py` & `scripts/ingest_data.py`)**:
  - Serves static assets and isolates project data paths (`data/<project-slug>/`).
  - Provides REST API endpoints for live Google Sheets syncing (`/api/sync-sheet`), UI-triggered on-demand data ingestion (`/api/ingest-data`), and Gemini executive brief/podcast regeneration (`/api/regenerate-briefing`).
  - Executes data extraction, normalization, and Gemini AI synthesis.
* **Dynamic Client-Side Computation**: All matrix coordinates, risk distributions, burndown velocity curves, and filter predicates are computed dynamically in the browser client on dataset load. **No precomputed analytics cache files** are generated or stored on disk.
* **Multi-Project Parameterized Routing**: The application reads `?project=<project-slug>` (defaulting to `sample`) and dynamically fetches isolated project datasets from `data/<project-slug>/`.

### 2.2 Server Runtime & CLI Tooling
* **Python Runtime**: Requires **Python 3.12+** with **Google Cloud ADC** (`gcloud auth application-default login`) or **`GEMINI_API_KEY`** (mandatory for Vertex AI / Gemini decision synthesis and Cloud TTS audio).
* **Server Runtime (`server.py`)**: Lightweight Python HTTP server serving static frontend assets, raw JSON data files, and REST API endpoints:
  - `GET /`: Serves `index.html` with query parameters.
  - `POST /api/sync-sheet`: Fetches live Google Sheets data and updates project data files.
  - `POST /api/ingest-data`: Triggers master ingestion pipeline (`scripts/ingest_data.py`).
  - `POST /api/regenerate-briefing`: Triggers Gemini API synthesis regeneration and audio podcast creation (`scripts/gemini_generator.py`).
* **Local Development Runner (`run_server.sh`)**: 1-command tmux lifecycle script managing background server execution on port 9000 (`http://localhost:9000` or `http://uk-bh-cloudtop.c.googlers.com:9000`).

### 2.3 Cloud Run & Security Architecture (Google SSO via IAP)
* **Cloud Run Deployment**: Containerized deployment on Google Cloud Run (`monaro-risk-dash-dev`) configured with `--no-allow-unauthenticated`.
* **Identity-Aware Proxy (IAP)**: All incoming traffic is intercepted by Google Cloud IAP, enforcing corporate Google SSO login.
* **Access Governance**:
  - `monaro-risk-dev@google.com`: Development and operator group.
  - `monaro-risk-prod@google.com`: Executive stakeholder and viewer group (e.g. `allins@google.com`).
  - Access is granted via the `roles/iap.httpsResourceAccessor` IAM role bound directly to these Google Groups. Adding/removing members in the Google Groups web UI instantly provisions or revokes dashboard access without touching GCP IAM.
* **Corporate MDB & TwoSync**: Ganpati (MDB) Prod groups (`%monaro-risk-admin.prod`, `%monaro-risk-dev.prod`) govern Nexus GCP project ownership, and TwoSync bridges MDB rosters to the Google Groups.

### 2.4 CI/CD Deployment Pipeline
* **Automated Cloud Build Trigger**: Cloud Build trigger (`deploy-monaro-risk-dash-dev`) executes automatically on every `git push` to branch `dev` for paths matching `project_dash/**`.
* **Pipeline Stages (`deploy/cloudbuild.yaml`)**:
  1. Unit test execution (`python3 -m unittest discover -s tests -p "test_*.py"`).
  2. Artifact Registry repository verification/creation (`cloud-run-source-deploy`).
  3. Docker container image build.
  4. Docker container image push.
  5. Cloud Run service deployment with `--iap` enabled.
  6. Automated IAM policy binding for IAP access.
* **Build Diagnostics CLI (`scripts/check_build_status.py`)**: Terminal tool to query Cloud Build API and inspect build status, step durations, and failure logs.
* **Asynchronous Push Protocol**: Pushes to `dev` trigger non-blocking background builds without hanging terminal sessions.

---

## 3. Data Architecture & Multi-Project Isolation

All project data is strictly isolated within `data/<project-slug>/`:

```
project_dash/
├── index.html                   # Core presentation frontend
├── server.py                    # API & static server
├── package_zip.sh               # Minimal bundle packager
├── docs/                        # Project manuals & guides
│   ├── HANDOVER_GUIDE.md        # Turnkey operator & handover manual
│   ├── TEAM_PRESENTATION_GUIDE.md # 5-minute showcase narrative
│   └── DEPLOYMENT_GUIDE.md      # CI/CD & IAP security setup
├── prompts/
│   ├── exec_summary_prompt.md   # Gemini structured JSON executive summary prompt
│   └── podcast_prompt.md        # Gemini dual-speaker podcast script prompt
├── scripts/
│   ├── ingest_data.py           # Master Ingestion Orchestrator CLI
│   ├── gemini_generator.py      # Gemini synthesis & TTS audio generator
│   ├── ingest_weekly_report.py  # Weekly PDF extraction script
│   └── check_build_status.py    # Cloud Build CI/CD status query tool
├── data/
│   ├── sample/                  # Public showcase dataset (Project Aurora)
│   │   ├── config.json          # Project metadata, branding & URLs
│   │   ├── risks.json           # 5x5 Inherent & Residual risk registry
│   │   ├── issues.json          # Operational issue register
│   │   ├── snapshots.json       # Longitudinal weekly snapshots (W22-W27)
│   │   ├── knowledge.json       # Blueprint & contract knowledge sources
│   │   └── driver_tree.json     # Contractual milestones & capability drops
│   └── f-dse/                   # Monaro / F-DSE Production Dataset (Git-ignored)
└── tests/                       # Automated test suite (97 tests)
```

### 3.1 Data Contracts & File Schemas

#### 1. `config.json`
Defines branding, color themes, and data source links:
```json
{
  "project": {
    "slug": "sample",
    "name": "Project Aurora",
    "title": "Program Governance & Risk Intelligence Platform",
    "subtitle": "Executive Cockpit & Risk Intelligence",
    "logoIcon": "🛡️"
  },
  "theme": {
    "primaryColor": "indigo",
    "primaryHex": "#4f46e5"
  },
  "sources": {
    "googleSheets": {
      "riskRegisterUrl": "https://docs.google.com/spreadsheets/d/...",
      "sheetName": "Risks"
    },
    "googleDrive": {
      "reportsFolderUrl": "https://drive.google.com/drive/folders/..."
    }
  }
}
```

#### 2. `risks.json`
List of registered risks with scoring and mitigations:
```json
[
  {
    "id": "RSK-001",
    "title": "Vendor Identity Provider Integration Delay",
    "category": "Technical",
    "workstream": "Security & Identity",
    "inherent_likelihood": 4,
    "inherent_impact": 4,
    "inherent_score": 16,
    "residual_likelihood": 2,
    "residual_impact": 3,
    "residual_score": 6,
    "status": "In Progress",
    "owner": "Sarah Jenkins",
    "mitigation": "Deploy fallback OIDC connector and prioritize staging verification.",
    "target_date": "2026-09-15",
    "is_team_google": false
  }
]
```

#### 3. `issues.json`
List of active operational issues:
```json
[
  {
    "id": "ISS-001",
    "title": "DevSecOps Pipeline Stage 2 Flakiness",
    "priority": "P1",
    "impact": "High",
    "status": "Open",
    "owner": "Tom Reynolds",
    "resolution_plan": "Pin runner image and add retry on transient network timeouts.",
    "target_date": "2026-08-25"
  }
]
```

#### 4. `driver_tree.json`
Hierarchical contractual delivery horizon:
```json
{
  "milestones": [
    {
      "id": "M-1.10b",
      "code": "1.10b",
      "name": "Platform Ready (E.01 Test/Dev Enclave)",
      "target_date": "30 Sep 2026",
      "status": "In Progress",
      "owner": "Steve Deacon",
      "deliverables": [
        {
          "id": "DEL-101",
          "name": "E.01 VPC Peering & Security Enclave",
          "status": "Amber",
          "related_risks": ["RSK-001", "RSK-012"],
          "related_issues": ["ISS-001"]
        }
      ]
    }
  ]
}
```

#### 5. `snapshots.json`
Longitudinal weekly reporting history (W22 through W27+):
```json
[
  {
    "week": "W27",
    "date": "2026-08-07",
    "reporting_period": "Week ending 07 Aug 2026",
    "metrics": {
      "total_risks": 107,
      "critical_risks": 8,
      "high_risks": 24,
      "open_issues": 29,
      "schedule_squeeze_index": 7.4
    },
    "synthesis": {
      "executive": {
        "headline": "DevSecOps & Platform Ready E.01 Convergence",
        "narrative": "...",
        "top_actions": [
          { "rank": 1, "title": "Finalize Identity Provider Bridge", "owner": "Sarah Jenkins", "deadline": "15 Aug 2026" }
        ],
        "sleeper_outlier": { "ref": "Ref 1.15", "title": "Telemetry Quota Exhaustion", "summary": "..." }
      },
      "technical": { "headline": "...", "narrative": "..." },
      "governance": { "headline": "...", "narrative": "..." }
    },
    "audio_briefing": {
      "audio_file": "assets/podcast_w27.mp3",
      "transcript": "..."
    }
  }
]
```

---

## 4. Functional Requirements (Modules FR-1 through FR-8)

### FR-1: Global Navigation & Shell Controls
- **FR-1.1 Dynamic Project Selector**: Navigation bar dropdown allowing dynamic switching between configured projects (`?project=sample`, `?project=f-dse`).
- **FR-1.2 Historical Time Machine Ribbon**: Header ribbon allowing users to scrub between historical weeks (`W22` through `W27`). Selecting a past week updates dashboard state to that historical point in time and displays a prominent warning banner with a 1-click button to return to the live baseline.
- **FR-1.3 Workspace Sync Modal**: Modal dialog supporting:
  - 1-Click live sync from Google Sheets via backend API.
  - Dropzone upload for weekly PDF reports.
  - Status toasts confirming sync results.
- **FR-1.4 Universal Item Detail Modal**: Deep inspection modal providing comprehensive details, history, owners, and citations for any clicked risk, issue, or milestone.

### FR-2: Executive Decision Briefing (Tab 1)
- **FR-2.1 Top 4 KPI Banner**: Real-time summary cards displaying:
  1. Critical / Extreme Risks (count and weekly change $\Delta$).
  2. Active Operational Issues (count and P0/P1 breakdown).
  3. Schedule Squeeze Barometer (composite 1–10 dependency index).
  4. Security ATO / Governance Gate status badge (e.g. `ATO-C: AMBER`).
- **FR-2.2 Multi-Tone Perspective Switcher**: Interactive pills toggling between **Executive** (board actions & milestones), **Technical** (enclaves & telemetry), and **Governance** (commercial gates & accreditation).
- **FR-2.3 Top 3 Critical Action Cards**: Formatted priority cards showing action title, description, assigned workstream owner, target date, and related risk citation links.
- **FR-2.4 Early Warning Sleeper Outlier**: Special highlighted alert card for emerging latent risks (e.g. `Ref 1.15`) that possess low residual ratings but high dependency friction.
- **FR-2.5 Dual-Speaker Audio Podcast Player**:
  - Embedded waveform scrubbing player powered by **Gemini Multi-Speaker Speech Synthesis** (`google.genai` SDK) generating natural, life-like conversational dialogue with `Puck` (host) and `Aoede` (co-host) voices.
  - Play/Pause toggle, skip $\pm 10$ seconds, variable speed controls (`0.75x`, `1x`, `1.25x`, `1.5x`, `2x`).
  - Auto-scrolling synchronized transcript drawer with speaker avatar badges.
  - Direct MP3 audio file export.

### FR-3: 5×5 Risk Heatmap & Live Risk Explorer (Tab 2)
- **FR-3.1 5×5 Matrix Grid**: Matrix mapping Likelihood (1–5) on the vertical axis against Impact (1–5) on the horizontal axis, colored by standard risk tiers (Green, Yellow, Amber, Red).
- **FR-3.2 Inherent vs. Residual Toggle**: Seamless toggle transitioning cell counts and vector trajectories between Inherent (Pre-Control) and Residual (Post-Control) risk ratings.
- **FR-3.3 Interactive Focus Ring Cell Filtering**: Clicking any matrix cell (e.g. Likelihood 4, Impact 4) highlights the cell with an active focus ring, calculates the filtered subset, and scrolls to/filters the Live Risk Explorer below. Clicking again clears the filter.
- **FR-3.4 Live Risk Explorer**: Searchable, filterable risk cards with:
  - Category and workstream filter dropdowns.
  - Text search matching ID, title, owner, and mitigation text.
  - Expandable mitigation accordions with owner, target date, and residual score pills.
  - 1-click citation jumps (`↗`) opening the universal Item Detail Modal.

### FR-4: Team Google Dedicated Risk Register (Tab 3)
- **FR-4.1 Scoped Google Risk View**: Dedicated tab isolating risks where `is_team_google == true`, allowing delivery leads to monitor Google-owned deliverables and contractual exposure separately from vendor/partner registers.

### FR-5: Issue Register (Tab 4)
- **FR-5.1 Tabular Issue Tracker**: Sortable table displaying active operational issues with Priority badges (`P0`, `P1`, `P2`, `P3`), Status indicators (`Open`, `In Progress`, `Blocked`, `Resolved`), assigned Owner, Target Resolution Date, and 1-click detail inspection.

### FR-6: Performance Trends & Velocity Analytics (Tab 5)
- **FR-6.1 Longitudinal Risk Burndown**: Line chart plotting total Inherent and Residual risk points across historical reporting periods.
- **FR-6.2 Multi-Granularity Switching**: Granularity selector toggling trend views between **Weekly**, **Bi-Weekly**, and **Monthly** intervals.
- **FR-6.3 Net Backlog Velocity**: Bar chart illustrating the rate of newly opened vs. resolved risks and issues per reporting cycle.
- **FR-6.4 Risk Cause Category Distribution**: Horizontal bar breakdown analyzing risk concentration across Schedule, Governance, Technical, and Commercial root causes.
- **FR-6.5 Timeline Drilldown Modal**: Modal allowing users to inspect the exact state diff between any two historical reporting weeks.

### FR-7: Knowledge Base & Solution Blueprints (Tab 6)
- **FR-7.1 Solution Blueprint Catalog**: Card grid organizing architectural blueprints, ATO accreditation artifacts, and contractual annexes.
- **FR-7.2 NotebookLM Integration**: Deep links to curated Gemini NotebookLM instances for rapid Q&A against source documentation.

### FR-8: Contractual Horizon (CD1) Driver Tree (Tab 7)
- **FR-8.1 Hierarchical Milestone Driver Tree**: Visual capability tree mapping Level 2 Contractual Milestones (`1.7a DevSecOps`, `1.10b Platform Ready`, `1.13 IBR`, `1.14 SRR`) down to individual deliverable packages.
- **FR-8.2 Interactive Deliverable Cards**: Deliverable cards displaying milestone owners, target completion dates, RAG status pills, and **clickable related risk & issue badges** (`RSK-001`, `ISS-002`) that instantly cross-filter the risk/issue ledgers.

---

## 5. AI Ingestion & Synthesis Engine

### 5.1 Ingestion Pipeline & Synchronization
* **UI-Triggered Ingestion (Primary)**: Users trigger data synchronization directly from the web dashboard via the **"Sync with Google Drive"** / **"Workspace Sync"** modal. The frontend invokes `/api/sync-sheet` or `/api/ingest-data` to ingest new Google Sheets data or uploaded PDF report packs in real time.
* **Master Ingestion CLI (`scripts/ingest_data.py`)**: Headless automation orchestrator accepting `--project=<slug>` (e.g. `python3 scripts/ingest_data.py --project=sample`).
  - Ingests Google Sheets registers, Drive PDF packs, and `knowledge.json` catalogs.
  - Normalizes and writes data directly into `snapshots.json`, `risks.json`, `issues.json`, and `driver_tree.json`.
  - Invokes `scripts/gemini_generator.py` to synthesize multi-tone executive briefs and neural podcast audio.

### 5.2 Gemini Decision Synthesis (`scripts/gemini_generator.py`)
* **Model**: Uses Gemini 3.0+ models (defaulting to `gemini-3.5-flash` / Vertex AI) for structured JSON synthesis.
* **Structured Output Schema**: Validates structured JSON matching `prompts/exec_summary_prompt.md` containing `executive`, `technical`, and `governance` synthesis blocks, Top 3 Action cards, and Sleeper Outliers.
* **Podcast Audio Scripting & Speech Synthesis**: Generates dual-host conversational dialogue scripts (`prompts/podcast_prompt.md`) and synthesizes life-like multi-speaker audio via **Gemini Multi-Speaker Speech Generation** using `Puck` and `Aoede` personas for natural executive discussions.

---

## 6. Spec-Driven Development (SDD) & Defect Management Protocol

To prevent future specification drift and maintain high code velocity:

1. **Conductor as Master Spec & Architecture Source of Truth**:
   - `conductor/product.md` and `conductor/tech-stack.md` define high-level vision and technical invariants.
   - This Master Specification Document (`conductor/spec.md`) serves as the definitive functional and design reference for the platform.
   - Planned multi-step features or structural refactorings are created as Conductor Tracks under `conductor/tracks/`.
2. **Defect Tracking via `.agents/bugs.json`**:
   - Bugs, regressions, and small enhancements are recorded in `.agents/bugs.json` using `/bug`, `/triage_bug`, and `/fix_bug`.
   - **TDD Requirement**: Every bug fix begins with an automated reproduction unit test that fails before the code fix and passes after.
3. **Spec Synchronization Barrier**:
   - Whenever a Conductor track completes or a significant feature/architectural change lands, the Master Spec (`conductor/spec.md`) must be reviewed and updated to reflect the new state.
4. **Automated Quality Assurance**:
   - The test suite (`tests/`) maintains 100% passing automated test coverage (currently 97 tests) validating data schemas, live calculations, server APIs, and driver tree interactions before code is pushed to `dev`.

---

## 7. Verification Checklist & Acceptance Criteria

- [ ] Single Page Application renders all 7 active navigation tabs cleanly with zero console errors.
- [ ] Multi-project parameter routing (`?project=sample` vs `?project=f-dse`) cleanly isolates datasets.
- [ ] 5×5 Risk Heatmap toggles seamlessly between Inherent and Residual distributions, and cell clicks filter the Live Risk Explorer with active focus rings.
- [ ] Neural podcast audio player supports waveform scrubbing, variable speeds (0.75x–2x), synced transcript, and MP3 download.
- [ ] Driver tree deliverable cards display clickable related risk and issue badges that cross-filter ledgers.
- [ ] Master ingestion pipeline (`python3 scripts/ingest_data.py --project=<slug>`) cleanly generates valid snapshot and data files without precomputed caches.
- [ ] Cloud Run deployment is secured by Identity-Aware Proxy (IAP) requiring corporate Google SSO.
- [ ] All 97 automated unit tests pass cleanly (`python3 -m unittest discover -s tests -p "test_*.py"`).
