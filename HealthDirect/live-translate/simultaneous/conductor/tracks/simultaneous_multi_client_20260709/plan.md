# Plan: Simultaneous Multi-Client Split-View Conversation Simulator (`simultaneous_multi_client`)

## 🛑 Execution Guardrails
* **Headless-First Verification**: Never load a browser window to debug WebSocket routing. Verify session coordination, room pairing, and message routing using `fastapi.testclient` and mock connections first.
* **Web Audio Autoplay Bypass**: Implement a simple, high-visibility "Initialize Audio" button to guarantee user-interaction-based `AudioContext` activation. Do not write complex self-retrying state loops to bypass browser autoplay blocks.
* **No-Drift Threshold**: Define "acceptable lockstep sync" as ±250ms. If the two clients play within 250ms of each other, do not implement additional dynamic NTP clock syncing.
* **Single-Pair Simplification**: The session coordinator should manage a single, static dual-client pair (one Nurse, one Patient) for demo purposes. Do not implement complex multi-room multi-tenant scaling architectures. Keep it simple and focused.

## Phase 1: Git Sandboxing & Backend Endpoints Setup
- [x] **Task 1.1**: Set up dedicated Git branch for safety
  *   Run `git checkout -b feature/simultaneous-multi-client` from `stable-pre-modularization` and push to remote.
- [x] **Task 1.2**: Implement HTTP routes in `web_server.py`
  *   Create `/nurse` and `/patient` endpoints serving HTML files.
- [x] **Task 1.3**: Implement `/ws/nurse` and `/ws/patient` endpoints
  *   Create independent WebSocket routes.
- [x] **Task 1.4**: Build thread-safe `ActiveSession` coordinator class
  *   Manage paired connection sockets, broadcast configuration updates (preset, model, language) from `/nurse` to `/patient`, and handle disconnects.
  *   *Anti-Loop Guard*: The session coordinator should manage a single, static dual-client pair (one Nurse, one Patient) for demo purposes. Do not implement complex multi-room multi-tenant scaling architectures. Keep it simple and focused.
- [x] **Task 1.5**: Write unit tests for session pairing and state synchronization

## Phase 2: Simultaneous Continuous Streaming Router
- [x] **Task 2.1**: Refactor `send_audio` for continuous lockstep streaming
  *   Remove all physical pausing, holding, and silence-injection loops.
  *   Load the pre-recorded stereo WAV file and split into Left (Patient) and Right (Nurse) mono bytearrays.
  *   Implement a real-time, real-rate throttling loop that streams 200ms Left chunks to `/ws/patient` and Right chunks to `/ws/nurse` continuously at 100% speed.
- [x] **Task 2.2**: Broadcast active speaker timers
  *   Push elapsed playhead timestamps and active-speaker state events to both WebSockets to keep UI timers fully aligned.
- [x] **Task 2.3**: Create and run unit tests for continuous simultaneous audio streaming

## Phase 3: Premium Nurse Interface (`/nurse`) with Independent Audio Panning Slider
- [x] **Task 3.1**: Create `nurse.html` template under `demo/web/`
  *   Build a visual workspace with master dropdowns (Scenario, Model, Language) and call action controls.
  *   Render the dual-column live transcript, speaker glowing borders, search glossaries, and references panel.
- [x] **Task 3.2**: Implement Client-Side Web Audio Graph with StereoPannerNode on `/nurse`
  *   Instantiate `AudioContext`.
  *   Route incoming original WAV stream chunks to `originalPanner` (panned Left).
  *   Route incoming Gemini translated audio bytes to `translationPanner` (panned Right).
  *   *Anti-Loop Guard*: Implement standard, direct gain manipulation. Do not build custom audio fading curves or exponential volume decay algorithms.
