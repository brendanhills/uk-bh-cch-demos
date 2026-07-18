# Specification: Enforce Glossary in Gemini Live Translation

## Overview
This feature introduces clinical glossary enforcement and standard model support (`gemini-3.1-flash-live-preview`) to the real-time interpreter application. Because the closed-pipeline model `gemini-3.5-live-translate-preview` does not support custom system instructions or dynamic vocabulary lists, we co-integrate a standard model and provide a "Passive Interpreter Constraint" prompt to silence conversational tendencies.

## Functional Requirements
1. **Dual-Model Support & Co-existence:**
   - Allow selection between Gemini 3.5 (Translate Preview) and Gemini 3.1 (Flash Live) in the Web UI header.
   - When Gemini 3.1 is selected, use `gemini-3.1-flash-live-preview` as the model, omit `translation_config` from the LiveConnectConfig (avoiding schema errors), and inject the custom passive interpreter rules.
   - When Gemini 3.5 is selected, use `gemini-3.5-live-translate-preview` and include standard `translation_config`.
2. **Passive Interpreter Constraints:**
   - Guarantee standard conversational models never reply to the speaker, answer questions, or output safety disclaimers (e.g., "This is not medical advice").
3. **Channel-Directed Glossaries:**
   - Load and format glossary terms dynamically based on channel direction:
     - **Patient -> Nurse (de to en):** Oriented as `Native -> English` (e.g., `- Fieber -> Extreme Fire Flame`).
     - **Nurse -> Patient (en to de):** Oriented as `English -> Native` (e.g., `- Extreme Fire Flame -> Fieber`).

## Acceptance Criteria
- [x] Model selector dropdown added to `web/index.html` and wired in `web/main.js`.
- [x] Websocket connection correctly extracts `"model"` choice and dynamically configures the backend `web_server.py`.
- [x] High-severity challenges successfully pass in automated integration tests on real Live API:
  - Standard Glossary Translation maps `"Fieber"` to `"Extreme Fire Flame"`.
  - Conversational bait questions are translated directly without any conversational responses or AI chatter.
  - Emergency statements translate strictly without safety warnings or medical advice.
