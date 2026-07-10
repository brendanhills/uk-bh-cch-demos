# Specification - Live Real-Time Translation (Gemini Live API)

## Overview
This track introduces real-time bilingual translation utilizing **Gemini Live API's Live Translate** (`https://ai.google.dev/gemini-api/docs/live-api/live-translate`). A citizen calls a health helpline to consult an English-speaking HealthDirect nurse.

To ensure fast development cycles and follow a **Simple First, Elaborate Later** strategy:
1. **Direct WebSocket Stream:** Stream 16kHz Mono 16-bit PCM audio chunks in real-time directly to Gemini Live API using the async `client.aio.live.connect()` client from the `google-genai` Python SDK.
2. **Side-by-Side Dual-Column UI:** Output a double-column console layout mapping original speech and translated turns in real-time.
3. **Australian Medical Glossary Priming:** Dynamically inject custom HealthDirect medical glossaries (`dictionary/glossary.json`) into system instructions to prime the Gemini Live Translate session.

## Scope & Objectives
1. **Gemini Live Translate Integration:**
   - Establish direct async WebSocket connection to `gemini-3.1-flash-live-preview`.
   - Feed realtime audio bytes and receive bidirectional translations under the same session.
2. **Medical Terminology Precision & Localization:**
   - Dynamically load terms from `dictionary/glossary.json`.
   - Instruct Gemini to act as an objective, professional on-call medical interpreter conforming strictly to Australian health standards (e.g., mapping "acetaminophen" or "tylenol" to "paracetamol", using Australian spellings like "paediatrician" and "diarrhoea", and emergency number "Triple Zero").
3. **Aligned Bilingual Terminal UI:**
   - Dual-column console rendering:
     - **Left Column:** English Nurse dialogues and English-translated patient turns.
     - **Right Column:** Foreign Patient dialogues (e.g., German) and foreign-translated nurse turns.

## Verification Criteria
- Clean execution of standalone script `live_translate_demo.py`.
- Successful direct WebSocket handshakes and data streaming with Gemini Live API.
- Verified side-by-side terminal rendering of conversation turns.
- Demonstrated translation accuracy respecting Australian medical terms and loaded glossaries.
