# Implementation Plan: Multimodal 2FA & Continuous Speaker Verification

## Phase 1: Multimodal 2FA Visual Code Capture Infrastructure
- [ ] Task: Write failing unit tests for 2FA code generation, session state storage, and vision verification logic in `tests/test_auth_2fa.py` (TDD Red Phase)
- [ ] Task: Implement backend 2FA code generator and ADK state storage in `app/cch_agent/` or `app/auth.py` to support generated session-specific 4-digit codes
- [ ] Task: Create "Mock SMS Dispatch Panel" on the web developer UI to securely expose the generated 2FA code for easy demoing/testing
- [ ] Task: Add Gemini Live API prompt instructions/guidelines for vision frame analysis to detect the 4-digit digits from the video feed
- [ ] Task: Implement the frontend UI camera prompt and status badges (`🔒 User Authenticated` and `🔓 Re-authentication Required`)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Hybrid Unobtrusive Speaker Verification & Conversational Handoff
- [ ] Task: Write failing unit tests for the parallel DSP pitch analyzer and conversational handoff context parsing in `tests/test_speaker_verification.py` (TDD Red Phase)
- [ ] Task: Build parallel backend DSP voice analysis task in FastAPI WebSocket stream (extracting voice pitch/energy and setting baseline)
- [ ] Task: Update Gemini Live API agent system instructions to monitor speaker profiles and handle explicit speaker handoff commands (e.g., *"I'm passing the phone to my husband"*)
- [ ] Task: Implement the soft guardrail refusal logic (polite refusal to share sensitive discharge details upon unannounced speaker change, asking for 2FA check)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Conversational Advice Audit Log & Session PII Auto-Cleanup
- [ ] Task: Create structured audit logging module in `app/audit.py` to record clinical advice transactions to `app/logs/audit/clinical_advice.log`
- [ ] Task: Integrate clinical advice logging into the chatbot's response/speech synthesis generation handlers (storing timestamp, text, and active 2FA state)
- [ ] Task: Build session-bound media directory handlers to direct incoming webcam frames and audio files into `app/logs/sessions/{session_id}/`
- [ ] Task: Implement WebSocket disconnect auto-purge routine in `app/main.py` that recursively and securely wipes the temporary session media directory
- [ ] Task: Implement regex-based text anonymizer in `app/audit.py` to redact client phone numbers/names, with a dedicated interface for future Google SDP integration
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Integration, Regression, & End-to-End Verification
- [ ] Task: Run automated regression and code coverage suite (`pytest --cov=app`)
- [ ] Task: Execute end-to-end manual verification plan across 2FA enrollment, continuous speech verification, spouse/doctor handoff, advice audit logs, and post-session PII deletion
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

