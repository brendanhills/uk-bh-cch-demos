# 📘 Project Dash / Monaro Risk Intelligence Platform — Master Specification

> **Version:** 2.1.0  
> **Status:** Approved / Active Baseline  
> **Target Audience:** Engineering, Product, Delivery Leads & Customer Stakeholders  
> **Repository:** `cloud-gtm/uk-bh-experiments/project_dash`  
> **Active Branch:** `dev`

---

## 1. Executive Summary & Vision

### 1.1 Problem Statement & Purpose
The **Project Dash / Monaro Risk Intelligence Platform** is an enterprise-grade, executive delivery cockpit built for high-stakes, multi-organization defense and public sector engineering programs. Modern delivery programs struggle with fragmented weekly status PDF reports, siloed risk registers in spreadsheets, disconnected contractual capability milestones, and manual executive briefing preparation.

Project Dash solves this by unifying:
1. **Longitudinal Risk & Issue Analytics**: Dynamic 5×5 inherent and residual risk heatmaps, velocity tracking, and root cause distributions.
2. **Contractual Capability Milestone Tree (CD1)**: Hierarchical milestone delivery horizons with automated RAG status rollups and interactive cross-filtering.
3. **AI-Powered Decision Intelligence**: Automated Gemini 3.5 executive syntheses (Executive, Technical, Governance perspectives) and dual-speaker neural podcast audio briefings.
4. **Time-Travel History Scrubbing**: Instant historical state replay across reporting cycles (W22 through W27+) with zero UI lag.
5. **Live Turnkey Data Synchronization**: Direct Google Sheets API sync, Drive PDF report ingestion, and curated Gemini NotebookLM knowledge exploration.

### 1.2 Core Architectural & Operational Principles
1. **Turnkey Handover & Browser-Triggered Data Operations**:
   - The platform is designed to be fully operable and maintainable by governance leads and program managers (`allins@`, `sdeacon@`, `waynedavis@`) without requiring ongoing software engineering support or dedicated administrative portals.
   - **Unified In-Dashboard Data Operations**: All 4 core data lifecycle operations are triggered on-demand directly from the dashboard:
     - **Live Sync**: Syncs live Google Sheets registers and NotebookLM knowledge sources via the **Workspace Sync Modal** (`POST /api/sync`).
     - **Report Ingestion**: Scans the shared Drive folder for newly uploaded PDF reports and ingests them into the time-travel registry with 1 click (`POST /api/ingest`).
     - **Executive Briefing Synthesis**: Synthesizes Gemini 3.5 Flash exception-first executive summaries and Top 3 Attention items upon ingestion or manual regeneration (`POST /api/briefing/generate`).
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

---

## 2. System Architecture & Technical Invariants

### 2.1 Technology Stack & Architectural Decisions
* **Frontend Architecture**: Zero-build, pure vanilla ES6 JavaScript modules located under `src/js/` (`app.js`, `state.js`, `api.js`, `charts.js`, `analytics.js`, and `modules/*.js`) rendered directly in `index.html`.
  - **No Node.js / Webpack / Vite build step required at runtime**.
  - Uses Tailwind CSS CDN for styling, Chart.js for data visualizations, and Google Fonts (Space Grotesk & Inter).
* **Backend Architecture**: Lightweight standard library Python 3.12+ HTTP server (`server.py`).
  - Implements a rationalized REST API (`/api/status`, `/api/sync`, `/api/ingest`, `/api/briefing/generate`) with backward-compatible aliases.
  - Serves static assets, raw JSON data files, and dispatches to `scripts/pipeline.py` and `scripts/gemini_generator.py`.
  - Executes data extraction, normalization, and Gemini AI synthesis.
* **Dynamic Client-Side Computation**: All matrix coordinates, risk distributions, burndown velocity curves, and filter predicates are computed dynamically in the browser client on dataset load. **No precomputed analytics cache files** are generated or stored on disk.
* **Multi-Project Parameterized Routing**: The application reads `?project=<project-slug>` (defaulting to `sample`) and dynamically fetches isolated project datasets from `data/<project-slug>/`.

