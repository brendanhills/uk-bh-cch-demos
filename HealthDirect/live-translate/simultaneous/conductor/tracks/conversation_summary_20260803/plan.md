# Implementation Plan - Conversation Summary & PII Deletion (`conversation_summary_20260803`)

This plan details the technical steps to generate, display, and purge conversation summaries post-session.

## Phase 1: Backend Transcript Caching, Summary Generation, and Purging
- [x] Task: Implement In-Memory Transcript Collection & Gemini Summarization
    - [x] Update `ActiveSession` inside `demo/web_server.py` to compile and cache transcript turns in ephemeral memory as they happen.
    - [x] Implement `generate_and_send_summary` method in `ActiveSession` using `google-genai` SDK to call Gemini with the cached transcript text when the stream ends.
    - [x] Integrate automatic summary triggering on call completion inside `stop_stream_unsafe`.
- [x] Task: Implement Manual Purge and Auto-Purge Background Worker
    - [x] Implement `purge_session_data` method to wipe the in-memory transcript, summary, and temporary disk logs (`conversation_transcript.log`).
    - [x] Implement a lightweight background task to auto-purge session data after `session_purge_ttl_seconds` (default: 300) when the session finishes.
- [x] Task: Selective Regression Testing
    - [x] Implement a targeted regression test inside `tests/test_conversation_summary.py` to ensure that active stream setup, WebSocket register/disconnect, and audio chunks transmission remain unaffected by the summary generation and purge handlers.
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: WebSocket Protocol & Frontend UI Integration
- [x] Task: Implement WebSocket Actions & Nurse Portal UI
    - [x] Update `ws_nurse_endpoint` in `demo/web_server.py` to handle the `delete_summary` message action and trigger `purge_session_data`.
    - [x] Add a premium, modern conversation summary card/modal in `demo/web/nurse.html`.
    - [x] Implement JavaScript logic in `demo/web/simultaneous_client.js` to:
        - Listen for `summary_generated` and display the generated summary in the UI.
        - Render a polished loading spinner/state while the summary is being compiled.
        - Handle clicking the "Delete Summary & Transcript" button by sending a `delete_summary` action over the WebSocket and clearing local UI state.
        - Support smooth transitions and micro-animations for displaying and deleting the summary.
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)
