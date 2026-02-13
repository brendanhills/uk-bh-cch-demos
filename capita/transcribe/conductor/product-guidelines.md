# Product Guidelines

These guidelines define the quality standards, architectural principles, and user experience goals for the Real-Time Transcription Simulator.

## 1. Tone and Voice
- **Pragmatic & Modern:** The simulator should feel like a high-performance developer tool. Documentation and CLI logs should be clear, actionable, and focus on developer productivity.
- **Transparent:** Never hide the complexity of real-time transcription. Instead, use visual and logical tools to make that complexity manageable and understandable.

## 2. User Experience (UX) Standards
- **Visual Evolution:** Distinguish between "Interim" (draft) and "Final" results visually. Use grey text for ongoing speech and high-contrast colors (Green/Yellow) for finalized text to provide immediate yet stable feedback.
- **Columnar Layout:** Maintain a strict two-column spatial separation for 2-channel audio. The visual distinction between Caller and Agent is a core requirement.
- **Real-Time Responsiveness:** The CLI should feel "live." Updates should happen in small, incremental bursts (250ms chunks) to simulate the flow of a real conversation.

## 3. Accuracy and Reliability
- **Chronological Integrity:** Prioritize the correct ordering of conversational events. Use stability buffers to ensure that late-arriving packets are placed in their correct temporal position before display.
- **Atomic Data:** Every transcript chunk must be tied to its precise audio timestamp. This allows for reliable downstream analysis and "Golden Set" verification.
- **Perfect Attribution:** For 2-channel audio, the simulator must guarantee zero cross-talk in speaker identification by leveraging wire-level separation.

## 4. Architectural Principles
- **Modularity First:** Maintain a strict separation of concerns between:
    - **Audio Sourcing:** Downloading and throttling GCS files.
    - **Transcription Engine:** Handling API streaming and synchronization logic.
    - **UI Rendering:** Terminal-specific layout and ANSI color management.
- **Threshold Configurability:** All timing and logic parameters (Gaps, Buffers, Blocking) must be easily adjustable via environment variables or CLI flags to support diverse evaluation scenarios.
- **Modern Python Standards:** Leverage `uv` for dependency management and follow PEP 8 style guidelines with modern type hinting.

## 5. Development Workflow
- **Self-Contained Setup:** Ensure the project can be initialized and run with a single command (e.g., `uv run ...`).
- **Fail-Fast Debugging:** Provide clear, immediate feedback for common setup errors (e.g., missing GCP credentials, incorrect bucket permissions).
