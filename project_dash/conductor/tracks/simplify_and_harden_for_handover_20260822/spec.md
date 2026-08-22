# Specification: Simplify & Harden Platform for Turnkey Handover

## Overview
Transform the Project Dash backend and ingestion architecture from a fragmented collection of ad-hoc scripts and endpoints into an anti-fragile, cohesive, and simplified platform suitable for long-term ownership by less technical maintainers.

## Core Problem Statement
1. Ingestion is fragmented across 4 separate scripts (`ingest_data.py`, `ingest_weekly_report.py`, `sync_notebook.py`, `gemini_generator.py`).
2. Server API exposes 10 ad-hoc endpoints (`/api/sync-sheet`, `/api/sync-all`, `/api/check-drive-sync`, `/api/notebooks`, `/api/check-notebook-sync`, `/api/sync-notebook`, `/api/ingest-report`, `/api/ingest-data`, `/api/regenerate-briefing`) with mixed GET/POST semantics.
3. Report parsing relies on fragile filename conventions that fail on non-standard PDF names.
4. Error handling is distributed and produces silent UI failures when API keys or permissions are misconfigured.

## Functional Requirements
1. **Consolidated Ingestion Pipeline (`scripts/pipeline.py`)**:
   - Single unified module replacing disparate scripts with a clean CLI interface (`python3 scripts/pipeline.py --project=f-dse --sync` and `--ingest-report=<path_or_id>`).
   - Resilient multi-modal report parser: extracts week and date using flexible heuristics (filename, PDF text metadata, date timestamps, and sequential fallback).
   - Robust fallback AI generation: if Gemini API key is missing or quota fails, generates deterministic, structured executive summaries without crashing.

2. **Rationalized RESTful Resource Hierarchy in `server.py`**:
   - Consolidate 10 endpoints into a clean, intuitive REST resource API:
     - `GET  /api/status?project=<slug>` (Probes connection health across Sheets, Drive, Notebooks, and latest ingested snapshot).
     - `POST /api/sync?project=<slug>` (Synchronizes live Sheets registers and checks Drive for new weekly packs).
     - `POST /api/ingest?project=<slug>` (Ingests selected weekly report, triggers Gemini synthesis, and persists new snapshot).
     - `POST /api/briefing/generate?project=<slug>` (On-demand regeneration of executive decision text & multi-speaker podcast audio).
   - Provide transparent backwards-compatible routing aliases so existing frontend actions and legacy automated tests continue to operate smoothly.

3. **Frontend Simplified Sync Flow & Toast UX**:
   - Update Google Workspace sync modal in `index.html` and `src/js/app.js` to communicate with the streamlined REST endpoints.
   - Surface actionable toast notifications and error indicators (e.g., "Google Sheets synced 🟢", "Found 1 unindexed report ⚠️", "Ingestion complete 🎉").

4. **Turnkey Handover Documentation Polish**:
   - Update `docs/HANDOVER_GUIDE.md` to document the 1-click web UI workflow and simplified 1-command CLI operations.

## Acceptance Criteria
- [ ] `scripts/pipeline.py` provides unified execution for Sheets syncing, PDF ingestion, and AI briefing generation.
- [ ] `server.py` routes all operations through clean `/api/status`, `/api/sync`, `/api/ingest`, and `/api/briefing/generate` endpoints with backward compatibility.
- [ ] Flexible report parser successfully identifies week number and date from non-standard filenames (e.g. `Report.pdf`, `W29_Summary.pdf`).
- [ ] Full automated test suite (`pytest tests/`) passes 100%.
- [ ] `docs/HANDOVER_GUIDE.md` updated with foolproof, non-technical instructions.
