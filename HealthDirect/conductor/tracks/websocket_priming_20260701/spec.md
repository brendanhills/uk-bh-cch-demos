# Specification: Australian Medical Glossary WebSocket Priming & System Instructions (Track: `websocket_priming_20260701`)

## Overview
This track introduces dynamic session priming and custom system instructions for Gemini Live Translate sessions within the Bilingual Medical Interpreter's web server (`web_server.py`). By dynamically loading the Australian clinical glossary terms from `dictionary/glossary.json` and injecting them alongside a highly-structured clinical persona prompt as the session's `system_instruction` in the `LiveConnectConfig`, we ensure that the Gemini Live Translate model:
1. Translates conversational audio accurately with precise clinical vocabulary alignment.
2. Adheres to Australian medical terminology standards and spelling conventions (e.g., "Emergency Department" instead of "ER", "paracetamol" instead of "acetaminophen").
3. Maintains a high-fidelity translation flow optimized for the dual-channel patient-nurse scenario in the Web interface.

## Functional Requirements
1. **Dynamic Glossary Loading & Formatter**:
   - Create a helper module/function inside `web_server.py` (or as a separate utility) to dynamically read the active glossary terms from `dictionary/glossary.json`.
   - Format the glossary terms cleanly (e.g., as key-value pairs of English to target language, or standard JSON representation) to be easily embedded in the prompt context.
2. **System Instruction Prompt Engineering**:
   - Design a highly-structured clinical interpreter system prompt that defines the model's persona, bilingual context (English <-> Target Language), and translation rules.
   - Explicitly instruct the model to strictly prefer Australian medical spelling and nomenclature, using the provided glossary mapping.
   - Instruct the model on how to handle turn-taking, medical terminology, and clinical jargon.
3. **Web Server Connection Integration (`web_server.py`)**:
   - Dynamically load the correct glossary based on the selected language preset.
   - Assemble the complete `system_instruction` parameter combining the clinical persona prompt, Australian terminology rules, and the relevant glossary terms.
   - Inject these system instructions into the WebSocket connection setup for client sessions during initialization (`LiveConnectConfig`).
4. **Robust Error Handling**:
   - Provide fallback system instructions if the glossary file is missing or corrupted, ensuring the service remains fully functional.

## Non-Functional Requirements
- **Context Efficiency**: Keep the system instructions and formatted glossary concise and optimized to avoid excessive context-token usage and minimize API latency.
- **Robustness**: Any glossary loading failures must not prevent the WebSocket connection from opening.

## Acceptance Criteria
- [ ] `web_server.py` successfully loads and embeds the Australian Medical Glossary into the WebSocket `system_instruction` configuration.
- [ ] Gemini Live Translate correctly adheres to the system instruction guidelines during sessions.
- [ ] Translation outputs in the Web UI prefer Australian medical terms (e.g., "paracetamol", "Emergency Department") when matching concepts are mentioned.
- [ ] No session setup or connection failures occur due to glossary size or bad formatting.
- [ ] Automated tests verify prompt assembly and glossary loading safety.
