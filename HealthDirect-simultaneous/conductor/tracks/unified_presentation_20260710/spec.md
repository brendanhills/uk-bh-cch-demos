# Specification: Single-Tab Unified Presentation Console (Alternative View)

## 1. Overview
The **Single-Tab Unified Presentation Console** is a standalone, alternative presentation dashboard (`presentation.html` or `unified.html`) designed to solve browser screen-sharing audio limitations. It allows clinicians (Nurses) to present simultaneous translation sessions over Google Meet (or similar web conferencing tools) with full audio sharing. By integrating both the Nurse Interface and the Patient View into a single browser tab, presenters can select the unified tab in Chrome's sharing picker, which natively captures and shares all synthesised speech and original audio.

This dashboard is an **alternative view** that runs in parallel with the existing independent split-tab screens (`nurse.html` and `patient.html`), which remain fully functional and unchanged for in-person or dual-monitor demonstrations.

## 2. Functional Requirements
- **Unified Alternative Container (`presentation.html`):** A new HTML endpoint that acts as a secure parent container.
- **Split-View / PIP Architecture:**
  - **Side-by-Side Mode:** A beautifully styled split-screen layout displaying the Nurse Console (left, 70% width) and the Patient View (right, 30% width).
  - **Floating Picture-in-Picture (PIP) / Overlay Mode:** A draggable, resizable floating card showing the Patient's view that overlays the Nurse Console, mimicking a native PIP overlay.
- **Audio Routing & Output:**
  - Standardise all audio playback inside the parent tab context to ensure Chrome's native tab audio capture captures both patient original/translated and nurse original/translated streams without echo or feedback.
- **Independent Context Scaling:** The Patient View card/frame must scale down gracefully using CSS transforms or standard layout rules, remaining perfectly readable at smaller form factors.
- **Session Reset & Synchronization:** The "Reset Session" and config dropdowns must seamlessly reset the entire unified presentation workspace in one click.

## 3. Non-Functional Requirements
- **Aesthetic Excellence:** Adhere to premium HealthDirect CSS styles, keeping the layout clean, responsive, and visually modern.
- **Zero-Latency Event Propagation:** Frame communication (if using iframes or parent-child postMessage) must be synchronous and introduce zero lag.

## 4. Acceptance Criteria
- [ ] Presenters can load `/presentation.html` or `/unified.html` and see both screens.
- [ ] Sharing the single tab in Chrome shares both the nurse's spoken audio and the patient's translated speech audio with remote participants.
- [ ] Layout scales elegantly across standard presentation resolutions (1080p, 1440p).
- [ ] No audio feedback or echo is introduced.

## 5. Out of Scope
- Native operating system virtual audio driver installations.
- Multi-monitor physical hardware configurations.
