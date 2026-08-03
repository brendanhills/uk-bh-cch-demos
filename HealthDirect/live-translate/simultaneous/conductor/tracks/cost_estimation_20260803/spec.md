# Specification: Cost-Estimation & Optimization Track (`cost_estimation_20260803`)

## Overview
This track aims to perform a comprehensive audit and analysis of Google Cloud & Gemini API usage in the simultaneous real-time medical interpreter application. It will catalog called APIs, model current unit pricing, analyze empirical costs on existing bilingual sample conversation runs, build a mathematical projection engine in Google Sheets format for ongoing multi-scale call volumes, and recommend concrete, actionable architectural cost optimizations.

---

## Functional Requirements

### 1. API Audit & Call Mapping
- Conduct a complete review of active and auxiliary modules in the repository.
- Map and catalog all API endpoints invoked, including:
  - **Gemini Live API (WebSockets):** Audio/Text inputs and outputs (including Gemini 3.1/3.5 models).
  - **Google Cloud Speech-to-Text (STT) V1 & V2 (Chirp-3):** Real-time/batch audio diarization and transcription.
  - **Google Cloud Text-to-Speech (TTS):** Synthetic dialogue audio library generation.
  - **Google Cloud Translation V2/V3:** Baseline/alternative translation calls.

### 2. Pricing Rate Sheet Definition
- Document and compile the standard, official unit pricing rates for each audited API:
  - Gemini API cost per 1M Input Tokens and 1M Output Tokens (split by Gemini 3.5 Flash, 3.1 Flash, and potentially Pro).
  - Google Cloud STT cost per minute (Chirp-3 vs. Standard models).
  - Google Cloud TTS cost per 1M characters (Wavenet/Neural voices vs. Standard).
  - Google Cloud Translation cost per 1M characters.

### 3. Empirical Cost Calculations for Sample Conversations
- Audit existing billing logs or estimate execution costs for our primary preset sample conversations:
  - German Fever Preset (`samples/de_fever_session.wav` / dialogue JSON).
  - Spanish Ear Preset (`samples/es_ear_session.wav` / dialogue JSON).
  - Arabic Asthma Preset (`samples/ar_asthma_session.wav` / dialogue JSON).
  - Vietnamese Paediatric Preset (`samples/paediatric_vietnamese_demo.wav` / dialogue JSON).
- Break down the cost calculation per-API and show the cumulative total cost for a full playthrough of each demo.

### 4. Google Sheets Volume Projection Calculator
- Design a complete Google Sheet structure consisting of:
  - **Tab 1: Rate Sheet** (Google Cloud & Gemini API current unit pricing).
  - **Tab 2: Sample Conversions** (Calculated cost per preset based on actual token/minute counts).
  - **Tab 3: Volume Projection Model** (Configurable cells for monthly calls, average duration, model mix, with auto-calculating totals).
- Write a ready-to-import CSV/TSV file (`utils/cost_calculator_sheet.csv`) containing this exact structure, preloaded with data, labels, and compatible formulas (e.g., `=SUM(...)`, `=AVERAGE(...)`) so it functions instantly upon import into Google Sheets.

### 5. Architectural Cost Optimization Recommendations
- Propose 3-5 concrete cost reduction techniques specifically tailored to this project's architecture, analyzing the trade-offs between cost and quality. Topics will include:
  - **Context Cache (Cached Tokens):** Reusing system instructions and clinical glossaries.
  - **Audio Sampling & Pacing Rates:** Lowering bitrates or optimizing payload sizes.
  - **Model Selection Strategy:** When to route to Gemini Flash vs. Gemini Flash-Lite.

---

## Acceptance Criteria
- [ ] A structured cost model document is generated in the repository (`conductor/tracks/cost_estimation_20260803/cost_analysis.md`).
- [ ] A ready-to-import Google Sheets calculator CSV file (`utils/cost_calculator_sheet.csv`) is created containing rate sheets, preset costs, and projection formulas.
- [ ] Optimization recommendations are fully documented in the analysis markdown.

---

## Out of Scope
- Integration of actual real-time billing API calls directly from GCP Billing (using static rate sheets instead).
- Automatic database schema changes for tracking costs per user session.
