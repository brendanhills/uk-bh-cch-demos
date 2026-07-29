# Specification: Browser-Side WebSocket Migration & Mic Streaming (Track: `browser_websocket_20260701`)

## Overview
This track migrates the Gemini Live Translate WebSocket connection directly to the client browser using client-side JavaScript. Instead of proxying audio and transcripts through a python web server, the web browser will connect directly to the Gemini Multimodal Live API over WebSockets. Additionally, this track introduces direct microphone streaming, allowing real-time, zero-latency, speaker-attributed medical translation directly from the user's microphone.

The Python web server (`web_server.py`) will be streamlined: it will no longer proxy the dual WebSocket connections or stream WAV file chunks, but will instead act as a static file server, a glossary data provider, and a secure Ephemeral Token dispenser to authenticate the frontend without exposing the root `GEMINI_API_KEY`.

## Functional Requirements
1. **Ephemeral Token Dispenser API**:
   - Add a POST `/api/token` endpoint to `web_server.py` that utilizes the Google GenAI SDK (`client.auth_tokens.create`) to generate short-lived, single-use client-side authentication tokens.
2. **Browser-Side Gemini WebSocket Client**:
   - Integrate a direct WebSocket client in `web/main.js` that connects directly to the public Gemini Multimodal Live API (`wss://generativelanguage.googleapis.com/...`).
   - Configure the WebSocket with custom clinical interpreter system instructions, Australian medical terminology rules, and preset-specific bilingual target languages.
3. **Live Microphone Audio Streaming**:
   - Implement real-time microphone capture in `web/main.js` using the Web Audio API and `navigator.mediaDevices.getUserMedia`.
   - Implement a PCM audio worker/processor (using modern AudioWorklet or standard processor) to capture and stream mic input down-sampled to 16kHz mono 16-bit PCM.
   - Stream the processed mic chunks directly to the browser-side Gemini Live connection.
4. **Bilingual Audio Playback**:
   - Play the translated audio stream (24kHz PCM from Gemini) returned directly to the browser, maintaining the immersive stereo panning and volume controls.
5. **FastAPI Backend Simplification**:
   - Clean up unused dual-session proxy code, file streaming, and manual chunking logic from `web_server.py`, keeping it focused on static files, glossary service, and token generation.

## Non-Functional Requirements
- **Low Latency**: Directly connecting the browser to Gemini reduces translation turnaround times and eliminates backend thread bottlenecks.
- **Security**: Root API Keys are never exposed to the client; all client connections are authenticated using short-lived (1 minute session / 30 minutes expiry) ephemeral tokens.
- **Microphone Permissions**: The app must handle microphone permission states gracefully, showing helpful states or instructions in the UI.

## Acceptance Criteria
- [ ] Backend server successfully generates short-lived ephemeral tokens via `/api/token`.
- [ ] Browser-side JavaScript successfully obtains token, establishes a direct secure WebSocket connection to Gemini Live, and configures the translation preset.
- [ ] User can stream their microphone input directly, and Gemini Live translates and transcribes it in real-time.
- [ ] The browser UI correctly highlights Australian medical glossary terms dynamically in real-time.
- [ ] Panning, mixing, and UI cards work beautifully with direct microphone streaming.
