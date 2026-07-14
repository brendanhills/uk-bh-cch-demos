# Implementation Plan: Single-Tab Unified Presentation Console

## Phase 1: Parent Container & Unified Routing Layout [checkpoint: a10b03e]
- [x] Task: Create a failing integration test for the presentation.html page load, layout verification, and router matching. [24769c9]
- [x] Task: Implement the new `demo/web/presentation.html` standalone view with an elegant dual-frame layout (left pane for Nurse console, right pane for Patient native view). [24769c9]
- [x] Task: Add route integration inside `demo/web_server.py` to serve `/presentation.html` and register it on startup. [24769c9]
- [x] Task: Conductor - User Manual Verification 'Phase 1: Parent Container & Unified Routing Layout' (Protocol in workflow.md) [7820dfe]

## Phase 2: Session Sync, Scaling & Picture-in-Picture (PIP) Floating Panel [checkpoint: 9925c5b]
- [x] Task: Add failing unit tests verifying synchronization events when triggering "Reset Session" or "Start Call". [a9739da]
- [x] Task: Implement window-level message passing (`postMessage`) or unified WebSockets state synchronisation so that the Nurse pane can trigger state resets, model selections, and calls across both panels simultaneously. [a9739da]
- [x] Task: Create a toggleable, resizable Picture-in-Picture (PIP) floating panel widget for the Patient View so users can seamlessly switch between Side-by-Side Split layout and Overlay layout. [a9739da]
- [x] Task: Conductor - User Manual Verification 'Phase 2: Session Sync, Scaling & Picture-in-Picture (PIP) Floating Panel' (Protocol in workflow.md) [2294d12]

## Phase 3: Premium Styling Polish
- [x] Task: Write comprehensive automation tests verifying that dual-channel audio streams operate independently and do not conflict within a single browser tab context. [32da7b9]
- [x] Task: Apply premium HealthDirect CSS styling, adding responsive flex layouts, smooth slide transitions, and CSS scale-down transforms for smaller screens. [a358f52]
- [~] Task: Conductor - User Manual Verification 'Phase 3: Premium Styling Polish' (Protocol in workflow.md)
