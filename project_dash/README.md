# 🚀 Project Dash — Decoupled Risk Intelligence & Governance Platform

An ultra-responsive, zero-build executive governance and risk intelligence platform powered by **Google Gemini AI**. Project Dash provides real-time 5×5 risk heatmaps, interactive burndown velocity curves, contractual driver trees, and Gemini-generated multi-tone executive briefings with neural multi-speaker podcast audio.

---

## 🌟 Key Architecture & Capabilities

1. **Decoupled Zero-Build Architecture**:
   - Pure client-side SPA (`index.html`) using Tailwind CSS and Chart.js.
   - 100% decoupled from project-specific content — dynamic project routing via query parameters: `?project=sample` (Project Aurora public showcase) or `?project=<your-project>`.
   - Can be served via Python server, Nginx, GitHub Pages, or serverless containers (Cloud Run).

2. **Gemini Ingestion & Decision Synthesis Engine**:
   - Ingestion CLI (`scripts/ingest_data.py`) automatically ingests Google Sheets, Google Drive PDF report packs, and knowledge documents into high-performance precomputed caches (`precomputed_analytics.json`).
   - Uses **Gemini 3.5 Flash** to generate structured executive syntheses tailored for 3 executive stakeholder perspectives:
     - 👔 **Executive**: Focus on milestones, strategic delivery blockers, and board actions.
     - ⚙️ **Technical**: Focus on infrastructure, security enclaves, API SLAs, and telemetry.
     - ⚖️ **Governance**: Focus on commercial gates, contractual IBR audits, and ATO accreditation.
   - Highlights **Top 3 Critical Action Cards** and early warning **Sleeper Outliers**.

3. **Neural Dual-Speaker Audio Briefing**:
   - Synthesizes dual-host executive discussion podcasts using Gemini TTS (`MultiSpeakerVoiceConfig` with `Puck` and `Aoede`).
   - Built-in neural waveform player with variable playback speed, auto-scrolling synced transcript, and direct MP3 export.

4. **Multi-Register 5×5 Risk & Issue Matrix**:
   - Dynamic Inherent vs. Residual risk matrix toggling with active cell focus rings and 1-click filtering (`↗`).
   - Longitudinal risk burndown and net backlog velocity tracking across Weekly, Bi-Weekly, and Monthly granularities.

5. **Contractual Driver Tree & Capability Horizon**:
   - Visual capability drop trees linking milestone gates directly to high-priority remediation plans and active risks.

6. **Knowledge Base & Solution Blueprints**:
   - Deep contract traceability and technical blueprint catalog mapping deliverable bundles to active risks.

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.10+
- (Optional for AI generation) Google Cloud ADC or `GEMINI_API_KEY`

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/your-org/project-dash.git
cd project_dash

# Copy environment template
cp .env.example .env

# (Optional) Authenticate with Google Cloud ADC for Vertex AI:
gcloud auth application-default login
```

### 3. Ingest Data & Precompute Analytics
```bash
# Ingest and precompute the sample showcase dataset (Project Aurora)
python3 scripts/ingest_data.py --project=sample
```

### 4. Run the Development Server
```bash
# Start the local development server on port 9000
python3 server.py

# Or use the background runner script:
./run_server.sh
```

Open your browser at:
👉 **Sample Showcase**: `http://localhost:9000/?project=sample`

---

## 📁 Directory Structure & Multi-Project Isolation

All project-specific data is strictly isolated inside the `data/<project-slug>/` directory:

```
project_dash/
├── index.html                   # Zero-build single-file frontend presentation engine
├── server.py                    # Parameterized HTTP server & On-demand sync APIs
├── .env.example                 # Environment configuration template
├── .gitignore                   # Strict sanitization rules
├── prompts/
│   ├── exec_summary_prompt.md   # Gemini structured JSON executive summary prompt
│   └── podcast_prompt.md        # Gemini dual-speaker podcast script prompt
├── scripts/
│   ├── ingest_data.py           # Master Ingestion Orchestrator CLI
│   ├── gemini_generator.py      # Gemini 3.5 synthesis & TTS audio generator
│   └── precompute_analytics.py  # High-performance analytics precomputation engine
├── data/
│   └── sample/                  # Public showcase dataset (Project Aurora)
│       ├── config.json          # Project branding, theme colors, feature flags
│       ├── risks.json           # 5x5 Inherent & Residual risk registry
│       ├── issues.json          # Operational issue register
│       ├── snapshots.json       # Longitudinal weekly snapshots (W22-W27)
│       ├── knowledge.json       # Blueprint & contract knowledge sources
│       ├── driver_tree.json     # Contractual milestones & capability drops
│       └── precomputed_analytics.json # Precalculated matrix & trend caches
└── tests/                       # Complete automated unit test suite
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
   python3 scripts/ingest_data.py --project=my-project
   ```

5. **View in browser**:
   Navigate to `http://localhost:9000/?project=my-project`.

---

## 🧪 Testing & Quality Assurance

Project Dash includes a comprehensive unit test suite covering data integrity, precomputed caches, Gemini generation, server endpoints, and frontend decoupling:

```bash
# Run all automated unit tests
python3 -m unittest discover tests

# Run specific test suites
python3 -m unittest tests/test_gemini_generator.py
python3 -m unittest tests/test_ingest_data.py
python3 -m unittest tests/test_server_parameterized.py
```

---

## 🔒 Security & Privacy

- **Strict Isolation**: Proprietary datasets (such as `data/f-dse/` or `data/local/`) and secret keys (`.env`) are excluded in `.gitignore`.
- **Zero Hardcoded Secrets**: Gemini API calls support standard Google Cloud Application Default Credentials (ADC) or environment-managed keys.

---

## 📄 License
Licensed under the Apache 2.0 License.
