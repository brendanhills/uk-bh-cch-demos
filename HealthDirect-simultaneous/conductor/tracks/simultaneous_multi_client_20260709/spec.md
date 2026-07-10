# Specification: Simultaneous Multi-Client Split-View Conversation Simulator (`simultaneous_multi_client`)

## 1. Overview
Redesign the simulation architecture of the Bilingual Medical Interpreter to separate the Nurse (Clinician) and Patient (Caller) interfaces into distinct browser windows (`/nurse` and `/patient`) over a **Simultaneous Continuous Streaming Router** model.

Rather than managing complex, fragile server-side turn-holding pacing loops, the backend will act as a stateless, high-speed routing proxy, streaming the Left (Patient) and Right (Nurse) audio channels of a pre-recorded stereo WAV file continuously in lockstep over separate WebSockets (`/ws/patient` and `/ws/nurse`).

On the client frontends, the browsers will play back Gemini's simultaneous translations immediately on-the-fly, and implement a **Client-Side Audio Panning Slider** (powered by the HTML5 Web Audio API `StereoPannerNode`). This slider allows a user to dynamically isolate or blend the original and translated voices for customer demonstrations.

---

## 2. Technical & Functional Requirements

### 2.1 Backend Router Routing & Session Coordinator
- **Unified Port & Routes**: Serve two separate web endpoints over a single port:
  - `/nurse`: Serves the Clinician interface template.
  - `/patient`: Serves the Patient interface template.
- **WebSocket Endpoints**:
  - `/ws/nurse`: Dedicated WebSocket for the `/nurse` browser client.
  - `/ws/patient`: Dedicated WebSocket for the `/patient` browser client.
- **Session Coordinator (`ActiveSession` class)**:
  - A thread-safe, singleton state coordinator to pair connected `/nurse` and `/patient` clients.
  - When the Nurse selects a scenario, model, or target language on `/nurse`, the `ActiveSession` pushes a synchronized state configuration JSON to the Patient `/patient` client.
  - Handles client disconnects gracefully, resetting states and alerting active sessions.

### 2.2 Continuous, No-Pause Playhead Streaming
- Clicking "Start Call" on the `/nurse` view triggers the backend to load the stereo WAV file, split it in memory into Left and Right channels, and stream them continuously.
- **Lockstep Paced Streaming**:
  - The server sends 200ms audio chunks every 200ms using real-time loop throttling.
  - Patient mono chunks (Left channel) are routed directly down `/ws/patient`.
  - Nurse mono chunks (Right channel) are routed directly down `/ws/nurse`.
  - **No Server Holds**: The server-side streaming loop **never pauses, holds, or blocks** based on Gemini's transcription states. It runs continuously at 100% real-time speed.

### 2.3 Independent Client-Side Web Audio Panning Sliders
To support bilingual call participants on separate client devices, **the `/nurse` and `/patient` views have completely independent, localized Audio Panning Sliders** (they are NOT ganged or synchronized together). 
- **The Rationale**: 
  - The Nurse only speaks/understands English and wants to adjust the slider on `/nurse` to hear the Patient's English translation.
  - The Patient only speaks/understands their native language (e.g. German) and wants to adjust the slider on `/patient` to hear the Nurse's German translation.
  - Making the sliders independent allows each participant to control their own mix without affecting the other's workspace.
- **Audio Routing Node Graph**:
  On both `/nurse` and `/patient` frontends independently, construct an HTML5 `AudioContext` with separate `StereoPannerNode` units:
  ```text
  [ Original Audio Node (WAV Stream) ] ────► [ Panner L (-0.6) ] ───┐
                                                                   ├───► [ Destination ]
  [ Translated Audio Node (Gemini TTS) ] ──► [ Panner R (+0.6) ] ───┘
  ```