### 2.2 Server Runtime & CLI Tooling
* **Python Runtime**: Requires **Python 3.12+** with **Google Cloud ADC** (`gcloud auth application-default login`) or **`GEMINI_API_KEY`** (mandatory for Vertex AI / Gemini decision synthesis and Cloud TTS audio).
* **Server Runtime (`server.py`)**: Lightweight Python HTTP server serving static frontend assets, raw JSON data files, and REST API endpoints:
  - `GET /`: Serves `index.html` with query parameters.
  - `GET /api/status`: Probes multi-source connection health across Sheets, Drive, NotebookLM, and latest snapshot.
  - `POST /api/sync`: Executes unified synchronization across all active project streams (Sheets, Drive, Notebooks).
  - `POST /api/ingest`: Parses an uploaded weekly report PDF, computes risk metrics, generates Gemini briefing, and persists new snapshot.
  - `POST /api/briefing/generate`: Generates or regenerates Gemini executive decision synthesis and multi-speaker podcast audio.
  - Transparent routing aliases maintained for backward compatibility (`/api/sync-sheet`, `/api/sync-all`, `/api/check-drive-sync`, `/api/sync-notebook`, `/api/ingest-report`, `/api/ingest-data`, `/api/regenerate-briefing`).
* **Unified Ingestion Engine (`scripts/pipeline.py`)**: Master ingestion CLI (`python3 scripts/pipeline.py --project=<slug> --sync`).
* **Local Development Runner (`run_server.sh`)**: 1-command tmux lifecycle script managing background server execution on port 9000 (`http://localhost:9000` or `http://uk-bh-cloudtop.c.googlers.com:9000`).

### 2.3 Dual-Environment Matrix & Cloud Run Security Architecture (Google SSO via IAP)

| Dimension / Parameter | Development (`dev`) | Production (`prod`) |
| :--- | :--- | :--- |
| **GCP Project ID** | `monaro-risk-dev` | **`monaro-risk-prod`** |
| **Deployment Region** | **`australia-southeast1`** (Sydney) | **`australia-southeast1`** (Sydney) |
| **Cloud Run Service Name** | `monaro-risk-dash-dev` | `monaro-risk-dash-prod` |
| **Ingress Setting** | `internal-and-cloud-load-balancing` | `internal-and-cloud-load-balancing` |
| **Custom HTTPS Domain** | `https://dev.monaro-risk.internal.goog` *(or IAP direct)* | `https://monaro-risk.internal.goog` *(or IAP direct)* |
| **Access Control (IAP)** | `monaro-risk-dev@google.com` | `monaro-risk-prod@google.com` |
| **Admin Group (IAP / CI)** | `monaro-risk-dev-admin@google.com` | `monaro-risk-prod-admin@google.com` |
| **CI/CD Cloud Build Trigger** | `deploy-monaro-risk-dash-dev` (on push to `dev`) | `deploy-monaro-risk-dash-prod` (on push of `project_dash/prod-*` tag) |
| **Default Active Dataset** | `sample` (Project Aurora) | `f-dse` (Monaro Live) |
| **Google Cloud Service Account** | `monaro-risk-dash-dev-sa@monaro-risk-dev.iam.gserviceaccount.com` | `monaro-risk-dash-prod-sa@monaro-risk-prod.iam.gserviceaccount.com` |

---

## 3. Data Architecture & Multi-Project Isolation

All project data is strictly isolated within `data/<project-slug>/`:

