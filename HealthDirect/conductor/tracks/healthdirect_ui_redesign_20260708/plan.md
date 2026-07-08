# Plan: HealthDirect UI Redesign (`healthdirect_ui_redesign`)

## Phase 1: CSS Architecture & Global Design Tokens (Theme Shift)
- [x] Task: Shift variables to high-fidelity Light Mode and configure brand color systems [3030f8a]
    - [x] Override global CSS variables in `:root` with light-mode equivalents (backgrounds, text-primary, text-secondary)
    - [x] Set brand colors: Navy (`#0c426e`), Coral-Orange (`#f05a28`), and Accent Teal (`#00a29a`)
    - [x] Redefine button styling and state transitions (hover, active, disabled) to look flat, modern, and clean
    - [x] Update background color and general layout container rules to look cohesive
- [~] Task: Conductor - User Manual Verification 'Phase 1: CSS Architecture & Global Design Tokens' (Protocol in workflow.md)

## Phase 2: Mock Video Call Layout & Floating Overlays
- [ ] Task: Redesign the Call Monitor Board as two premium, wide-aspect video stream feeds
    - [ ] Replace simple card containers in `index.html` with `.video-stream-frame` mock structures
    - [ ] Add SVG-based default avatars (Patient and Nurse) and camera backdrop overlays
- [ ] Task: Implement floating controls and metrics overlays matching the screenshot
    - [ ] Add upper dark pill overlays: floating clinic/call badge ("ACT GP") and call timer on the left; signal strength and HD badges on the right
    - [ ] Add lower horizontal hover controls: sleek floating black bars containing microphone, camera, snapshot, full-screen, PIP, pin, and minimize SVGs
    - [ ] Update active-speaker border glow in CSS (Coral-Orange glow for Patient, Teal/Navy glow for Clinician)
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Mock Video Call Layout & Floating Overlays' (Protocol in workflow.md)

## Phase 3: Console Audio Mixer & Unified Sidebar Workspace
- [ ] Task: Restyle the Audio Mixer and Cross-fader as an elegant hardware console
    - [ ] Align the slider control container directly below the video streams
    - [ ] Add a clean slider track with ticks, a brand-colored gradient fill, and sleek labels for foreign language/English speaker outputs
- [ ] Task: Refactor the workspace layout as a unified right sidebar console
    - [ ] Group the Live Transcript feed and Clinical Glossary/References side-by-side or as stacked vertical widgets on the right side of the screen
    - [ ] Match the layout of the "Video Call Apps" sidebar from the HealthDirect screenshot
    - [ ] Polish scrollbars, search input, filter chips, and card headers to match the brand typography and white/light styling
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Console Audio Mixer & Unified Sidebar Workspace' (Protocol in workflow.md)

## Phase 4: Integration Testing & Verification
- [ ] Task: End-to-end local test and verification
    - [ ] Start the FastAPI server locally and open the browser
    - [ ] Run clinical call scenarios (German, Spanish, Vietnamese, Arabic) to verify that speech translation, WebSocket messaging, audio playback, and pacing work perfectly
    - [ ] Verify that glossary word highlighting, hover tooltips, and search filtering work flawlessly with the new HTML structures
    - [ ] Ensure that existing python test suite passes without any failures or regressions
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Integration Testing & Verification' (Protocol in workflow.md)
