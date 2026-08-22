# System Specification & Architecture Design Document (SDD)
# Project Dash — Decoupled Risk Intelligence & Governance Platform

> **Document Status:** Active Master Specification  
> **Target Version:** 2.0 (Post-Baseline Multi-Project Release)  
> **Last Updated:** 2026-08-22  
> **Primary Stakeholders:** Allison Innes (`allins@google.com`), Steve Deacon (`sdeacon@google.com`), Wayne Davis (`waynedavis@google.com`), Brendan Hills (`brendanhills@google.com`)

---

## 1. Executive Summary & Vision

### 1.1 Purpose & Data Confidentiality Invariant
**Project Dash** is an ultra-responsive, decoupled executive governance and operational risk intelligence platform. It unifies fragmented weekly PDF reports, Google Sheets risk registers, contractual milestones, and NotebookLM knowledge documents into an interactive, real-time decision cockpit — providing comprehensive 5×5 risk matrices, longitudinal burndown analytics, contractual delivery driver trees, and integrated **Google Gemini AI** executive decision briefings.

### 1.2 Core Architectural & Operational Principles
1. **Turnkey Handover & Browser-Triggered Data Operations**:
   - The platform is designed to be fully operable and maintainable by governance leads and program managers (`allins@`, `sdeacon@`, `waynedavis@`) without requiring ongoing software engineering support or dedicated administrative portals.
   - **Unified In-Dashboard Data Operations**: All 4 core data lifecycle operations are triggered on-demand directly from the dashboard:
     - **Live Sync**: Syncs live Google Sheets registers and NotebookLM knowledge sources via the **Workspace Sync Modal** (`POST /api/sync`).
     - **Report Ingestion**: Scans the shared Drive folder for newly uploaded PDF reports and ingests them into the time-travel registry with 1 click (`POST /api/ingest`).
     - **Executive Briefing Synthesis**: Synthesizes Gemini 3.5 Pro exception-first executive summaries and Top 3 Attention items upon ingestion or manual regeneration (`POST /api/briefing/generate`).
     - **Neural Podcast Generation**: Generates Australian multi-speaker (`Puck` & `Aoede`) podcast audio dialogue on-demand directly in the backend.
   - **Self-Service Access**: User provisioning is handled through Google Groups (`monaro-risk-dev@google.com` / `monaro-risk-prod@google.com`), automatically synchronizing IAP permissions without touching GCP IAM.
   - **Automated CI/CD**: Cloud Build automatically builds, tests, and deploys verified changes upon git push, eliminating manual container or server management.
2. **Defensive Processing & Resilient Ingestion**:
   - Ingestion pipelines dynamically adapt to variations in weekly report filenames, dates, and text formatting.
   - The platform includes self-healing deterministic fallbacks to guarantee that dashboards remain responsive and functional even during temporary API quota limits or network interruptions.
3. **Unified, Minimal Architecture**:
   - Backend functionality is consolidated into a cohesive ingestion pipeline (`scripts/pipeline.py`) and a clean REST resource interface (`server.py`).
   - Business logic favors refactoring and unifying shared workflows over accumulating single-purpose scripts or endpoints.
