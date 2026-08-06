# Specification: Conversation Summary & PII Deletion (`conversation_summary_20260803`)

## Overview
During live translation sessions, a patient-nurse interaction occurs. When the call completes, a clinical summary of the conversation must be generated and presented to the nurse within 60 seconds (target: sub-10 seconds). Furthermore, to comply with privacy/PII standards, the nurse must have the ability to delete this summary and transcript immediately. Additionally, to ensure no PII is accidentally stored long-term, the server must automatically purge all session-related PII (transcripts, summaries, etc.) after a configurable idle duration (default: 5 minutes) from call completion.

## Functional Requirements
1. **In-Memory Transcript Caching (Cost Optimization)**:
   - **No Audio Re-Processing**: Do NOT send the raw audio stream or re-transcribe the call for summary generation.
   - Use the side-by-side text transcript already compiled and cached in ephemeral server memory during the live call as the context for the summary prompt.
2. **Automated Summary Trigger**:
   - Immediately when the call finishes (i.e., session disconnect, stop stream, or hang up), the server must compile the cached conversation transcript.
   - The server must trigger an asynchronous, fast summary request using Gemini API (e.g., Gemini 3.5 Flash) with the cached text transcript as input.
   - The summary should be formatted based on a clinical template:
     - **Chief Complaint / Reason for Call**
     - **Symptom History / Timeline**
     - **Key Clinical Details & Discussion**
     - **Action Plan / Next Steps**
3. **Low-Latency Delivery (<60s limit, <10s target)**:
   - The summary generation and delivery to the client must complete in under 10 seconds.
   - Use async server tasks to avoid blocking the main server thread during generation.
4. **Nurse Portal Integration (`nurse.html`)**:
   - Present the summary inside a modern, dedicated modal or expandable card panel in `nurse.html`.
   - The interface must display a clear, styled loading/generation spinner or progress indicator while the summary is being compiled.
5. **PII Deletion & Purging Mechanism**:
   - Provide a prominent "Delete Summary & Transcript" button on the Nurse UI.
   - Clicking this button must:
     - Clear the summary and transcript from the client-side UI and local/session storage.
     - Send a request to the server to completely purge the conversation transcript, audio logs, and generated summary from server-side memory/cache and any session-specific storage.
     - Confirm to the nurse via a subtle, smooth notification that all PII and conversation data have been permanently purged.
6. **Configurable Auto-Purge Backup Task**:
   - Implement an automated background task on the server to prune session data.
   - If a session remains completed and untouched for longer than a configurable TTL (Time-To-Live, defaulting to 300 seconds / 5 minutes), the server must automatically trigger the purge workflow for that session's transcript, audio buffers, and summary.
   - The TTL should be configurable inside the central configuration file (`demo/interpreter_config.json`) via `"session_purge_ttl_seconds"`.

## Non-Functional Requirements
- **Privacy First (No Persistence)**: Do not store any transcripts or summaries to any persistent databases or disk logs. All session transcript/summary data must reside only in ephemeral server memory and be easily purgeable.
- **Fast Performance**: Sub-10 seconds from call end to summary display.

## Acceptance Criteria
- [ ] Server detects call completion (session disconnect) and starts generating the summary.
- [ ] Summary is generated using Gemini API with a structured clinical template.
- [ ] Summary is pushed to the client and displayed in the Nurse Portal UI (`nurse.html`).
- [ ] The nurse view features a polished loading state while waiting for the summary.
- [ ] A prominent "Delete Summary & Transcript" button is visible to the nurse.
- [ ] Clicking the delete button immediately wipes the UI data, clears client storage, and sends a purge request to the server.
- [ ] Server handles the purge request by completely deleting any in-memory transcript, audio buffers, and generated summary for that session.
- [ ] A background task automatically purges finished session data after the configured TTL (e.g. 5 minutes) if the nurse hasn't already manually deleted it.
- [ ] The TTL can be configured inside `interpreter_config.json`.
- [ ] All tests for the summary generation, deletion, and auto-purge flows pass successfully.

## Out of Scope
- Integration with external Electronic Health Record (EHR) databases or permanent medical storage.
- Auto-saving summaries to a cloud bucket (this track enforces ephemeral memory and deletion capabilities).
