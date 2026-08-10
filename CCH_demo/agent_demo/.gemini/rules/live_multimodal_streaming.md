# Live Multimodal Streaming & Grounding Best Practices

Guiding rules and architecture best practices for building Gemini Live API & ADK multimodal applications.

## 1. ADK Session Resumption & Sanitization
- Reusing static session IDs with `InMemorySessionService` restores prior session turn history and image blobs into Gemini Live API context.
- Always provide a `fresh=true` reset mechanism that calls `session_service.delete_session(...)` and sets `session_resumption=None` when starting new demo/practice runs.

## 2. Positive Grounding Over Negative Prompting
- Avoid negative prompt constraints (e.g. *"Do NOT say wound care"*). Negative constraints prime self-attention tokens and fail when audio turns arrive without visual data.
- Enforce strict positive affirmative grounding: *"Discuss ONLY facts explicitly provided in this conversation (printed on a visible document image, spoken by the user, or returned by a tool)."*
- Include explicit re-shot prompts when document images are missing, blurry, or unreadable (*"I can see you're holding up a document, but the text is a bit blurry. Could you please hold it closer and steady?"*).

## 3. ASR Language Anchoring & Multi-Lingual Speech Transcription
- Include all expected language codes (e.g., `language_codes=["en-AU", "ar"]`) in `AudioTranscriptionConfig` or avoid restrictive single-language hints so non-English user speech transcripts (such as Arabic) are not suppressed by the speech-to-text engine.
- Instruct the system prompt to remain in the default language for short, phonetically ambiguous utterances (such as *"No"*, *"No it's not"*, *"Yes"*, *"Thanks"*). Switch languages ONLY on explicit language requests or clear, unambiguous foreign-language sentences.

## 4. Webcam Streaming Sweet-Spot Resolution
- Stream webcam frames at **720p HD (1280x720)** resolution with **0.82 JPEG quality** (~50KB per frame payload).
- This provides the optimal balance of crisp document text legibility for OCR and ultra-fast, low-latency WebSocket streaming.

## 5. BIDI Live Stream Tool Selection & Turn Invariants
- **Avoid Heavy Tools in Live Audio**: In real-time Gemini Live API streaming sessions, avoid attaching web search tools (`google_search`) directly into active BIDI audio models unless explicitly required, as tool execution introduces 1-3 second turn delays.
- **Yield Turn Control on Questions**: For multi-step conversational taskflows, instruct the system prompt to stop speaking immediately and yield turn control whenever asking the user a question (identity, appointment preference, subsidies). Always wait for user input before proceeding to subsequent steps or tool calls.
- **Answer First, Do Not Mutate Code On Questions**: When in Planning Mode or when the user asks an investigatory question (e.g., *"are there any bugs we should fix?"*), provide the analysis and update planning artifacts first. Never modify codebase files unless the user explicitly requests execution.
- **Inspect DOM Before UI Planning**: Always inspect the exact HTML structure (`index.html`) using `view_file` to verify container locations and class names before formulating UI plans.