4. **Data Confidentiality & Decoupled Multi-Project Support**:
   - Proprietary Monaro / F-DSE project content is strictly protected behind Google SSO and IAP.
   - The system natively supports parameter-driven project isolation (`?project=sample` vs `?project=f-dse`), enabling safe demonstrations and public testing using sanitized sample datasets (Project Aurora).

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
  - `GET /api/sync-sheet` & `POST /api/sync-sheet`: Fetches live Google Sheets data and updates project data files.
  - `GET /api/sync-all` & `POST /api/sync-all`: Triggers multi-source synchronization across Sheets, Drive, and Notebooks.
  - `GET /api/check-drive-sync`: Scans configured Google Drive folder for newly uploaded weekly PDF reports.
  - `GET /api/notebooks`: Lists configured NotebookLM notebooks and sync status.
  - `GET /api/check-notebook-sync`: Probes NotebookLM connectivity and update status.
  - `GET /api/sync-notebook` & `POST /api/sync-notebook`: Synchronizes knowledge sources with NotebookLM.
  - `GET /api/ingest-report` & `POST /api/ingest-report`: Ingests and processes uploaded PDF weekly reports.
  - `POST /api/ingest-data`: Triggers master ingestion pipeline (`scripts/ingest_data.py`).
  - `POST /api/regenerate-briefing`: Triggers Gemini API synthesis regeneration and audio podcast creation (`scripts/gemini_generator.py`).
  *(Note: Endpoint consolidation and rationalization is tracked in Bug #79).*
* **Local Development Runner (`run_server.sh`)**: 1-command tmux lifecycle script managing background server execution on port 9000 (`http://localhost:9000` or `http://uk-bh-cloudtop.c.googlers.com:9000`).

### 2.3 Dual-Environment Matrix & Cloud Run Security Architecture (Google SSO via IAP)

| Dimension / Parameter | Development (`dev`) | Production (`prod`) |
| :--- | :--- | :--- |
| **GCP Project ID** | `monaro-risk-dev` | **`monaro-risk-prod`** |
| **Deployment Region** | **`australia-southeast1`** (Sydney) | **`australia-southeast1`** (Sydney) |
| **Cloud Run Service Name** | `monaro-risk-dash-dev` | **`monaro-risk-dash-prod`** |
| **Active Git Branch** | `dev` | **`dev`** *(Single-branch trunk architecture)* |
| **Deployment Trigger Event** | Auto on `git push origin dev` | **Auto on `git tag` matching `^project_dash/prod-.*$`** |
| **Artifact Registry Repo** | `cloud-run-source-deploy` (Sydney) | `cloud-run-source-deploy` (Sydney) |
| **IAP Google SSO Group** | `monaro-risk-dev@google.com` | **`monaro-risk-prod@google.com`** |
| **Live Deployed Dashboard** | • [Monaro Live (Dev)](https://monaro-risk-dash-dev-525025654699.australia-southeast1.run.app/?project=f-dse)<br>• [Aurora Showcase (Dev)](https://monaro-risk-dash-dev-525025654699.australia-southeast1.run.app/?project=sample) | • [Monaro Live (Prod)](https://monaro-risk-dash-prod-525025654699.australia-southeast1.run.app/?project=f-dse)<br>• [Aurora Showcase (Prod)](https://monaro-risk-dash-prod-525025654699.australia-southeast1.run.app/?project=sample) |

* **Identity-Aware Proxy (IAP) & Access Governance**:
  - All incoming traffic is intercepted by Google Cloud IAP, enforcing corporate Google SSO login.
  - `monaro-risk-dev@google.com`: Development and operator group.
  - `monaro-risk-prod@google.com`: Executive stakeholder and viewer group (e.g. `allins@google.com`).
  - Access is granted via the `roles/iap.httpsResourceAccessor` IAM role bound directly to these Google Groups. Adding or removing members in the Google Groups web UI instantly provisions or revokes dashboard access without touching GCP IAM.
* **Corporate MDB & TwoSync**: Ganpati (MDB) Prod groups (`%monaro-risk-admin.prod`, `%monaro-risk-dev.prod`) govern Nexus GCP project ownership, and TwoSync bridges MDB rosters to the Google Groups.

### 2.4 CI/CD Deployment Pipeline & Production Release Promotion

The platform follows a deterministic, tag-driven release promotion model from a single branch (`dev`):

1. **Continuous Deployment to Dev (`monaro-risk-dev`)**:
   - Cloud Build trigger (`deploy-monaro-risk-dash-dev`) executes automatically on every `git push origin dev` for paths matching `project_dash/**`.
   - Runs automated unit tests, builds the Docker container image, pushes to Artifact Registry in `australia-southeast1`, and updates `monaro-risk-dash-dev` on Cloud Run.

2. **Production Release Promotion via Git Tags (`monaro-risk-prod`)**:
   - Promotion to production does NOT require branch merges or manual container rebuilds.
   - When a release candidate is verified on `dev`, the operator promotes the exact verified commit to production by creating and pushing a release tag:
     ```bash
     # 1. Tag the verified commit on dev
     git tag project_dash/prod-v2.0.0
     
     # 2. Push tag to trigger production Cloud Build
     git push origin project_dash/prod-v2.0.0
     ```
   - Cloud Build trigger (`deploy-monaro-risk-dash-prod`) detects tags matching `^project_dash/prod-.*$`, executes the test suite, builds the production container image, deploys to `monaro-risk-dash-prod`, and updates IAP bindings.
   - **Rollback / Fast Roll-forward**: Any historical release can be instantly restored by selecting a prior tag in Pantheon Cloud Build triggers or redeploying the specific commit digest from Artifact Registry (refer to [`deploy/PROD_PROVISIONING_GUIDE.md`](./deploy/PROD_PROVISIONING_GUIDE.md)).

3. **Pipeline Stages (`deploy/cloudbuild.yaml`)**:
   - Step 1: Unit test execution (`python3 -m unittest discover -s tests -p "test_*.py"`).
   - Step 2: Artifact Registry repository verification/creation (`cloud-run-source-deploy`).
   - Step 3: Docker container image build.
   - Step 4: Docker container image push.
   - Step 5: Cloud Run service deployment with `--iap` enabled.
   - Step 6: Automated IAM policy binding for IAP access.
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
Defines branding, color themes, KPI pillars, and feature toggles:
```json
{
  "project": {
    "slug": "sample",
    "name": "Project Aurora",
    "title": "Enterprise AI & Sovereign Cloud Modernization",
    "organization": "Global Enterprise Transformation Board",
    "logoIcon": "🪐",
    "heroTag": "Enterprise Sovereign Enclave • AI Platform Modernization",
    "primaryRegisterName": "Joint Program Register",
    "secondaryRegisterName": "Team Cloud Register",
    "links": {
      "charter": "https://example.com/aurora/charter",
      "architecture": "https://example.com/aurora/architecture",
      "tracker": "https://example.com/aurora/jira"
    }
  },
  "kpiPillars": [
    {
      "id": "commercial",
      "label": "Commercial & Budget",
      "value": "🟢 ON TRACK",
      "subtext": "Milestone payments aligned to baseline schedule"
    },
    {
      "id": "milestone",
      "label": "Milestone Gate 2 (IBR)",
      "value": "🟡 IN PROGRESS (88%)",
      "subtext": "System requirements review on critical path"
    },
    {
      "id": "security",
      "label": "ATO & Cyber Security",
      "value": "🟢 ACCREDITED",
      "subtext": "Sovereign enclave security controls validated"
    },
    {
      "id": "escalations",
      "label": "Critical Escalations",
      "value": "🔴 4 ITEMS",
      "subtext": "3 technical blockers under active mitigation"
    }
  ],
  "sources": {
    "googleSheets": { "enabled": false },
    "googleDrive": { "enabled": false },
    "geminiNotebooks": { "enabled": false }
  },
  "features": {
    "executiveBriefing": { "enabled": true },
    "riskMatrix": { "enabled": true },
    "secondaryRegister": { "enabled": true },
    "issues": { "enabled": true },
    "trends": { "enabled": true },
    "knowledgeBase": { "enabled": true },
    "driverTree": { "enabled": true },
    "audioBriefing": { "enabled": true }
  }
}
```

#### 2. `risks.json`
List of registered risks aligned with Commonwealth & Defence risk standards:
```json
[
  {
    "id": "AUR-RSK-001",
    "displayId": "01",
    "status": "Active",
    "riskOwner": "Marcus Chen",
    "bundle": "Bundle H (Core Infra)",
    "driverTreeRef": "1.10b",
    "riskName": "Sovereign Enclave Hardware Interconnect Latency",
    "title": "Sovereign Enclave Hardware Interconnect Latency",
    "description": "Dedicated fiber cross-connect lead times may compress network validation window prior to Phase 1 cutover.",
    "causeCategory": "Engineering/Platform",
    "causeDescription": "Root cause related to Engineering/Platform dependency integration and timeline constraints.",
    "consequenceDescription": "Potential schedule delay of 2-4 weeks and increased verification overhead.",
    "trend": "↓",
    "priority": "High",
    "governanceLevel": "Joint Steering Committee",
    "inherentLikelihood": 5,
    "inherentConsequence": 4,
    "inherentRiskScore": 20,
    "inherentRiskLevel": "Critical",
    "treatmentOwner": "Marcus Chen",
    "treatmentPlan": "Staged redundant optical interconnects and pre-provisioned dark fiber lines.",
    "targetDate": "30-Sep-2026",
    "residualLikelihood": 2,
    "residualConsequence": 3,
    "residualRiskScore": 6,
    "residualRiskLevel": "Medium",
    "dateRaised": "15-May-2026",
    "strategy": "Mitigate",
    "sourceRegister": "joint",
    "sourceLabel": "Joint Program Register"
  }
]
```

#### 3. `issues.json`
List of active operational issues aligned with program governance registers:
```json
[
  {
    "id": "I-0001",
    "displayId": "1",
    "status": "Active",
    "issueOwner": "Tom Trobe",
    "bundle": "Bundle H (Core Infra)",
    "driverTreeRef": "1.10b",
    "issueName": "Platform Ready Test/Dev Environment Delivery Lead-Time",
    "title": "Platform Ready Test/Dev Environment Delivery Lead-Time",
    "description": "Dedicated fiber cross-connect lead times may compress network validation window prior to Phase 1 cutover.",
    "causeDescription": "Long-lead hardware supply chain dependency for physical enclave optical termination.",
    "impactCategory": "Schedule",
    "severity": "Medium",
    "priority": "Urgent",
    "trend": "↔",
    "escalateTo": "Google Internal",
    "actionPlan": "Validating schedule impacts, with CD1 Gap Closure Plan and mitigating delivery approach whilst connectivity is established.",
    "nextActionOwner": "Tom Trobe",
    "dateRaised": "23-Jul-2026",
    "raisedBy": "Susan Allin",
    "dateClosed": "",
    "lastUpdated": "23-Jul-2026",
    "sourceRegister": "joint",
    "sourceLabel": "Joint Program Register"
  }
]
```

#### 4. `driver_tree.json`
Hierarchical contractual delivery horizon mapping capability drops to milestone gates:
```json
{
  "version": "03",
  "program": "Delivery Governance & Sovereign Enclave Modernization",
  "lastUpdated": "2026-08-07",
  "capabilityDrops": [
    {
      "id": "cd1",
      "name": "Capability Drop 1.0 (Core Sovereign Enclave)",
      "lead": "Ed Louis (HJCC / FAS GCD / CJC)",
      "targetDate": "2027-02-01",
      "status": "AMBER",
      "gates": [
        {
          "ref": "1.2b",
          "name": "Milestone 1 Deliverables Acceptance",
          "description": "Finalization and sign-off on SRP, V&V Strategy, and IMS deliverable baseline packages.",
          "status": "AMBER",
          "level": 2,
          "owner": "Michael Maconachie",
          "targetDate": "2026-08-31",
          "progress": 60,
          "gapCloseRef": "1",
          "gapCloseTitle": "Commonwealth Milestone 1 Acceptance Matrix",
          "shift": "Forecast completion moved to 31 Aug 2026"
        },
        {
          "ref": "1.10b",
          "name": "Platform Ready (E.01 Test/Dev Enclave)",
          "description": "Core sovereign hardware infrastructure initialized and verified for early test/dev workloads.",
          "status": "AMBER",
          "level": 2,
          "owner": "Steve Deacon",
          "targetDate": "2026-09-30",
          "progress": 85,
          "gapCloseRef": "3",
          "shift": "Environment build commenced with staged optical interconnect verification"
        }
      ]
    }
  ]
}
```
*(Note: Gates in `driver_tree.json` do not hardcode risk/issue arrays. Risks and issues dynamically bind to gates via `driverTreeRef` at runtime, enabling automated badge rollups and cross-filtering).*

#### 5. `snapshots.json`
Longitudinal weekly reporting history (keyed by week slug):
```json
{
  "lastSynced": "2026-08-19T08:04:46.636518",
  "driveFolderId": "sample-drive-folder-aurora",
  "snapshots": {
    "w27": {
      "weekNumber": 27,
      "weekLabel": "Week 27",
      "week": "Week 27",
      "date": "07 Aug 2026",
      "isLatest": true,
      "isCurrent": true,
      "driveFileId": "1HBfI9itx3BER4IRnH9eavBgAsrDGHnmu",
      "driveFileName": "Weekly Reporting - Week 27 - 07 Aug 2026.pdf",
      "overallStatus": "🟡 AMBER (Stable)",
      "kpis": {
        "commercial": "🟢 ON TRACK",
        "ibr": "🟡 DUE AUG 2026 (85%)",
        "ato": "🟢 GREEN",
        "escalations": "🔴 5 ITEMS"
      },
      "synthesis": {
        "executive": "Program posture for Week 27 maintains a stable AMBER status with active mitigation across 28 registered risks...",
        "technical": "Technical velocity confirms key milestones on track with ongoing security accreditation and environment validation...",
        "governance": "Governance alignment continues across key deliverable gates with 11 active blockers under remediation."
      },
      "top3": [
        {
          "num": 1,
          "type": "decision",
          "tag": "🚨 Immediate Action",
          "ref": "1.2b",
          "title": "Commonwealth Acceptance",
          "action": "Executive engagement needed with Cth delegates to finalize acceptance of SRP, V&V, and IMS deliverable packs."
        }
      ],
      "sleeperOutlier": {
        "ref": "1.14",
        "title": "Cross-Domain Enclave Model Quantization",
        "warning": "Inference latency spikes under peak token load in air-gapped sovereign environments."
      },
      "podcastScript": [
        {
          "speaker": "Alex",
          "role": "Program Analyst",
          "avatar": "🎙️",
          "time": "0:00",
          "text": "Welcome to the Executive Briefing for Week 27..."
        }
      ],
      "generatedBy": "gemini-3.5-flash"
    }
  }
}
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
- **FR-2.1 Top 4 Program KPI Banner**: Executive header strip rendering 4 core program pillars defined in `config.json`:
  1. **Commercial & Budget**: Financial/commercial standing (e.g. `🟢 ON TRACK`).
  2. **Milestone Gate 2 (IBR)**: Critical path schedule milestone status and completion percentage (e.g. `🟡 IN PROGRESS (88%)`).
  3. **ATO & Cyber Security**: Security accreditation and ATO gate posture (e.g. `🟢 ACCREDITED`).
  4. **Critical Escalations**: Count of active executive escalations and blocker items (e.g. `🔴 4 ITEMS`).
  *(Note: Inherent/Residual risk totals, active issue counts, and the Schedule Squeeze Barometer index are displayed in dedicated sub-panels directly below the executive briefing card).*
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
