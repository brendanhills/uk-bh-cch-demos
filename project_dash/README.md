# F-DSE Program Governance & Risk Intelligence Platform

Interactive Executive Cockpit and Risk Intelligence Platform built for the **Future Data Science Environment (F-DSE)** governance lifecycle.

---

## 📖 Table of Contents
1. [🌟 Architecture & Key Capabilities](#-architecture--key-capabilities)
2. [🚀 Local Quickstart](#-local-quickstart)
3. [🖥️ Dashboard Feature & Component Guide](#️-dashboard-feature--component-guide)
   - [Global Header & Navigation Bar](#global-header--navigation-bar)
   - [Tab 1: Executive Summary & Decision Briefing (`exec-briefing`)](#tab-1-executive-summary--decision-briefing-exec-briefing)
   - [Tab 2: Joint Program Risks 5×5 Matrix (`overview`)](#tab-2-joint-program-risks-55-matrix-overview)
   - [Tab 3: Team Google Risks (`team-google`)](#tab-3-team-google-risks-team-google)
   - [Tab 4: Issue Register (`issues`)](#tab-4-issue-register-issues)
   - [Tab 5: Performance Trends & Velocity (`trends`)](#tab-5-performance-trends--velocity-trends)
   - [Tab 6: Contractual & Blueprint Knowledge Base (`blueprints`)](#tab-6-contractual--blueprint-knowledge-base-blueprints)
   - [Tab 7: CD1 Driver Tree & Gap Close Horizon (`driver-tree`)](#tab-7-cd1-driver-tree--gap-close-horizon-driver-tree)
   - [Tab 8: Whole Register Ledger (`ledger`)](#tab-8-whole-register-ledger-ledger)
   - [Global Modals & Detail Drawers](#global-modals--detail-drawers)
4. [🔄 How to Update Data (Step-by-Step Instructions)](#-how-to-update-data-step-by-step-instructions)
   - [1. Updating Weekly Status Reports (Google Drive PDF Ingestion)](#1-updating-weekly-status-reports-google-drive-pdf-ingestion)
   - [2. Updating Risk & Issue Registers (Google Sheets Sync)](#2-updating-risk--issue-registers-google-sheets-sync)
   - [3. Adding & Syncing Gemini Notebooks (Multi-Notebook Knowledge Base)](#3-adding--syncing-gemini-notebooks-multi-notebook-knowledge-base)
   - [4. Updating Audio Briefings & Transcripts](#4-updating-audio-briefings--transcripts)
   - [5. Master Data Files & Storage Reference](#5-master-data-files--storage-reference)
5. [👥 Access Control & Ganpati (MDB) Groups](#-access-control--ganpati-mdb-groups)
6. [🔒 Cloud Deployment & Operations Pipeline](#-cloud-deployment--operations-pipeline)
7. [📁 Repository Layout](#-repository-layout)
8. [🛡️ Architecture Guardrails & Engineering Best Practices](#️-architecture-guardrails--engineering-best-practices)
9. [📞 Support & Contacts](#-support--contacts)

---

## 🌟 Architecture & Key Capabilities

1. **Single Product Vanilla Architecture**:
   - High-performance, zero-build single-file SPA (`index.html`) using Tailwind CSS and Chart.js.
   - Sub-millisecond tab switching and native browser history (`pushState` / `popstate`).
2. **Executive Decision Briefing (Gemini 3.5 Pro)**:
   - Exception-first synthesis highlighting Top 3 Critical Action items, Early Warning Sleeper Outlier (`Ref 1.15`), and schedule squeeze alerts.
   - Neural Australian Audio Briefing (`en-AU-Neural2-A` & `B`) with speed controls, animated waveform, and direct download.
3. **Interactive 5×5 Risk Heatmap & Issue Cockpit**:
   - Dynamic Inherent vs. Residual matrix toggling, active focus rings, and granular 1-click citation jumps (`↗`).
4. **Performance Trends & Velocity**:
   - Dynamic Burndown and Risk Cause Category distribution with `Weekly`, `Bi-Weekly`, and `Monthly` granularity.
5. **Contractual Delivery & Gap Close Horizon**:
   - CD1 Driver Tree linking Level 2 Contractual Milestones to high-priority remediation plans.
6. **Multi-Register Governance Cockpit**:
   - **Combined Executive Summary**: Unified leadership synthesis aggregating Joint Program and Team Google risks.
   - **Joint Program Risks (107)**: Dedicated 5×5 matrix for overarching multi-party delivery obligations (Accenture/Google/Cth).
   - **Team Google Risks (12)**: Dedicated 5×5 cockpit for Google-internal engineering tasks, GDC air-gap infrastructure, and mitigations.
7. **Generalized Multi-Notebook Knowledge Base**:
   - Central Registry (`data/notebooks/registry.json`) supporting multiple Gemini Notebooks (Contracts, Technical Blueprints, Security ATO).
   - Dynamic UI dropdown selector in the Contractual Delivery / Annexes tab to switch between notebook sources seamlessly.
   - Generalized sync CLI: `python3 scripts/sync_notebook.py --notebook-id <UUID> --title "<TITLE>" --slug "<SLUG>"`.
8. **Gemini Notebook & Contract Blueprint Knowledge Base**:
   - Ingests **Project Monaro Contract Notebook** (`acdbb29b-8632-4fc7-9ba8-2357beeff141`, 17 sources).
   - Bidirectional contract traceability mapping Bundles A through L / Annexes B through L directly to risks and issues.
   - Differential sync engine and 1-click Workspace Sync (`/api/sync-notebook`).

---

## 🚀 Local Quickstart

```bash
# 1-Command Server Lifecycle & Tmux Management
./run_server.sh           # Creates tmux session if missing, starts/restarts server, attaches
./run_server.sh status    # Check live session and server port status
./run_server.sh restart   # Restart server in tmux session
./run_server.sh kill      # Stop server and kill tmux session

# Open in browser
http://localhost:9000
```

---

## 🖥️ Dashboard Feature & Component Guide

### Global Header & Navigation Bar

Located at the very top of the application, the global header provides universal status information, version indicators, and quick-access utility tools:

* **Platform Title & Home Reset**: Displays the application title and single tech stack subtitle. Clicking anywhere in the title block resets the view and returns you smoothly to the Executive Summary home tab (`exec-briefing`).
* **Live Status Badge (`F-DSE Live (Week 27)`)**: Displays the active reporting period. In live mode, this badge is styled with a green pill.
* **Time Machine Trigger (`⏱️ Time Machine`)**: Opens the Governance Time Machine modal, allowing you to instantly rewind the entire dashboard to any past reporting week (`W22` through `W27+`). When a past snapshot is active, a sticky amber notification banner appears across the top of the screen with a **"⚡ Return to Present"** button.
* **Open Sheet Button (`Open Sheet ↗`)**: Deep-links directly to the team's official Google Sheet containing the live Joint Risk & Issue Register.
* **Latest Report Pack Link (`Week 27 Pack ↗`)**: Direct deep-link to the latest weekly PDF reporting pack in the team's shared Google Drive folder. Includes an animated live pulse indicator.
* **Workspace Sync Hub (`Sync`)**: Opens the multi-stream synchronization modal. Displays an animated badge (`!`) whenever a new, uningested weekly PDF report is detected in Google Drive.
* **Navigation Tabs Bar**: Sticky tab bar enabling sub-millisecond navigation across all 8 functional areas with URL hash and browser history support.

---

### Tab 1: Executive Summary & Decision Briefing (`exec-briefing`)

The default landing tab designed for executive leadership, steering committees, and joint board meetings. It condenses complex multi-register data into a rapid 2-minute decision brief.

#### Key Components:
1. **Executive Cockpit Status Bar & 4-Pillar KPI Strip**:
   - **Overall Status Badge**: Shows portfolio RAG status (e.g. `🟡 AMBER (Stable)`).
   - **4 KPI Summary Pills**:
     - `Commercial`: Tracks commercial contract posture (`🟢 ON TRACK`).
     - `Milestone 2`: Tracks Milestone 2 / IBR progress (`🟡 DUE AUG 26 (85%)`).
     - `ATO-C Gate`: Tracks security accreditation readiness (`🟢 GREEN`).
     - `Escalations`: Highlights active executive escalations (`🔴 5 ITEMS`).
2. **Gemini 3.5 Pro Executive Decision Synthesis Hero Card**:
   - **Exception-First AI Narrative**: AI-generated synthesis highlighting core achievements, active blockers, and portfolio-level risk deltas.
   - **Clickable Driver Citations**: Embedded deep-links (e.g. `Ref 1.10b ↗`, `Ref 1.2b ↗`) that jump directly to specific deliverable cards in the Driver Tree.
   - **1-Click Copy Synthesis Button (`📋 Copy Synthesis & Top 3`)**: Copies the formatted executive text and top priorities directly to your clipboard for status emails and slide decks.
3. **Top 3 Critical Executive Attention Items**:
   - Three high-visibility action cards outlining immediate priorities:
     - **Item 1: Commonwealth Acceptance (`Ref 1.2b`, Gap #1)**: Executive engagement for deliverable sign-offs.
     - **Item 2: SRR Prioritization Glide Path (`Ref 1.14`, Gap #4)**: System Requirements Review prioritization.
     - **Item 3: GDC Platform Ready (`Ref 1.10b`, Gap #3)**: Test/dev infrastructure enablement.
   - Each card displays the target date, impact description, and 1-click citation links (`↗`).
4. **Early Warning Sleeper Outlier Watch**:
   - A dedicated purple alert card flagging **Ref 1.15 (Milestone 3 PDR)**. While currently reported as `🟢 GREEN`, the card warns of schedule compression created by the downstream SRR shift, preventing unexpected red status surprises.
5. **Australian Neural Audio Briefing Player (`en-AU-Neural2`)**:
   - **Podcast Player Bar**: Dual-voiced (`Alex & Jordan`) 90-second conversational briefing.
   - **Interactive Controls**: Play/Pause, animated waveform visualizer, time scrubber, and speed controls (`1.0x`, `1.25x`, `1.5x`).
   - **Transcript Button (`📜 Transcript`)**: Opens a modal with the complete audio script.
   - **Download Audio Button**: One-click download of the MP3 audio file.
6. **Active Issue/Risk or Escalation Being Tracked with Gap Close Plan**:
   - Official remediation tracker reflecting Pages 4–5 of the weekly report pack.
   - **Dynamic Baseline Diffing Dropdown**: Allows users to compare current progress against *Last Week (Week 25)*, *2 Weeks Ago (Week 24)*, or *1 Month Ago (Week 22)* to highlight weekly deltas.
7. **Side-by-Side Top 5 Critical Risks & Top 5 Escalated Issues**:
   - Ranked lists of the most critical risks (by residual score) and top escalated issues, each with direct links to view the full matrix or register.
8. **Near-Term Deliverables & Schedule Squeeze Barometer**:
   - Three zero-float squeeze cards quantifying timeline compression across upcoming gates: *Milestone 2 (IBR)*, *SRR to PDR Compression*, and *Facilities to Enclave Ready Compression*.

---

### Tab 2: Joint Program Risks 5×5 Matrix (`overview`)

The central analytical workspace for multi-party consortium delivery obligations across Accenture, Google, and the Commonwealth.

#### Key Components:
1. **5×5 Risk Heatmap Matrix**:
   - Standard 5×5 risk matrix plotting **Likelihood** (1–5) against **Consequence** (1–5).
   - **Inherent vs. Residual Toggle**: Seamlessly switch between Inherent (Pre-Control) and Residual (Post-Control) ratings to visualize the impact of mitigation treatments.
   - **Status Filter Buttons**: Filter matrix counts by `Open (99)`, `Active (78)`, `Eventuated (21)`, `Closed (8)`, or `All (107)`.
2. **Top 3 KPI Quick Filter Cards**:
   - `🔴 Critical Exposure Risks`: Filters for high-severity risks (Scores 18–25).
   - `⚠️ Eventuated Issues`: Filters for eventuated risk items escalated into active issues.
   - `🟡 Unactioned Risks`: Filters for active risks requiring mitigation plan updates.
3. **Active Focus Ring & Heatmap Cell Filtering**:
   - Clicking any cell in the 5×5 grid (e.g. *Likelihood 4, Consequence 3*) locks focus on that cell with an active focus ring and instantly filters the Live Risk Explorer below.
   - An active filter banner appears with a **"✕ Clear Matrix Filter"** button.
4. **Live Risk Explorer & Triage**:
   - **View Mode Switcher**: Toggle between `📇 Cards View` (rich cards with treatment plans, owners, and delta notes) and `📑 Compact Table` (dense spreadsheet-like view).
   - **Full-Text Search**: Search instantly by Risk ID, statement, owner, root cause, treatment plan, or Driver Ref.
   - **Quick Preset Chips**: Fast one-click filtering by `All Risks (107)`, `Score ≥ 18 (4)`, `Trending Worse (1)`, `Eventuated Issues (21)`, `Joint Exec Escalations (5)`, and `Reset All Filters`.
   - **Faceted Filter Dropdowns**: Filter by Bundle / Workstream (e.g., Bundle G, A.AO, F, I, L), Cause Category (Schedule, Cost, Scope, Governance, Legal, SovOps), Governance Level (Internal Google, Team Google, PSG, IPF), and Status.
   - **Item Detail Modal (`↗`)**: Clicking any ticket opens the comprehensive risk inspector modal.

---

### Tab 3: Team Google Risks (`team-google`)

A dedicated, Google Blue-themed risk cockpit focused strictly on Google-internal engineering tasks, GDC air-gap hardware, firmware baseline drift, crypto key ceremonies, and sovereign logistics.

#### Key Components:
1. **Team Google 5×5 Heatmap Matrix**:
   - Dedicated matrix isolating the 12 Google delivery workstream tasks.
   - Supports Inherent (Gross) vs. Residual (Net) switching and status filtering.
2. **Direct Google Sheet Link**:
   - Direct shortcut button opening the official Team Google risk register spreadsheet.
3. **Top 3 KPI Cards for Team Google**:
   - `Critical Google Exposure (18-25)`: Highlights critical items such as HSM Key Management and Interconnect lead times.
   - `Active Delivery Tasks (11)`: Active workstream items under mitigation.
   - `Resolved / Closed (1)`: Successfully resolved tasks (e.g. SAML token expiry).
4. **Team Google Risk Explorer**:
   - Live search input and category filter covering *Engineering/Platform*, *Security/Compliance*, *Architecture/AI*, *Supply Chain/Delivery*, and *Governance*.

---

### Tab 4: Issue Register (`issues`)

A streamlined cockpit dedicated to real-time tracking of operational blockers, escalated delivery impediments, and eventuated risks.

#### Key Components:
1. **Issue Count & Live Search**:
   - Header badge displaying the active issue count (29 Issues).
   - Search bar filtering by issue ID, name, owner, description, or action plan.
2. **Sticky-Header Issue Table**:
   - Dense, high-visibility table displaying:
     - **ID & Status**: Ticket ID and lifecycle status badge.
     - **Owner & Driver Ref**: Assigned workstream lead and contractual gate reference.
     - **Issue Statement & Name**: Detailed description of the operational blocker.
     - **Severity**: Color-coded severity rating.
     - **Governance Action Plan**: Agreed mitigation strategy and target resolution date.
     - **Details Button (`↗`)**: Opens the full Item Detail Modal.

---

### Tab 5: Performance Trends & Velocity (`trends`)

Longitudinal analytics visualizing project trajectory, intake velocity, burndown rate, and root-cause concentration.

#### Key Components:
1. **Multi-Granularity Switcher**:
   - Switch chart intervals between `Monthly`, `Bi-Weekly`, and `Weekly` views.
2. **Risk Volume & Intake vs. Closures (Backlog Chart)**:
   - Dynamic Chart.js stacked bar and line chart comparing total active backlog against newly opened and closed items per reporting period.
3. **Risk Mitigation Score Performance (Burndown Chart)**:
   - Visualizes portfolio-wide mitigation velocity by tracking the spread between Inherent Score (Pre-Control) and Residual Score (Post-Control) across time.
4. **Risk Cause Category Concentration**:
   - Horizontal bar chart identifying systemic failure modes across *Schedule*, *Governance*, *Scope*, *Cost*, *Legal/Contract*, and *SovOps*.
5. **Risk Severity Profile**:
   - Breakdown of portfolio risk scores across standard 5×5 severity bands.
6. **Interactive Timeline Drill-Down Modal**:
   - Clicking any historical bar opens a granular modal displaying exact snapshot metrics and a **"⏳ Time travel to this week"** button.

---

### Tab 6: Contractual & Blueprint Knowledge Base (`blueprints`)

Grounded directly against Gemini NotebookLM, this tab provides bidirectional traceability between technical solution blueprints (Bundles A through L / Annexes B through L) and live governance risks.

#### Key Components:
1. **Multi-Notebook Dropdown Selector**:
   - Dynamic dropdown powered by `data/notebooks/registry.json` that lets users switch between connected Gemini Notebooks (e.g. *Project Monaro Contract Notebook*, *Technical Architecture & System Blueprints*, *Security ATO Accreditation*).
2. **NotebookLM Integration**:
   - **Open in NotebookLM (`↗`)**: Direct link to open the active notebook in the NotebookLM web application.
   - **Sync Notebook Button**: 1-click trigger to synchronize notebook source catalogs and recalculate active risk counts.
3. **4 Knowledge Base KPI Summary Cards**:
   - `Ingested Sources`: Total ingested documents (17 files: PDFs, Markdown, Contracts).
   - `Solution Blueprints`: Total solution bundles (10 bundles: Annexes B through L).
   - `Contract Traceability`: Percentage of contract annexes mapped to active risks (100% mapped).
   - `Sync Engine`: Differential cache status.
4. **Solution Blueprint & Technical Annex Cards (Bundles A through L)**:
   - Detailed cards for each contract bundle (e.g. *Bundle B: Security / ATO-C*, *Bundle C: AI & ML Analytics*, *Bundle H: Managed Infrastructure & GDC Hardware*).
   - Displays version, driver tree links, document summary, and **Live Risk Counter Badges** (Joint Risks and Team Google Risks) with 1-click filter jumps into the risk explorer.
5. **Research, Governance & Supporting Documentation Grid**:
   - Document cards for *Commonwealth Head Agreement Schedule 4 (Milestones)*, *Schedule 7 (Security)*, *Joint Governance Charters*, and *Subcontractor Verification Protocols*.

---

### Tab 7: CD1 Driver Tree & Gap Close Horizon (`driver-tree`)

Direct structural decomposition of contractual gates, RAG status, deliverable leads, baseline vs. forecast dates, and linked gap closure plans.

#### Key Components:
1. **Tier 0 Objective & Tier 1 Capability Drops**:
   - Displays overarching Tier 0 Defence objective and breakdown of **Capability Drop 1 (CD1, Feb 2027)** and **Capability Drop 1.5 (CD1.5, Aug 2027)**.
   - **View Deck Button (`📄 View Week 27 Deck ↗`)**: Deep-links to the full slide pack on Google Drive.
2. **Level Decomposition Filter**:
   - Toggle between `All Items`, `Level 2 (Primary Gates)`, and `Level 3 (Work Packages)`.
3. **24 Contractual Deliverable Cards**:
   - Interactive cards for all key gates (e.g. `1.2b M1 Acceptance`, `1.6 Facilities`, `1.7a DevSecOps`, `1.10b E.01 Platform Ready`, `1.13 IBR`, `1.14 SRR`, `1.15 PDR`, `3.1 ADR`).
   - Displays status badge (Red, Amber, Green, Blue), workstream lead, target delivery date, baseline shift notes, and linked Gap Close Plan numbers.

---

### Tab 8: Whole Register Ledger (`ledger`)

A full audit ledger intended for Project Managers and compliance officers.

#### Key Components:
* **Access Mode**: Hidden by default from standard executive view; activated via URL parameters `?view=pm` or `?ledger=true`.
* **Complete Tabular Ledger**: Unfiltered table of all 107 risks with IDs, statements, owners, categories, driver refs, inherent/residual scores, status, and target dates.
* **1-Click CSV Export (`📥 Export CSV`)**: Exports the entire register to a downloadable CSV file.

---

### Global Modals & Detail Drawers

* **Item Detail Modal / Inspector Drawer**:
  - Displays full ticket metadata, inherent vs. residual 5×5 score matrix comparisons, root cause descriptions, assigned mitigation treatment plans, historical update notes, and linked contract blueprint annexes.
* **Time Machine Modal**:
  - Displays all indexed historical reporting weeks (`W22` to `W27+`). Clicking any week instantly re-renders the dashboard in that historical state.
* **Timeline Week Drill-Down Modal**:
  - Displays velocity breakdown, net closure delta, and burndown score for any selected period from the Performance Trends tab.
* **Multi-Stream Workspace Live Sync Hub Modal (`sheetsModal`)**:
  - Centralized management hub for all 4 external sync streams:
    1. Joint Program Risk & Issue Register (Google Sheet)
    2. Team Google Risk Register (Google Sheet)
    3. Weekly Status Reports Archive (Google Drive Folder)
    4. Project Knowledge & Contract Blueprints (NotebookLM)
  - Features single-click **"⚡ Sync All Workspace Sources Now"** action.
* **Podcast Audio Transcript Modal**:
  - Complete, verbatim dialogue transcript of the Australian Neural Audio Briefing with speaker tags for Alex and Jordan.

---

## 🔄 How to Update Data (Step-by-Step Instructions)

The platform supports a robust, multi-stream data architecture that synchronizes data across Google Drive, Google Sheets, and Gemini NotebookLM.

```
                  ┌─────────────────────────────────────────┐
                  │          External Sources               │
                  └────┬─────────────────┬────────────────┬─┘
                       │                 │                │
           Weekly PDF  │    Google Sheet │    NotebookLM  │
             Reports   │    Registers    │    Blueprints  │
                       ▼                 ▼                ▼
            ┌──────────────────┐┌──────────────────┐┌──────────────────┐
            │ Google Drive     ││ Google Sheets    ││ Gemini Notebook  │
            │ Shared Folder    ││ (Joint & Google) ││ Ingestion Engine │
            └─────────┬────────┘└────────┬─────────┘└────────┬─────────┘
                      │                  │                   │
                      ▼                  ▼                   ▼
            ┌──────────────────┐┌──────────────────┐┌──────────────────┐
            │ ingest_weekly_   ││ /api/sync-sheet  ││ sync_notebook.py │
            │ report.py        ││ (live data sync) ││ (catalog & map)  │
            └─────────┬────────┘└────────┬─────────┘└────────┬─────────┘
                      │                  │                   │
                      ▼                  ▼                   ▼
            ┌──────────────────────────────────────────────────────────┐
            │                  Local Storage Layer                     │
            │  • src/data/weekly_snapshots.json                        │
            │  • src/data/live_synced_data.json                        │
            │  • data/notebooks/registry.json                          │
            └────────────────────────────┬─────────────────────────────┘
                                         │
                                         ▼
            ┌──────────────────────────────────────────────────────────┐
            │        index.html (Executive Dashboard Single-Page App)  │
            └──────────────────────────────────────────────────────────┘
```

---

### 1. Updating Weekly Status Reports (Google Drive PDF Ingestion)

When a new weekly risk and status pack arrives (e.g. *Week 28 - 14 Aug 2026*):

#### Method A: 1-Click Sync from Dashboard Web UI (Recommended)
1. Drop the new weekly PDF report (e.g. `Weekly Reporting - Week 28 - 14 Aug 2026.pdf`) into the team's shared Google Drive folder:
   - **Drive Folder**: [Open F-DSE Drive Folder](https://drive.google.com/corp/drive/folders/1JIsbi35mXn4W-NxjbLTWo22FQMv_zv-C) (`1JIsbi35mXn4W-NxjbLTWo22FQMv_zv-C`)
2. Open the dashboard in your browser (`http://localhost:9000`).
3. Notice the amber **`!`** alert badge on the **Sync** button in the top header.
4. Click **Sync** to open the Multi-Stream Sync Hub.
5. In the **Weekly Status Reports Archive** section, click **↻ Scan Drive** or click **⚡ Sync All Workspace Sources Now**.
6. The dashboard will automatically:
   - Index the new week (e.g. `Week 28`).
   - Update `src/data/weekly_snapshots.json`.
   - Update the latest pack link in the header (`Week 28 Pack ↗`).
   - Add `Week 28` to the Time Machine and Baseline Diff selector.
   - Refresh the Executive Briefing and KPI metrics.

#### Method B: Local Python CLI Ingestion Script
You can also run the ingestion script directly from the terminal:
```bash
# Ingest by specifying Drive File ID and file name:
python3 scripts/ingest_weekly_report.py \
  --file-id "<DRIVE_FILE_ID>" \
  --name "Weekly Reporting - Week 28 - 14 Aug 2026.pdf" \
  --week 28 \
  --date "14 Aug 2026"
```

---

### 2. Updating Risk & Issue Registers (Google Sheets Sync)

When risk owners, treatment plans, or likelihood/consequence scores are updated in Google Sheets:

#### Method A: 1-Click Sync from Dashboard Web UI
1. Make your edits in either official Google Sheet:
   - **Joint Risk & Issue Register**: [Open Joint Sheet](https://docs.google.com/spreadsheets/d/1qR1tEHFs0QC6CGSUpzHgVgolcF0zQNcg99yZgJwoMVY/edit)
   - **Team Google Risk Register**: [Open Team Google Sheet](https://docs.google.com/spreadsheets/d/1lNRf5NEBd6ygc91nNwFA4HWGFfbDK02QkbkVfr4OUoA/edit?gid=0#gid=0)
2. In the dashboard header, click **Sync** $\rightarrow$ **⚡ Sync All Workspace Sources Now**.
3. The dashboard reloads the latest records from `/api/sync-sheet`, updating the 5×5 matrices, issue counts, search index, and KPI totals in real time.

#### Method B: Updating Offline / Static JSON Datasets
If working offline without server connectivity:
1. Update `src/data/live_synced_data.json` and `data/sheets/live_synced_data.json`.
2. Ensure each risk item adheres to the expected JSON schema:
```json
{
  "id": "RSK-010",
  "displayId": "10",
  "status": "Active",
  "riskOwner": "Susan Allin",
  "bundle": "Bundle L",
  "driverTreeRef": "1.2b",
  "riskName": "Highly onerous Incident Management notification obligations",
  "riskDescription": "Contract mandates strict incident reporting SLAs...",
  "causeCategory": "Schedule",
  "trend": "↔",
  "priority": "Urgent",
  "governanceLevel": "Internal Google",
  "inherentLikelihood": 4,
  "inherentConsequence": 4,
  "inherentRiskScore": 21,
  "inherentRiskLevel": "High",
  "treatmentOwner": "Susan Allin",
  "treatmentPlan": "Execute strategic change plan for working group level...",
  "targetDate": "31-Aug-2026",
  "residualLikelihood": 4,
  "residualConsequence": 4,
  "residualRiskScore": 21,
  "residualRiskLevel": "High",
  "sourceRegister": "joint"
}
```

---

### 3. Adding & Syncing Gemini Notebooks (Multi-Notebook Knowledge Base)

The platform supports connecting multiple Gemini NotebookLM knowledge bases.

#### Method A: Syncing Current Active Notebook from Web UI
1. Navigate to the **📚 Blueprint Knowledge** tab.
2. Click **Sync Notebook** in the header banner.
3. The differential sync engine re-scans the catalog and recalculates risk mapping totals.

#### Method B: Registering a New Gemini Notebook via CLI
To connect an entirely new Gemini Notebook (e.g. *Commercial Contracts*, *Technical Architecture*, or *ATO Security*):
```bash
python3 scripts/sync_notebook.py \
  --notebook-id "<GEMINI_NOTEBOOK_UUID>" \
  --title "Technical Architecture & System Blueprints" \
  --slug "tech_blueprints" \
  --category "Architecture & Engineering" \
  --description "Vertex AI Enclaves, Diode Ingestion, and GDC Infrastructure Specifications"
```

This command will:
1. Register the new notebook in `data/notebooks/registry.json`.
2. Generate catalog and bundle mapping JSON files in `data/notebooks/`.
3. Recalculate dynamic active risk counters across all bundles.
4. Add the notebook to the **Notebook Dropdown Selector** in the UI.

---

### 4. Updating Audio Briefings & Transcripts

When publishing a new weekly executive audio briefing:
1. Place the generated audio file into the `assets/` directory (e.g. `assets/podcast_w28.mp3`).
2. Update the audio source and title in `index.html`:
   - Search for `#nativePodcastAudio` and update the `src` attribute.
   - Search for `#podcastTitleText` and update the episode title.
   - Search for `#podcastTranscriptContent` and paste the updated conversation transcript.

---

### 5. Master Data Files & Storage Reference

| File / Path | Purpose & Description | Update Method | Downstream UI Dependencies |
| :--- | :--- | :--- | :--- |
| **`src/data/weekly_snapshots.json`** | Historical multi-week snapshots (`w22`–`w27+`), executive KPIs, and gap close plans. | `scripts/ingest_weekly_report.py` / Sync Hub | Time Machine, Executive Cockpit, Baseline Diffing, Driver Tree |
| **`src/data/live_synced_data.json`** | Master live dataset containing all 107 Joint Risks, 12 Team Google Risks, and 29 Issues. | `/api/sync-sheet` / Google Sheets | 5×5 Risk Matrices, Risk Explorer, Issue Register, Trends |
| **`data/notebooks/registry.json`** | Central registry of all connected Gemini Notebooks. | `scripts/sync_notebook.py` | Blueprint Knowledge Tab dropdown selector |
| **`data/notebooks/*_catalog.json`** | Catalog of ingested documents, token counts, and categories for a specific notebook. | `scripts/sync_notebook.py` | Document count badges, Research repository cards |
| **`data/notebooks/*_mapping.json`** | Bidirectional mapping linking contract bundles to active Joint and Team Google risks. | `scripts/sync_notebook.py` | Solution Blueprint cards, active risk count badges |

---

## 👥 Access Control & Ganpati (MDB) Groups

Authentication and access control are governed through Google-native **Ganpati (MDB)** Prod groups synced to Google Cloud via **TwoSync**:

| Group Name | Ganpati Namespace / Type | TwoSync Identity (GCP IAM) | Purpose & Target Audience |
| :--- | :--- | :--- | :--- |
| **`monaro-risk-admin`** | `prod` / `ADMIN` | `monaro-risk-admin@twosync.google.com` | **Admin / Ownership Group**: Administers access rules and owns the dev/prod team groups. Self-owned by technical leads. |
| **`monaro-risk-dev`** | `prod` / `TEAM` | `monaro-risk-dev@twosync.google.com` | **Development & Engineering**: Engineers and data developers who can deploy updates and access dev/staging builds. |
| **`monaro-risk-prod`** | `prod` / `TEAM` | `monaro-risk-prod@twosync.google.com` | **Production Stakeholders & Viewers**: Executive stakeholders (e.g. `allins@google.com`), PMs, and cross-functional governance viewers. |

### Adding Members to Groups
1. Open the group in Ganpati:
   - **Admin**: [https://ganpati2.corp.google.com/group/%25monaro-risk-admin.prod](https://ganpati2.corp.google.com/group/%25monaro-risk-admin.prod)
   - **Dev**: [https://ganpati2.corp.google.com/group/%25monaro-risk-dev.prod](https://ganpati2.corp.google.com/group/%25monaro-risk-dev.prod)
   - **Prod (Viewers)**: [https://ganpati2.corp.google.com/group/%25monaro-risk-prod.prod](https://ganpati2.corp.google.com/group/%25monaro-risk-prod.prod)
2. Navigate to the **Children** tab $\rightarrow$ click **Propose New Children**.
3. Add the individual Googler LDAPs (members can be from any team or organization across Google).
4. Submitting the proposal automatically approves it (since `monaro-risk-admin` owns the groups).

### TwoSync Registration
To sync Ganpati groups to GCP IAM rosters (`*@twosync.google.com`), run:
```bash
/google/src/head/depot/google3/security/twosync/tools/register.sh --group monaro-risk-dev
/google/src/head/depot/google3/security/twosync/tools/register.sh --group monaro-risk-prod
```

---

## 🔒 Cloud Deployment & Operations Pipeline

The platform includes a secured, private deployment pipeline to Google Cloud Run configured via `.env` with explicit Dashboard Viewer and Admin access controls, domain security, and immediate shutdown capabilities:

### 1. Configure Role-Based Access in `.env`
Copy `.env.example` to `.env` and configure your authorized viewers and admins:
```bash
# --- Dashboard Viewers (Can view dashboard via Google SSO) ---
DASHBOARD_VIEWER_GROUPS="monaro-risk-prod@twosync.google.com"
DASHBOARD_VIEWER_USERS="brendanhills@google.com,allins@google.com"

# --- Dashboard Admins / Editors (Can deploy updates and manage revisions) ---
DASHBOARD_ADMIN_GROUPS="monaro-risk-dev@twosync.google.com"
DASHBOARD_ADMIN_USERS="brendanhills@google.com"

# --- Security & Domain Restrictions ---
BLOCKED_DOMAINS="altostrat.com"
```

### 2. Deploy to Cloud Run
```bash
# 1-Click deploy using settings from .env
./deploy/deploy_gcp.sh

# Or optionally override/add viewers or admins via CLI flags
./deploy/deploy_gcp.sh \
  --viewer-group "monaro-risk-prod@twosync.google.com" \
  --admin-group "monaro-risk-dev@twosync.google.com"
```

### 3. Check Live Status & Role Policies
```bash
# Check if the service is online, its URL, and current Viewer and Admin bindings
./deploy/deploy_gcp.sh --status
```

### 4. Immediate Service Shutdown (Stop Server)
Whenever you need to immediately stop the service and take the dashboard offline (like `sudo shutdown -h now`):
```bash
# 1-Click Service Shutdown
./deploy/shutdown.sh

# Or using the alias / flag
./deploy/stop.sh
./deploy/deploy_gcp.sh --stop
```

### 5. Domain Blocking & Security Rules
* **Strict Least Privilege**: Deployed with `--no-allow-unauthenticated` so only explicitly authorized Viewers and Admins can invoke or manage the service.
* **Domain Blocking**: Domains such as `altostrat.com` are strictly forbidden and blocked by pre-flight validation.

---

## 📁 Repository Layout

```
project_dash/
├── .env.example                # Environment template (Gemini API, deployment & role allowlists)
├── index.html                  # Core Single-Page Application (HTML5 / Tailwind / Chart.js)
├── server.py                   # Python server with Drive sync and ingestion APIs
├── run_server.sh               # 1-Command tmux server manager (start, attach, restart, kill)
├── package_zip.sh              # 1-Command packager for standalone zip bundle
├── deploy/                     # Cloud deployment & shutdown operations
│   ├── deploy_gcp.sh           # Private Cloud Run deployment with Viewer/Admin IAM & security
│   ├── shutdown.sh / stop.sh   # Immediate service shutdown script
│   ├── README.md               # Detailed deployment operations guide
│   ├── Dockerfile              # Production Nginx container image
│   └── nginx.conf              # Cloud Run Nginx configuration (port 8080)
├── README.md                   # Complete platform documentation and user manual
├── HANDOVER_GUIDE.md           # Turnkey operator & maintainer handover manual
├── TEAM_PRESENTATION_GUIDE.md  # Rolling team showcase narrative, delta notes & demo scripts
├── assets/                     # Audio assets (podcast_w27.mp3, podcast_w26.mp3)
├── prompts/                    # Gemini prompt templates (exec_summary_prompt.md)
├── scripts/                    # Ingestion & report processing utilities
│   ├── ingest_weekly_report.py # Automated weekly Drive report ingestion CLI
│   └── sync_notebook.py        # Multi-notebook Gemini sync and catalog CLI
├── src/data/                   # Weekly snapshots and live synced data
│   ├── weekly_snapshots.json   # Multi-week historical snapshots (w22–w27+)
│   └── live_synced_data.json   # Master live synced risk and issue register
├── data/                       # Categorized persistent data store
│   ├── drive/                  # Drive snapshots cache
│   ├── notebooks/              # Multi-notebook registry, catalogs, and bundle mappings
│   └── sheets/                 # Google Sheets live sync cache
├── tests/                      # Automated unit and regression test suite
├── archive/                    # Archived Streamlit prototype files
├── dash_v1/                    # Reference React/Vite v1 prototype
└── conductor/                  # Conductor SDD tracks, specs, and implementation plans
```

---

## 🛡️ Architecture Guardrails & Engineering Best Practices

To maintain data integrity, eliminate UI breakages, and uphold production-grade reliability across single-page applications and multi-register governance platforms:

### 1. Mandatory AST/Syntax Validation for Inline Web App Scripts
* **Rule**: Whenever modifying JavaScript inside `.html` or single-file SPA templates:
  1. Extract inline script blocks and execute `node -c <script_file.js>` to verify zero unescaped template quotes or syntax anomalies (`SyntaxError: Unexpected string`).
  2. Execute a simulated DOM runtime execution test to confirm global functions (`switchTab`, `initApp`, `renderExecBriefing`) initialize without runtime exceptions before declaring task completion.

### 2. Search & Heatmap Drill-Down Filter State Isolation
* **Rule**: When interacting with targeted analytical widgets (e.g., clicking a 5×5 Risk Heatmap cell or Blueprint Bundle badge):
  - Isolate the filter state by automatically clearing conflicting free-form search text (`explorerSearchInput.value = ''`) and overlapping category dropdowns.
  - This prevents accidental `AND` filter collisions that cause false "0 results" empty states.

### 3. Multi-Register Governance Separation Standard
* **Rule**: When hosting internal vendor workstreams (e.g., *Team Google Delivery Tasks*) alongside multi-party consortium governance (e.g., *Joint Program Risk Register*):
  - Maintain clean data tagging and isolation in memory.
  - Provide dedicated cockpit views with distinct visual branding (e.g., Google Blue theme vs. Joint Slate theme).
  - Dynamically roll up multi-register totals in Executive Decision Briefings with clear source pill badges.
  - Unify all sync pipelines into a single-pane-of-glass Live Sync Hub.

---

## 📞 Support & Contacts

* **Primary Stakeholder / Business Owner**: Allison Innes (`allins@google.com`)
* **Technical Lead**: Steve Deacon (`sdeacon@google.com`)
* **Program Lead**: Wayne Davis (`waynedavis@google.com`)
* **Initial Creator**: Brendan Hills (`brendanhills@google.com`)

