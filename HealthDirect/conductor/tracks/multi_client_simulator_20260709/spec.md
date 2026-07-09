# Specification: Multi-Client Split-View Conversation Simulator (`multi_client_simulator`)

## 1. Overview
Redesign the simulation architecture to separate the Nurse (Clinician) and Patient (Caller) interfaces into distinct browser windows. Instead of a single screen showing both participants side-by-side, the system will serve separate routes: `/nurse` (for the clinician) and `/patient` (for the caller) over a single port.
The Nurse view acts as the **Master Controller** to select the scenario, model, and language, which are automatically synchronized to the Patient's view. When the Nurse starts the call, the backend streams the audio channels in lockstep over separate WebSockets, maintaining perfect turn-taking pacing and timing across both clients.

---

## 2. Functional Requirements

### 2.1 Backend Routing & Coordination
- **Unified Port & Routes**: Serve two separate web endpoints:
  - `/nurse`: Serves the Clinician interface.
  - `/patient`: Serves the Patient interface.
- **Session Coordinator (Master Control)**:
  - Maintain a shared session state (`active_session`) on the FastAPI backend.
  - When the Nurse selects a scenario or model on `/nurse`, the backend pushes the configuration to the connected Patient on `/patient` to ensure both clients are matched.
- **Simultaneous Playhead Stream**:
  - Clicking "Start" on `/nurse` triggers the backend to load the stereo audio file.
  - Chunks are read and streamed to the Nurse (Channel 1) and Patient (Channel 2) WebSockets simultaneously, ensuring that playhead timing is perfectly synchronized.
- **Turn-taking Event Propagation**:
  - Broadcast turn-taking state events (e.g., `stream_paused`, `turn_complete`) to both WebSockets to keep UI indicators (active speaker glows, timers) completely aligned.

### 2.2 Nurse View (`/nurse`)
- **Master Controls**: Access to dropdown selectors for "Scenario", "Model", and "Patient Language".
- **Visuals (Audio-Only for now)**: Premium clinician workspace with avatars representing the Patient Caller and Nurse Sarah.
- **Call Controls**: Start Call, End Call, and Turn Pacing parameters.
- **Transcript Console**: Live scrolling transcript showing both English and Patient translations with clinical glossary highlights.
- **Side Panels**: Active Clinical Glossary Search and Encountered Medical References panel.

### 2.3 Patient View (`/patient`)
- **Simplified Interface**: Extremely clean and accessible layout following the HealthDirect brand theme.
- **Sync Status**: Displays "Waiting for Clinician to start..." until the Nurse initiates the call.
- **Automatic Language Sync**: Automatically detects and displays the language selected by the Nurse, with an optional dropdown to override if needed.
- **Incoming Transcript**: Display only the translated dialogue from the Nurse in their selected language in large, highly readable fonts, and a preview of their own transcribed words.

---

## 3. Non-Functional Requirements
- **WebSocket Performance**: Low-latency WebSocket synchronization to keep both views perfectly aligned with the audio playhead.
- **Responsive Layout**: Designed to look professional in different window widths (allowing side-by-side browser window placement on a single monitor).
- **Test Integrity**: Ensure backward compatibility so that existing python tests can run without regressions.

---

## 4. Acceptance Criteria
- [ ] Navigating to `/nurse` and `/patient` in separate windows loads their respective interfaces.
- [ ] The Patient view automatically synchronizes with the active scenario and language selected on the Nurse view.
- [ ] Initiating the call on the Nurse view triggers synchronized dual-channel audio streaming and bidirectional translations.
- [ ] Active speaker indicators and transcripts are updated in lockstep across both views.
- [ ] No regressions in core transcription, translation, and pacing algorithms.