```
project_dash/
├── index.html                   # Core presentation frontend
├── server.py                    # Parameterized REST API & static server
├── deploy/                      # Turnkey Cloud Run provisioning & Dockerfile
│   ├── cloudbuild.yaml          # Sydney multi-stage automated CI/CD pipeline
│   ├── Dockerfile               # Container specification (python:3.13-slim)
│   ├── provision_environment.sh # Turnkey GCP API & IAM provisioning script
│   └── PROD_PROVISIONING_GUIDE.md # Production Pantheon click-ops runbook
├── docs/                        # Project manuals & guides
│   ├── HANDOVER_GUIDE.md        # Turnkey operator & handover manual
│   ├── TEAM_PRESENTATION_GUIDE.md # 5-minute showcase narrative
│   └── DEPLOYMENT_GUIDE.md      # CI/CD & IAP security setup
├── prompts/
│   ├── exec_summary_prompt.md   # Gemini structured JSON executive summary prompt
│   └── podcast_prompt.md        # Gemini dual-speaker podcast script prompt
├── scripts/
│   ├── pipeline.py              # Consolidated master ingestion, report parsing & sync engine
│   ├── gemini_generator.py      # Gemini synthesis & TTS audio generator
│   └── check_build_status.py    # Cloud Build CI/CD status query tool
├── src/
│   └── js/                      # Modular ES6 frontend architecture (api.js, state.js, analytics.js, app.js)
│       └── modules/             # UI domain modules (exec_briefing, risk_explorer, issue_register, etc.)
├── data/
│   ├── sample/                  # Public showcase dataset (Project Aurora)
│   │   ├── config.json          # Project metadata, branding & URLs
│   │   ├── risks.json           # 5x5 Inherent & Residual risk registry
│   │   ├── issues.json          # Operational issue register
│   │   ├── snapshots.json       # Longitudinal weekly snapshots (W22-W27)
│   │   ├── knowledge.json       # Blueprint & contract knowledge sources
│   │   └── driver_tree.json     # Contractual milestones & capability drops
│   └── f-dse/                   # Monaro / F-DSE Production Dataset (Git-ignored)
├── archive/                     # Preserved prototypes & legacy scripts with full git history
└── tests/                       # Automated test suite (127 unit tests)
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
    "audioBriefing": { "enabled": true },
    "ledger": { "enabled": true }
  }
}
```

#### 2. `risks.json`
List of registered risks aligned with Commonwealth & Defence risk standards:
```json
[
  {
    "id": "R-0001",
    "displayId": "RSK-001",
    "status": "Active",
    "isTeamGoogle": false,
    "riskOwner": "Sarah Jenkins",
    "bundle": "B1 - Identity & Access",
    "driverTreeRef": "1.2b",
    "riskName": "Sovereign Identity Federation Latency",
    "riskDescription": "Cross-boundary IdP token exchange exceeds 200ms latency budget during peak shift handover periods.",
    "category": "Technical",
    "cause": "Under-provisioned HSM crypto accelerators in secondary enclave zone.",
    "impact": "Slow biometric authentication at perimeter control points.",
    "inherentLikelihood": 4,
    "inherentConsequence": 4,
    "inherentScore": 16,
    "inherentRating": "Extreme",
    "residualLikelihood": 2,
    "residualConsequence": 3,
    "residualScore": 6,
    "residualRating": "Medium",
    "treatmentStrategy": "Mitigate",
    "treatmentPlan": "Deploy hardware token caching layer and dedicated crypto-accelerated edge gateways.",
    "treatmentOwner": "Marcus Vance",
    "targetDate": "2026-09-30",
    "treatmentStatus": "In Progress"
  }
]
```

#### 3. `issues.json`
Operational issue register:
```json
[
  {
    "id": "I-0001",
    "displayId": "ISS-001",
    "status": "Active",
    "issueOwner": "David Chen",
    "priority": "Urgent",
    "issueName": "Fibre Splicing Delay at Node 4",
    "issueDescription": "Third-party contractor delayed optical patch panel delivery, stalling enclave interconnect validation.",
    "category": "Schedule",
    "bundle": "B3 - Core Network",
    "driverTreeRef": "1.10b",
    "impact": "Blocks milestone 1.10b Platform Ready signoff by 2 weeks.",
    "actionPlan": "Expedite replacement patch panels via air freight; authorize weekend overtime for splicing crews.",
    "targetResolutionDate": "2026-08-25"
  }
]
```

