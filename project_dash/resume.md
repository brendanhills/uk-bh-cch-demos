# Project Dash — Session Resume & Compaction Summary

**Checkpoint Timestamp:** `2026-08-17 21:31:00 AEST`  
**Active Git Branch:** `dev`  
**Workspace:** `/usr/local/google/home/brendanhills/dev/uk-bh-experiments/project_dash`  
**Local Cloudtop Dev Server:** `http://uk-bh-cloudtop.c.googlers.com:9000/?project=sample`  
**Test Suite Health:** **85/85 passing cleanly** (`python3 -m unittest discover tests`).  
**Active Track Status:** Track `decouple_and_gemini_ingestion_20260817` marked **COMPLETE** (`[x]`).

---

## 🌅 Tomorrow Morning Quick-Start Checklist

### 1. Test the Local Project Switcher & Dashboards
👉 **[Open Project Aurora (Public Sample Showcase)](http://uk-bh-cloudtop.c.googlers.com:9000/?project=sample)**  
👉 **[Open Project F-DSE (Proprietary Live Instance)](http://uk-bh-cloudtop.c.googlers.com:9000/?project=f-dse)**  
* Verify the top-bar project badge (`PROJECT AURORA` vs `PROJECT F-DSE`) and the 1-click workspace switcher dropdown.
* Click between **Executive**, **Technical**, and **Governance** tone pills in the Executive Briefing to verify dynamic multi-perspective syntheses.
* Verify Top 3 Action cards, Sleeper Outlier cards, 5x5 heatmap risk matrix, and burndown velocity curves.

### 2. Verify On-Demand Server APIs
```bash
# Test Sheet Sync API for Sample
curl -s "http://localhost:9000/api/sync-sheet?project=sample" | jq .project

# Test Drive Sync API for F-DSE
curl -s "http://localhost:9000/api/check-drive-sync?project=f-dse" | jq .project
```

### 3. Review Recorded Bugs / Next Steps
* **Bug #59**: *Driver Tree gate deliverable cards related risks links/badges are not clickable* (Status: `Reported`).
  * Run `/triage_bug #59` or `/fix_bug #59` when ready to address.

---

## 🎯 Executive Summary of Session Accomplishments

1. **Complete Decoupling of Frontend Engine from Project Content (Phases 1–4)**:
   - Extracted all proprietary registers, blueprints, and snapshots into isolated `data/sample/` (Project Aurora) and `data/f-dse/` (Project F-DSE) directories.
   - Refactored `index.html` to dynamically load `config.json`, `risks.json`, `issues.json`, `snapshots.json`, `driver_tree.json`, `knowledge.json`, and `precomputed_analytics.json` based on `?project=<slug>`.
   - Added persistent top-bar project branding badge and a quick-switcher dropdown menu.

2. **Distinct Multi-Tone AI Executive Briefings**:
   - Enriched both `data/sample/snapshots.json` and `data/f-dse/snapshots.json` with tailored, rich multi-perspective syntheses (Executive, Technical, Governance), Top 3 action items, and Sleeper Outliers across all historical weeks.
   - Decoupled NotebookLM links, knowledge base sources, and dual-host neural podcast players.

3. **Backend Server Parameterization & On-Demand APIs (Phase 5)**:
   - Parameterized `server.py` to route all endpoints (`/api/sync-sheet`, `/api/check-drive-sync`, `/api/notebooks`, `/api/check-notebook-sync`) dynamically via `?project=<slug>` or `.env` defaults.
   - Added `POST /api/ingest-data` to trigger project ingestion on demand.
   - Added `POST /api/regenerate-briefing` to invoke Gemini 3.5 live on-demand synthesis regeneration.
   - Created comprehensive unit test suite `tests/test_server_parameterized.py`.

4. **Repository Sanitization & Open-Source Readiness (Phase 6)**:
   - Configured strict `.gitignore` rules to exclude secrets (`.env*`), private data (`data/f-dse/`, `data/local/`), and private audio while preserving the public showcase (`data/sample/`).
   - Created `.env.example` documenting Vertex AI Application Default Credentials (ADC), `GEMINI_API_KEY`, models, and project defaults.
   - Rewrote open-source [`README.md`](./README.md) with quickstart guides, multi-project directory isolation, and automated Gemini ingestion instructions.

5. **Bug Reporting Protocol**:
   - Recorded Bug #59 into `.agents/bugs.json` per protocol without premature code modification.

---

## 🧪 Verification & Test Suite Status

```bash
# Run full automated test suite
python3 -m unittest discover tests
# Result: Ran 85 tests in 4.35s -> OK (100% Passing)

# Validate JavaScript syntax
node -c index.html extracted script blocks -> OK (0 Syntax Errors)
```

---

## 📁 Repository Directory Structure

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
│   ├── sample/                  # Public showcase dataset (Project Aurora)
│   └── f-dse/                   # Proprietary live delivery dataset
└── tests/                       # Complete automated unit test suite (85 tests)
```
