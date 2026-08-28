# 🚀 Project Dash — Decoupled Risk Intelligence & Governance Platform

An ultra-responsive, decoupled executive governance and operational risk intelligence platform. Project Dash provides real-time 5×5 risk heatmaps, interactive burndown velocity curves, contractual driver trees, and integrated **Google Gemini AI** executive briefings with dual-speaker audio podcasts.

---

## 🌟 Key Architecture & Capabilities

1. **Decoupled Architecture & Multi-Project Routing**:
   - Pure client-side SPA (`index.html`) using Tailwind CSS and Chart.js.
   - 100% decoupled from project-specific content — dynamic project routing via query parameters: `?project=sample` (Project Aurora public showcase) or `?project=<your-project>`.
   - Can be served via Python server, Nginx, GitHub Pages, or serverless containers (Cloud Run).

2. **Gemini Ingestion & Decision Synthesis Engine**:
   - Ingestion CLI (`scripts/pipeline.py`) automatically ingests Google Sheets, Google Drive PDF report packs, and knowledge documents into standardized project datasets (`snapshots.json`, `risks.json`, `issues.json`).
   - Uses **Gemini 3.5 Flash** to generate structured executive syntheses tailored for 3 executive stakeholder perspectives:
     - 👔 **Executive**: Focus on milestones, strategic delivery blockers, and board actions.
     - ⚙️ **Technical**: Focus on infrastructure, security enclaves, API SLAs, and telemetry.
     - ⚖️ **Governance**: Focus on commercial gates, contractual IBR audits, and ATO accreditation.
   - Highlights **Top 3 Critical Action Cards** and early warning **Sleeper Outliers**.

3. **Neural Dual-Speaker Audio Briefing**:
   - Synthesizes dual-host executive discussion podcasts using Gemini TTS (`MultiSpeakerVoiceConfig` with `Puck` and `Aoede`).
   - Built-in neural waveform player with variable playback speed, auto-scrolling synced transcript, and direct MP3 export.

4. **Multi-Register 5×5 Risk & Issue Matrix & Clean Register Isolation**:
   - Explicitly separated tabs for **Internal Risks** (107 primary items) and **Team Google Risks** (12 technical items) with dedicated matrices, provenance tooltips, and ownership filters.
   - Dynamic Inherent vs. Residual risk matrix toggling with active cell focus rings and 1-click filtering (`↗`).
   - Longitudinal risk burndown and net backlog velocity tracking across Weekly, Bi-Weekly, and Monthly granularities.

5. **Global "Google Need-to-Know" & "Looking Around the Corner" Strategic Advisory**:
   - Persistent top-level **Google Need-to-Know** notification banner visible across all tabs with collapsible state persistence.
   - **Looking Around the Corner (30-60 Day Horizon)** predictive advisory in the Executive Summary synthesizing supply chain lead times, cross-register gaps, and PDR concurrency traps.
   - Smart CD1 Driver Tree deep-linking that opens full interactive Risk Detail Modals directly from deliverable cards.

6. **Knowledge Base & Solution Blueprints**:
   - Deep contract traceability and technical blueprint catalog mapping deliverable bundles to active risks.

---

## 🚀 Quickstart

### 1. Prerequisites
- **Python 3.12+**
- **Google Cloud ADC** (`gcloud auth application-default login`) or **`GEMINI_API_KEY`** (Required for Gemini AI decision synthesis and neural podcast audio generation)

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/your-org/project-dash.git
cd project_dash

# Copy environment template
cp .env.example .env

# Authenticate with Google Cloud ADC for Vertex AI Gemini:
gcloud auth application-default login
```

### 3. Run the Development Server
```bash
# Start the local development server on port 9000
python3 server.py

# Or use the background runner script:
./run_server.sh
```

### 4. Open in Browser & Trigger Ingestion from UI
1. Open your browser at:
   👉 **Sample Showcase**: `http://localhost:9000/?project=sample`
2. Click the **"Sync with Google Drive"** / **"Workspace Sync"** button in the top navigation header.
3. The dashboard will trigger the automated ingestion pipeline, run Gemini decision synthesis, generate the neural podcast audio, and update all 5×5 matrices and trend curves in real time!

*(Optional Headless Automation CLI: `python3 scripts/pipeline.py --project=sample`)*

---

## 📁 Directory Structure & Multi-Project Isolation

All project-specific data is strictly isolated inside the `data/<project-slug>/` directory:

```
project_dash/
├── index.html                   # Zero-build single-file frontend presentation engine
├── server.py                    # Parameterized HTTP server & On-demand sync APIs
├── .env.example                 # Environment configuration template
├── .gitignore                   # Strict sanitization rules
├── docs/                        # Project operator manuals & guides
│   ├── HANDOVER_GUIDE.md        # Turnkey operator & handover manual
│   ├── TEAM_PRESENTATION_GUIDE.md # 5-minute showcase narrative
│   └── DEPLOYMENT_GUIDE.md      # Automated CI/CD & IAP security setup
├── prompts/
│   ├── exec_summary_prompt.md   # Gemini structured JSON executive summary prompt
│   └── podcast_prompt.md        # Gemini dual-speaker podcast script prompt
├── scripts/
│   ├── pipeline.py              # Unified ingestion, Drive report parsing & Gemini synthesis engine
│   ├── gemini_generator.py      # Gemini 3.5 synthesis & TTS audio generator
│   └── check_build_status.py    # Cloud Build CI/CD status query tool
├── src/
│   └── js/                      # Modular ES6 frontend architecture (api.js, state.js, analytics.js, app.js)
├── data/
│   └── sample/                  # Public showcase dataset (Project Aurora)
│       ├── config.json          # Project branding, theme colors, feature flags
│       ├── risks.json           # 5x5 Inherent & Residual risk registry
│       ├── issues.json          # Operational issue register
│       ├── snapshots.json       # Longitudinal weekly snapshots (W22-W27)
│       ├── knowledge.json       # Blueprint & contract knowledge sources
│       └── driver_tree.json     # Contractual milestones & capability drops
└── tests/                       # Complete automated unit test suite (127 tests)
```

---

## 🛠️ Adding a New Project

To add a new project (e.g. `my-project`):

1. **Create project directory**:
   ```bash
   mkdir -p data/my-project
   cp -r data/sample/* data/my-project/
   ```

2. **Customize `data/my-project/config.json`**:
   - Update `project.name`, `project.title`, `project.logoIcon`, and `theme.primaryColor`.
   - Configure data source links (`sources.googleSheets.riskRegisterUrl`, etc.).

3. **Populate your data**:
   - Update `risks.json`, `issues.json`, `snapshots.json`, `driver_tree.json`, and `knowledge.json`.

4. **Run ingestion**:
   ```bash
   python3 scripts/pipeline.py --project=my-project
   ```

5. **View in browser**:
   Navigate to `http://localhost:9000/?project=my-project`.

---

## 🧪 Testing & Quality Assurance

Project Dash includes a comprehensive unit test suite covering data integrity, live client calculations, Gemini generation, server endpoints, and frontend decoupling:

```bash
# Run all automated unit tests
python3 -m unittest discover -s tests -p "test_*.py"

# Run specific test suites
python3 -m unittest tests/test_gemini_generator.py
python3 -m unittest tests/test_pipeline.py
python3 -m unittest tests/test_server_parameterized.py
```

---

## 🚢 CI/CD & Deployment Architecture

Project Dash is deployed automatically to Google Cloud Run in Sydney, Australia (**`australia-southeast1`**) via Cloud Build:

- **Development (`monaro-risk-dash-dev`)**: Triggered automatically on pushes to the `dev` branch.
- **Production (`monaro-risk-dash-prod`)**: Triggered automatically when release tags matching `^project_dash/prod-.*$` (e.g. `project_dash/prod-v1.0.0`) are pushed on `dev`.
- **Documentation / No-Build Pushes**: To push documentation or workflow updates without triggering a Cloud Run build, include `[skip ci]` or `[ci skip]` in your commit message:
  ```bash
  git commit -m "docs: update runbooks [skip ci]"
  git push origin dev
  ```
- **Provisioning & Operations**: See [`deploy/PROD_PROVISIONING_GUIDE.md`](./deploy/PROD_PROVISIONING_GUIDE.md) for full Pantheon Click-Ops instructions, CLI scripts, operator IAM roles, and rollback runbooks.

---

## 🔒 Security & Privacy

- **Strict Isolation**: Proprietary datasets (such as `data/f-dse/` or `data/local/`) and secret keys (`.env`) are excluded in `.gitignore`.
- **Zero Hardcoded Secrets**: Gemini API calls support standard Google Cloud Application Default Credentials (ADC) or environment-managed keys.

---

## 📄 License
Licensed under the Apache 2.0 License.