#### 4. `driver_tree.json`
Hierarchical contractual delivery horizon mapping capability drops to milestone gates:
```json
{
  "capabilityDrops": [
    {
      "name": "Capability Drop 1.0 (Core Sovereign Enclave MVP)",
      "lead": "Ed Louis (HJCC / FAS GCD)",
      "targetDate": "2027-02-01",
      "status": "AMBER",
      "gates": [
        {
          "ref": "1.2b",
          "name": "Milestone 1 Architecture & V&V Acceptance",
          "description": "Customer sign-off on System Requirements, V&V plan, and baseline architecture.",
          "status": "AMBER",
          "level": 2,
          "owner": "Michael Maconachie",
          "targetDate": "2026-08-31",
          "progress": 60,
          "gapCloseRef": "1",
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
        "risk": "Inference latency spikes under peak token load in air-gapped sovereign environments.",
        "trigger": "Concurrent multi-tenant query surge during shift handover."
      },
      "plans": [
        {
          "ref": "1",
          "title": "Commonwealth Acceptance Alignment",
          "status": "In Progress",
          "owner": "Sarah Jenkins",
          "targetDate": "31 Aug 2026"
        }
      ],
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

#### 6. `knowledge.json`
Blueprint knowledge and contractual reference mapping:
```json
{
  "blueprints": [
    {
      "bundle": "B1",
      "annex": "Annex A",
      "title": "Sovereign Identity & Access Management Blueprint",
      "version": "v1.4",
      "driverTreeRefs": ["1.2b", "1.7a"],
      "summary": "Architectural specifications for hardware-backed token exchange across sovereign enclave boundaries."
    }
  ]
}
```

---

## 4. Functional Requirements (Modules FR-1 through FR-9)

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
- **FR-2.2 Multi-Perspective Executive Synthesis**: Exception-first briefings tailored for Executive, Technical, and Governance leaders.
- **FR-2.3 Neural Dual-Speaker Audio Podcast**: Waveform audio player with variable speed (0.75x–2x), transcript synching, and MP3 download.

### FR-3: 5×5 Inherent & Residual Risk Heatmap (Tab 2)
- **FR-3.1 5×5 Matrix Grid**: Matrix mapping Likelihood (1–5) on the vertical axis against Impact (1–5) on the horizontal axis, colored by standard risk tiers (Green, Yellow, Amber, Red).
- **FR-3.2 Inherent vs. Residual Toggle**: Seamless toggle transitioning cell counts and vector trajectories between Inherent and Residual risk ratings.
- **FR-3.3 Interactive Focus Ring Cell Filtering**: Clicking any matrix cell highlights the cell with an active focus ring and filters the Live Risk Explorer below.
- **FR-3.4 Live Risk Explorer**: Searchable, filterable risk cards with category dropdowns, text search, and expandable mitigation accordions.

### FR-4: Issue Register (Tab 3)
- **FR-4.1 Tabular Issue Tracker**: Sortable table displaying active operational issues with Priority badges (`P0`, `P1`, `P2`, `P3`), Status indicators (`Open`, `In Progress`, `Blocked`, `Resolved`), assigned Owner, Target Resolution Date, and 1-click detail inspection.

### FR-5: Team Google Dedicated Risk Register (Tab 4)
- **FR-5.1 Scoped Google Risk View**: Dedicated tab isolating risks where `isTeamGoogle == true`, allowing delivery leads to monitor Google-owned deliverables and contractual exposure separately from vendor/partner registers.

### FR-6: Performance Trends & Velocity Analytics (Tab 5)
- **FR-6.1 Longitudinal Risk Burndown**: Line chart plotting total Inherent and Residual risk points across historical reporting periods.
- **FR-6.2 Multi-Granularity Switching**: Granularity selector toggling trend views between **Weekly**, **Bi-Weekly**, and **Monthly** intervals.
- **FR-6.3 Net Backlog Velocity**: Bar chart illustrating the rate of newly opened vs. resolved risks and issues per reporting cycle.
- **FR-6.4 Risk Cause Category Distribution**: Horizontal bar breakdown analyzing risk concentration across Schedule, Governance, Technical, and Commercial root causes.

### FR-7: Knowledge Base & Solution Blueprints (Tab 6)
- **FR-7.1 Solution Blueprint Catalog**: Card grid organizing architectural blueprints, ATO accreditation artifacts, and contractual annexes.
- **FR-7.2 NotebookLM Integration**: Deep links to curated Gemini NotebookLM instances for rapid Q&A against source documentation.

### FR-8: Contractual Horizon (CD1) Driver Tree (Tab 7)
- **FR-8.1 Hierarchical Milestone Driver Tree**: Visual capability tree mapping Level 2 Contractual Milestones (`1.7a DevSecOps`, `1.10b Platform Ready`, `1.13 IBR`, `1.14 SRR`) down to individual deliverable packages.
- **FR-8.2 Interactive Deliverable Cards**: Deliverable cards displaying milestone owners, target completion dates, RAG status pills, and clickable related risk & issue badges (`RSK-001`, `ISS-002`) that instantly cross-filter ledgers.

### FR-9: Whole Register Master Ledger (Tab 8)
- **FR-9.1 Unified Program Master Ledger**: Comprehensive tabular ledger presenting all registered risks and issues in a single master spreadsheet view, accessible via `features.ledger` or `?view=pm`.

---

## 5. Clean RESTful API & Ingestion Architecture

### 5.1 Clean RESTful Resource Contracts (`server.py`)
The backend provides a clean, cohesive REST interface designed for in-dashboard client interactions and headless automated execution:

| HTTP Method & Path | Purpose | Request Payload / Params | Response Summary |
| :--- | :--- | :--- | :--- |
| `GET  /api/status` | Probes multi-source connection health across Sheets, Drive, NotebookLM, and latest snapshot. | `?project=<slug>` | JSON `{ success: true, project, total_snapshots, total_risks, total_issues }` |
| `POST /api/sync` | Executes unified synchronization across all active project streams (Sheets, Drive, Notebooks). | `{ project: "<slug>" }` | JSON `{ status: "ok", project, summary: { snapshots, risks, issues } }` |
| `POST /api/ingest` | Parses an uploaded weekly report PDF, computes risk metrics, generates Gemini briefing, and persists new snapshot. | `{ project: "<slug>", fileName: "...", fileId: "...", fallback: false }` | JSON `{ status: "ok", project, week, snapshots }` |
| `POST /api/briefing/generate` | Generates or regenerates Gemini executive decision synthesis and multi-speaker podcast audio. | `{ project: "<slug>", week: "Week 28", fallback: false }` | JSON `{ status: "ok", project, week, synthesis, top3, sleeperOutlier, podcastScript }` |

*(Note: Transparent backward-compatible routing aliases are maintained in `server.py` for legacy `/api/sync-sheet`, `/api/sync-all`, `/api/check-drive-sync`, and `/api/sync-notebook` paths).*

### 5.2 Unified Ingestion & Processing Pipeline (`scripts/pipeline.py`)
All ingestion, parsing, metric calculation, and AI generation logic is consolidated into a single, anti-fragile module:
- **Resilient Report Parsing**: Automatically extracts week numbers and dates from diverse naming patterns (e.g. `Weekly Reporting - Week 28 - 14 Aug 2026.pdf`, `W29_Summary.pdf`, `Status_Report.pdf`) with sequential fallback.
- **Defensive Fallback Generation**: If Gemini API quota, credentials, or network connectivity fail, the pipeline automatically provides deterministic, structured executive briefings and podcast dialogues to guarantee zero UI downtime.
- **Headless CLI Interface**:
  ```bash
  # 1-Command Workspace Sync
  python3 scripts/pipeline.py --project=f-dse --sync

  # 1-Command Weekly Report Ingestion
  python3 scripts/pipeline.py --project=f-dse --ingest-report="Weekly Reporting - Week 28 - 14 Aug 2026.pdf"
  ```

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
   - The test suite (`tests/`) maintains 100% passing automated test coverage (currently **127 unit tests**) validating data schemas, live calculations, server APIs, and driver tree interactions before code is pushed to `dev`.

---

## 7. Verification Checklist & Acceptance Criteria

- [ ] Single Page Application renders all 8 active navigation tabs cleanly with zero console errors.
- [ ] Multi-project parameter routing (`?project=sample` vs `?project=f-dse`) cleanly isolates datasets.
- [ ] 5×5 Risk Heatmap toggles seamlessly between Inherent and Residual distributions, and cell clicks filter the Live Risk Explorer with active focus rings.
- [ ] Neural podcast audio player supports waveform scrubbing, variable speeds (0.75x–2x), synced transcript, and MP3 download.
- [ ] Driver tree deliverable cards display clickable related risk and issue badges that cross-filter ledgers.
- [ ] Unified pipeline engine (`python3 scripts/pipeline.py --project=<slug> --sync`) cleanly generates valid snapshot and data files without precomputed caches.
- [ ] Cloud Run deployment is secured by Identity-Aware Proxy (IAP) requiring corporate Google SSO.
- [ ] All 127 automated unit tests pass cleanly (`python3 -m unittest discover -s tests -p "test_*.py"`).
