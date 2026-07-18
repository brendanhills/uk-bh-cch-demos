# Specification: Gemini 2.5 Unary/Streaming Integration & Evaluation (`gemini_25_integration_20260708`)

## Background
Gemini 2.5 Flash is highly optimized for audio-understanding, native translation, and speaker attribution. However, the Multimodal Live API (the bidirectional WebSockets protocol `bidiGenerateContent` on the `v1beta` API) does not currently support `gemini-2.5-flash`, throwing a policy violation error (1008). 

To utilize the capabilities of Gemini 2.5 Flash for transcription and translation, we need to design a secondary pipeline that operates over standard unary or HTTP-streaming content generation endpoints (`generate_content` / `generate_content_stream`).

## Goals
- Design a high-fidelity batch/file-processing mechanism for translating entire audio consultation files.
- Enable native speaker diarization and translation for audio up to 10MB (approx. 5 minutes) via inline base64 bytes, and larger files via the GCS / Files API.
- Create a front-end "Batch Audio Translation" interface in the browser Web UI to let users upload or select a pre-recorded audio file and watch the translated transcript render in real-time.

## Key Requirements
- **Backend Service**: An asynchronous FastAPI route (e.g. `/api/translate_file`) that receives a file or references a pre-recorded sample, invokes `client.models.generate_content_stream(model="gemini-2.5-flash", ...)` with customized medical system instructions, and returns a Server-Sent Events (SSE) stream.
- **Frontend Tab**: A new tab or view in the HTML/JS frontend named "File Translation Demo" or similar, utilizing standard fetch streaming to render the transcript turn-by-turn with animated typing effects.
- **Glossary Enforcement**: Explore how to apply medical terminology glossaries passively using specialized prompt engineering or structured JSON generation instructions under Gemini 2.5 Flash.