- [x] **Task 3.3**: Build the independent Nurse-side Bilingual Audio Panning Slider
  *   Create a slider in the `/nurse` UI to dynamically adjust the gain/panning of the original and translated audio nodes.
  *   Verify: Slider is localized to `/nurse` and does not affect `/patient`. Slider at `-1.0` plays only original; at `+1.0` plays only translation; at `0.0` plays both blended 50/50.

## Phase 4: Simplified Patient Interface (`/patient`) with Independent Audio Panning Slider
- [x] **Task 4.1**: Create `patient.html` template under `demo/web/`
  *   Build a clean, accessible caller view with synchronization indicators (e.g., "Waiting for clinician...").
  *   Implement auto-language sync driven by the Nurse controller and render translated nurse dialogues in high-contrast large fonts.
- [x] **Task 4.2**: Implement Client-Side Web Audio Graph with StereoPannerNode on `/patient`
  *   Mirror the Web Audio graph on the Patient-side to allow independent panning controls for the caller.
- [x] **Task 4.3**: Build the independent Patient-side Bilingual Audio Panning Slider
  *   Create a localized slider in the `/patient` UI to adjust the caller's panning independently of the clinician's settings.
  *   Verify: The Patient can isolate the original German speaker or the translated Nurse voice according to their own preferences.
- [x] **Task 4.4**: Implement "Demo Focus" Audio Mute Toggles (Single-Machine Google Meet Sharing)
  *   Add a prominent "Mute Tab Audio" button on both `/nurse` and `/patient` HTML views.
  *   When clicked, instantly mute or attenuate (gain = 0.05) all audio nodes for that specific browser tab.
  *   *Why*: When demoing side-by-side on a single machine over Google Meet, this lets the presenter mute the Patient's audio output when demonstrating the Nurse's ear, and vice-versa, avoiding double-vocal clashing on the screen share!

## Phase 5: Verification, Integration & Automated Unit Testing
- [x] **Task 5.1**: Develop Headless, Command-Line Backend Unit Tests (Fast & Browserless)
  *   Write python unit tests using `pytest` and `fastapi.testclient.TestClient` to verify session coordinator pairing, continuous streaming routing, and configuration sync without spawning a browser.
  *   *Why*: Browser-based testing is slow and heavy. These headless socket tests run in **milliseconds**, providing instant, reliable validation of core logic.
- [x] **Task 5.2**: Run local dual-browser side-by-side manual validation
  *   Start the FastAPI server locally, open `/nurse` and `/patient` in separate windows.
  *   Verify that selecting a language on the Nurse view automatically updates the Patient view.
  *   Start the session, verify continuous dual-channel streaming, simultaneous translation, and independent slider panning on both sides.
  *   Test the "Demo Focus" mute buttons to ensure smooth audio switching during screen sharing.
  *   *Anti-Loop Guard*: If you encounter audio clicking/popping over WebSockets, apply a static, simple 50ms buffer delay. Do not rewrite the browser's audio decoding engine. If it works smoothly in Chrome, do not attempt to refactor the entire pipeline to resolve edge cases in old Safari or Firefox builds unless explicitly required.
- [x] **Task 5.3**: Backward compatibility validation
  *   Verify that the test suite runs and all existing tests pass on the feature branch.
- [x] **Task 5.4**: Create and run Headless WebSocket Session Sync test (`tests/test_multi_client_sync.py`)
  *   Verify paired connection sockets, broadcast configuration updates from `/nurse` to `/patient`, and handle client disconnects.
- [x] **Task 5.5**: Create and run Lockstep Paced Streaming Throttling test (`tests/test_streaming_throttling.py`)
  *   Verify that the server-side real-time streaming loop delivers chunks at a precise, non-blocking rate of 200ms per chunk (5 chunks per second).
- [x] **Task 5.6**: Create and run Offline Gap & Starvation Detector test (`tests/test_offline_gap_check.py`)
  *   Verify that no single chunk interval exceeds 250ms under load, catching any blocking synchronous thread execution immediately.
