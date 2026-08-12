# Specification: Multimodal 2FA & Continuous Speaker Verification

## Dependencies
- **Depends on Track**: None. Integrates directly with the existing FastAPI WebSocket interface, Web Audio API frontend stream, and Gemini Live API backend.

## Functional Requirements

### 1. Phase 1: Multimodal 2FA Visual Code Capture (Strict Physical Flow)
- **Mock SMS Code Generation:** Upon initiating a sensitive EMR operation or entering the discharge portal, the system triggers a 2FA prompt. It generates a random 4-digit verification code (e.g., `4832`) and logs it securely to a "Mock SMS Dispatch Panel" on the developer dashboard/UI (simulating SMS delivery to the user's phone).
- **Webcam Camera Guide:** The app opens the camera stream and displays a clean visual guide: `"Hold your phone's screen showing the 2FA code up to the camera"`.
- **Vision Decoding via Gemini Live API:** The user holds up their physical phone (or a physical card/paper) displaying the 4-digit code. Gemini's visual system inspects the video frames, parses the digits, and matches them against the generated session code.
- **Verification Shutter:** Once verified, a success chime plays, and the UI displays a green badge `🔒 User Authenticated`.

### 2. Phase 2: Hybrid Unobtrusive Speaker Verification
- **Dual-Layer Speaker Analysis:**
  1. **Acoustic Model-Driven Check:** Update Gemini's system instructions to continuously monitor the speaker's acoustic profile (pitch, tone, cadence, age/gender profile). Gemini autonomously flags speaker mismatches in the conversation loop.
  2. **Parallel DSP Analyzer (Backend):** Implement a lightweight Digital Signal Processing (DSP) voice pitch tracker running on the FastAPI backend. It analyzes raw audio chunks streamed over the WebSocket, establishing an acoustic baseline for the authenticated user and flagging any sudden, sustained pitch/spectral envelope deviations.
- **Context-Aware Soft Guardrail:**
  - If an unannounced speaker change is detected (unauthorized voice), the assistant politely refuses to disclose sensitive medical, discharge, or booking details (e.g., *"I detected a different speaker. For patient privacy, please show your 2FA code to the camera again to verify your identity."*). It does not abruptly disconnect or lock the screen.
- **Conversational Speaker Handoff:**
  - If the primary user says: *"I'm passing the phone to my husband"* or *"Please let Dr. Watson join"*, Gemini detects this conversational intent, registers the handoff, and updates the speaker profile to trust the secondary speaker—bypassing the immediate 2FA trigger.

### 3. Phase 3: Conversational Advice Audit Log & Session-Bound PII Cleanup
- **Clinical Advice Provenance Audit Log:** Create a human-readable, compliant audit log file (`app/logs/audit/clinical_advice.log`). Every time the chatbot delivers advice or instructions (medication, discharge steps, nurse details), log:
  - Timestamp (ISO 8601) and Session ID.
  - Exact medical advice/guidelines text delivered.
  - The active user's security/authentication state at that moment (e.g., `2FA_VERIFIED`, `GUEST_AUTHORIZED`, `UNVERIFIED_PENDING`).
  - Safe for demo presentation at the end of the call flow.
- **Session-Bound PII Cleanup:**
  - All webcam frames (taken for 2FA visual matching) and raw incoming voice buffers are stored solely in a temporary session directory (`app/logs/sessions/{session_id}/`).
  - **Auto-Purge Handler:** When the session WebSocket disconnects, trigger a secure garbage collection routine to recursively delete all visual frames and raw audio from disk, leaving zero media footprint.
  - **Text PII Anonymization:** Redact basic client phone numbers and names from the long-term clinical audit log using regex pre-processing.
  - **Future SDP Integration Roadmap:** Design the logging interface to support Google Cloud Sensitive Data Protection (SDP) API integration in a subsequent phase for enterprise-grade DLP.

## Non-Functional Requirements
- **Low Latency:** The parallel DSP audio analysis must run with `<10ms` processing overhead per audio chunk to keep the real-time bidirectional stream lag-free.
- **Resilience:** Vision parsing must be resilient to screen glare, tilt, and moderate indoor lighting variations.

## Acceptance Criteria
- Triggering 2FA generates a random code and instructs the user to present it. Showing the correct physical code to the webcam successfully unlocks the session.
- If a secondary speaker speaks without prior authorization, the assistant refuses sensitive medical requests and prompts for re-authentication.
- If the authenticated user says *"Let my spouse join the conversation"*, the assistant permits the secondary speaker to talk without triggering security alerts.
- Delivering medical advice automatically logs the transaction in the clinical advice audit log, showing the advice text alongside the active authentication state.
- Disconnecting the call session securely purges all temporary 2FA webcam images and raw audio buffers from disk.

