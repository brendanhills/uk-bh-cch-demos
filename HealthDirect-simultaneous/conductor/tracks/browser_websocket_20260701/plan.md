# Implementation Plan - Browser-Side WebSocket Migration & Mic Streaming (Track: `browser_websocket_20260701`)

This plan details the steps to migrate the Gemini Live Translate WebSocket connection directly to the browser and implement real-time microphone streaming.

## Phase 1: Backend Security & Token Ingestion
- [ ] Task: Implement Ephemeral Token Generator Endpoint in `web_server.py`
    - [ ] Create `/api/token` POST endpoint.
    - [ ] Initialize `genai.Client` with the local API key configured for the v1alpha API version.
    - [ ] Create a short-lived ephemeral token via `client.auth_tokens.create`.
    - [ ] Add robust error handling if the API key is not present or token creation fails.
- [ ] Task: Write unit tests for Token API endpoint
    - [ ] Create `tests/test_token_api.py`.
    - [ ] Mock the GenAI client's auth_tokens service.
    - [ ] Verify that a POST to `/api/token` returns a 200 OK and a valid token structure.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Backend Security & Token Ingestion' (Protocol in workflow.md)

## Phase 2: Frontend Direct WebSocket & Mic Streaming Integration
- [ ] Task: Integrate `GeminiLiveAPI` and Mic Capture Utilities in the Browser
    - [ ] Adapt `geminilive.js` capabilities into the main frontend architecture.
    - [ ] Create helper methods in `web/main.js` to request microphone access and initialize Web Audio API.
    - [ ] Implement a lightweight PCM down-sampling utility to convert the raw browser microphone inputs to 16kHz mono 16-bit PCM.
- [ ] Task: Connect Frontend Directly to Gemini Live API
    - [ ] Update `connectCall()` in `web/main.js` to first fetch the ephemeral token from `/api/token`.
    - [ ] Initialize the direct Gemini Live API connection over WebSocket using the token.
    - [ ] Fetch the current glossary from `/api/glossary` and format it as clinical rules.
    - [ ] Send the Initial Setup message containing system instructions, persona, and glossary rules to Gemini Live.
    - [ ] Bind real-time microphone stream chunks to send to Gemini.
    - [ ] Handle incoming audio and text transcripts directly in JavaScript.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Frontend Direct WebSocket & Mic Streaming Integration' (Protocol in workflow.md)

## Phase 3: Backend Streamline & Final Integration
- [ ] Task: Streamline `web_server.py`
    - [ ] Remove unused dual-session parallel WebSocket proxy logic and file chunking helper methods.
    - [ ] Maintain FastAPI static file serving and the `/api/glossary` endpoint.
- [ ] Task: End-to-End Verification and Glossary Alignment
    - [ ] Verify that real-time transcription and translated audio playback function flawlessly.
    - [ ] Confirm Australian Clinical Glossary terms are highlighted perfectly in real-time in the UI.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Backend Streamline & Final Integration' (Protocol in workflow.md)
