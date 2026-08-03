# Implementation Plan: Cost-Estimation & Optimization (`cost_estimation_20260803`)

This plan outlines the sequential steps to perform the API audit, calculate empirical costs, build the Google Sheets projection template, and deliver actionable cost-reduction recommendations.

## Phase 1: API Audit & Unit Pricing Research
- [x] Task: Perform Codebase API Call Audit
    - [x] Search the repository (`live-translate/simultaneous/`) for all external Google Cloud client and endpoint invocations.
    - [x] Document all called API services (Gemini Live API, Cloud STT, Cloud TTS, Cloud Translation, etc.) and their specific models/voices in use.
- [x] Task: Compile Official Unit Pricing Rate Sheet
    - [x] Retrieve and verify current public pricing rates for each audited GCP service.
    - [x] Compile rates into a structured table (with units like per 1M characters, per audio minute, or per 1M tokens).
- [x] Task: Conductor - User Manual Verification 'Phase 1: API Audit & Unit Pricing Research' (Protocol in workflow.md)

## Phase 2: Dialogue Token Audit & Empirical Cost Calculations
- [~] Task: Audit Sample Conversations for Token & Duration Metrics
    - [~] Analyze the duration and transcript word/character counts of our existing sample presets (German, Spanish, Arabic, Vietnamese).
    - [~] Run test simulations or parse metadata to measure or calculate the precise input and output token counts when processed by the Gemini Live API.
- [ ] Task: Calculate Cumulative Preset Costs
    - [ ] Compute the exact cost for running each preset playthrough, showing the individual cost of STT, Gemini Live (input/output), and TTS.
    - [ ] Summarize these costs in a comparative table.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Dialogue Token Audit & Empirical Cost Calculations' (Protocol in workflow.md)

## Phase 3: Google Sheets Projection Calculator CSV Design
- [ ] Task: Design and Populate ready-to-import CSV Template
    - [ ] Create `utils/cost_calculator_sheet.csv` inside the repository.
    - [ ] Format Tab 1 (Rate Sheet) as CSV blocks.
    - [ ] Format Tab 2 (Sample Conversions) with formulas referencing the rate sheet blocks.
    - [ ] Format Tab 3 (Volume Projections) with custom input variables and SUM/PRODUCT formulas to automatically scale totals over weeks, months, and years.
- [ ] Task: Verify Google Sheet Compatibility
    - [ ] Manually verify that all written formulas are fully compatible with Google Sheets and parse correctly when uploaded.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Google Sheets Projection Calculator CSV Design' (Protocol in workflow.md)

## Phase 4: Cost Optimization Analysis & Recommendations Report
- [ ] Task: Document Findings and Recommendations
    - [ ] Create the central analysis report file: `conductor/tracks/cost_estimation_20260803/cost_analysis.md`.
    - [ ] Detail the API audit, rate sheets, empirical calculations, and long-term projections.
    - [ ] Formulate 3-5 high-impact, actionable cost optimization strategies with estimated savings (e.g., using Gemini Context Caching, bitrate reductions, etc.).
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Cost Optimization Analysis & Recommendations Report' (Protocol in workflow.md)
