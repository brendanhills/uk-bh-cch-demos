# Plan: Multi-Client Split-View Conversation Simulator (`multi_client_simulator`)

## Phase 1: Session Coordinator & Dual-Route Backend Setup
- [ ] Task: Implement FastAPI endpoints and shared backend session state
    - [ ] Create HTTP routes `/nurse` and `/patient` in `web_server.py` to serve separate frontends
    - [ ] Add separate `/ws/nurse` and `/ws/patient` WebSocket endpoints
    - [ ] Create a thread-safe `ActiveSession` state coordinator to pair connected clients, synchronize preset/model/language configurations, and handle disconnects gracefully
- [ ] Task: Create unit tests for session pairing and state synchronization
- [ ] Task: Implement session pairing and configuration synchronization to pass tests
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Session Coordinator & Dual-Route Backend Setup' (Protocol in workflow.md)

## Phase 2: Synchronized Dual-Channel Audio Streaming & Routing
- [ ] Task: Refactor the WebSocket audio streaming loop for dual-client routing
    - [ ] Modify the `send_audio` background task to support streaming to two distinct WebSockets
    - [ ] Load the pre-recorded stereo WAV file, split into Nurse and Patient mono arrays, and stream them in perfect lockstep
    - [ ] Broadcast active speaker state, turn pauses, and pacing hold states to both WebSockets to keep UI timers and indicators fully aligned
- [ ] Task: Create unit tests for synchronized dual-channel audio streaming and pacing propagation
- [ ] Task: Implement dual-channel streaming and propagation logic to pass tests
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Synchronized Dual-Channel Audio Streaming & Routing' (Protocol in workflow.md)

## Phase 3: Separate Frontend Interfaces (Nurse vs. Patient)
- [ ] Task: Create the Master Nurse Control Panel UI (`nurse.html` / `/nurse`)
    - [ ] Build a premium visual workspace with master dropdowns (Scenario, Model, Language) and call action controls
    - [ ] Render the dual-column live transcript, speaker glowing borders, search glossaries, and references panel
- [ ] Task: Create the Simplified Patient UI (`patient.html` / `/patient`)
    - [ ] Build a clean, accessible caller view with synchronization indicators (e.g., "Waiting for clinician...")
    - [ ] Implement auto-language sync driven by the Nurse controller and render translated nurse dialogues in high-contrast large fonts
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Separate Frontend Interfaces (Nurse vs. Patient)' (Protocol in workflow.md)

## Phase 4: Integration Testing & Verification
- [ ] Task: End-to-end local test and verification
    - [ ] Start the FastAPI server locally, open `/nurse` and `/patient` in separate windows
    - [ ] Verify that selecting a language on the Nurse view automatically updates the Patient view state
    - [ ] Start the session, verify synchronized audio and translation delivery, and confirm no regressions in existing python tests
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Integration Testing & Verification' (Protocol in workflow.md)
