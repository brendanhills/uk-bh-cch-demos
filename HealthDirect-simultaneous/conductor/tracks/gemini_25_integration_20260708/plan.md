# Implementation Plan: Gemini 2.5 Unary/Streaming Integration (`gemini_25_integration_20260708`)

This plan details the future investigation steps to integrate standard Gemini 2.5 Flash into our bilingual medical translation pipeline as a file/batch-processing feature.

---

## Phase 1: Research & Prototyping Unary Translation Pipeline
- [ ] Task: Re-establish the basic unary generation prototype to process WAV files from the `samples/` directory using Gemini 2.5.
- [ ] Task: Evaluate performance (accuracy, latency, speaker attribution) compared to the real-time Live WebSocket API (Gemini 3.5 / 3.1).
- [ ] Task: Benchmark passive clinical glossary enforcement via system instructions and custom structured prompting.

## Phase 2: Backend Streaming API & Endpoint
- [ ] Task: Implement an SSE (Server-Sent Events) endpoint `/api/translate_file` in `demo/web_server.py`.
- [ ] Task: The endpoint should stream out line-by-line speaker attributions (CLINICIAN vs PATIENT) as they are produced by the Gemini 2.5 Flash stream.
- [ ] Task: Add test coverage in the test suite to ensure the batch API endpoint works correctly.

## Phase 3: Frontend "File Translation Demo" UI
- [ ] Task: Create a new tab or view in `demo/web/index.html` allowing the user to select an existing sample file (German, Spanish, Arabic, etc.) or upload their own WAV file.
- [ ] Task: Build JavaScript UI logic in `demo/web/main.js` to trigger the streaming fetch, parse incoming SSE data, and render the speaker-attributed transcript line-by-line.
- [ ] Task: Polish interactions using premium CSS styles, smooth transitions, and distinct speaker turn-taking indicators.
