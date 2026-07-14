# Implementation Plan: Single-Tab Unified Presentation Console

## Phase 1: Parent Container & Unified Routing Layout
- [x] Task: Create a failing integration test for the presentation.html page load, layout verification, and router matching. [24769c9]
- [x] Task: Implement the new `demo/web/presentation.html` standalone view with an elegant dual-frame layout (left pane for Nurse console, right pane for Patient native view). [24769c9]
- [x] Task: Add route integration inside `demo/web_server.py` to serve `/presentation.html` and register it on startup. [24769c9]
- [x] Task: Conductor - User Manual Verification 'Phase 1: Parent Container & Unified Routing Layout' (Protocol in workflow.md) [7820dfe]

## Phase 2: Session Sync, Scaling & Picture-in-Picture (PIP) Floating Panel
- [ ] Task: Add failing unit tests verifying synchronization events when triggering "Reset Session" or "Start Call".
- [ ] Task: Implement window-level message passing (`postMessage`) or unified WebSockets state synchronisation so that the Nurse pane can trigger state resets, model selections, and calls across both panels simultaneously.
- [ ] Task: Create a toggleable, resizable Picture-in-Picture (PIP) floating panel widget for the Patient View so users can seamlessly switch between Side-by-Side Split layout and Overlay layout.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Session Sync, Scaling & Picture-in-Picture (PIP) Floating Panel' (Protocol in workflow.md)

## Phase 3: Premium Styling Polish & Audio Sharing Help Overlay
- [ ] Task: Write comprehensive automation tests verifying that dual-channel audio streams operate independently and do not conflict within a single browser tab context.
- [ ] Task: Apply premium HealthDirect CSS styling, adding responsive flex layouts, smooth slide transitions, and CSS scale-down transforms for smaller screens.
- [ ] Task: Add a high-visibility, elegant "Google Meet Audio Sharing Guide" overlay to teach presenters how to enable the "Share tab audio" option.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Premium Styling Polish & Audio Sharing Help Overlay' (Protocol in workflow.md)