- **The Interactive Slider**:
  - Provide an independent slider on both frontends labeled **"Audio Panning Demo Control"** with values ranging from `-1.0` (Left) to `+1.0` (Right).
  - Adjusting the slider scales the gain/volume of the nodes locally on that client's browser:
    - **Fully Left (-1.0)**: Mutes the Right (Translated) node, playing *only* the original speaker's voice.
    - **Fully Right (+1.0)**: Mutes the Left (Original) node, playing *only* the translated interpreter's voice.
    - **Centered (0.0)**: Blends both original and translated audio 50/50, demonstrating simultaneous interpretation.

### 2.4 Interface Layouts

#### A. Nurse View (`/nurse`)
- **Master Controls**: Dropdown selectors for "Scenario", "Model", and "Patient Language".
- **Call Actions**: "Start Call" and "End Call" controls.
- **Panning Control**: Prominent slider to adjust demo panning in real-time.
- **Live Transcript**: Dual-column simultaneous transcript showing English and the Patient's language, complete with clinical glossary highlighted terms.
- **Side Panel**: Interactive Australian Medical Glossary search and encountered medical reference log.

#### B. Patient View (`/patient`)
- **Simplified Caller UI**: Minimalist, accessible, mobile-friendly design using HealthDirect typography.
- **Sync Status**: Large marquee showing "Waiting for Clinician..." until the Nurse starts the session.
- **Automatic Sync**: Detects scenario/language updates from the Nurse master and updates the UI instantly.
- **Incoming Transcript**: Renders only the translated clinician's words in native language (large font) and a preview of their own transcribed words.
- **Panning Control**: Prominent slider to adjust demo panning on the Patient side.

### 2.5 Single-Machine Demo & Google Meet Sharing Considerations
When presenting this solution to a customer over a Google Meet call, the presenter will typically have **both `/nurse` and `/patient` windows open side-by-side on a single machine**.
To prevent simultaneous overlapping translations from playing out loud over the same physical speaker (which can confuse Google Meet listeners), the frontends will implement:
- **"Demo Focus" Audio Toggles**:
  - Provide a prominent button/toggle on both views labeled **"Demo Mode: Focus Audio"** or **"Mute Tab Audio"**.
  - Clicking this toggle instantly mutes or attenuates (drops by 90%) all audio playback (original WAV and Gemini translation) for *that specific browser tab*.
- **The Presenter Flow**:
  - To showcase what the **Nurse** experiences: The presenter turns on "Demo Focus" on `/nurse` and *mutes* `/patient`. The audience hears the Patient's English translation seamlessly.
  - To showcase what the **Patient** experiences: The presenter turns on "Demo Focus" on `/patient` and *mutes* `/nurse`. The audience hears the Nurse's German/Spanish translation.
  - This prevents double-vocal clashing during screen shares and gives the presenter complete control over the auditory experience!

---

## 3. Git Reversion Path

Because this represents a significant shift from the previous sequential turn-taking pacing approach, we must protect the current code:
- **Dedicated Branch**: All work will be developed and committed on a new branch: `feature/simultaneous-multi-client`.
- **Branch Origin**: Branched from the stable `stable-pre-modularization` commit.
- **Reversion Command**: If we need to revert or compile a comparison build, a simple:
  ```bash
  git checkout stable-pre-modularization
  ```
  will instantly restore the old sequential pacing architecture, ensuring 100% safety and backward compatibility.

---

## 4. Acceptance Criteria
- [ ] Navigating to `/nurse` and `/patient` in separate windows loads their respective interfaces.
- [ ] Language and scenario selections on `/nurse` are synchronized instantly to `/patient`.
- [ ] Initiating the call triggers continuous, simultaneous audio streaming of both channels in perfect lockstep.
- [ ] Gemini Live translates on-the-fly and streams back audio, playing concurrently over the continuing stream.
- [ ] The audio panning slider successfully isolates the original voice, isolates the translated voice, or blends them together perfectly.
- [ ] No regressions in core translation, clinical glossary parsing, and database queries.
- [ ] The Git reversion path is successfully validated.
