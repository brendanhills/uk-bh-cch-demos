# Specification: HealthDirect UI Redesign (`healthdirect_ui_redesign`)

## Overview
Redesign the Bilingual Medical Call Monitor web application interface to match the look, feel, brand identity, and high-fidelity video-call layout of the real HealthDirect application shown in the screenshot. All existing backend logic, WebSocket connections, audio playback/pacing, cross-fader mixing, real-time transcript logging/rendering, and clinical glossary searching/tooltips must remain fully functional without any feature regressions.

## Brand Identity & Aesthetic Elements
- **Aesthetic**: Modern High-Fidelity Light Mode. Clean white and light gray backgrounds, crisp typography, and professional drop shadows.
- **Brand Colors**:
  - **HealthDirect Navy**: `#0c426e` (Primary for headings, headers, bold text)
  - **HealthDirect Coral-Orange**: `#f05a28` (Primary brand accent, logo circle, active-speaker indicator)
  - **HealthDirect Teal-Cyan**: `#00a29a` (Secondary brand accent for secondary links and icons)
- **Typography**: Inter (Sans-serif) for clean readability, JetBrains Mono (Monospace) for metrics and timing codes.

## Functional & Layout Changes

### 1. Logo and Header
- Replace the simple text header with a styled brand logo: "healthdirect" (bold navy and orange) and "Video Call" in a sleek, lightweight teal font.
- Incorporate the iconic dot-circle emblem to the right of the logo text.
- Reorganize the top control section:
  - Clean drop-down selectors for "Scenario" and "Model".
  - Sleek, compact pacing sliders (Turn Timeout, Audio Ceased, Audio Startup, Transition Pause).
  - Modernized, flat buttons with soft brand color fills and hover micro-animations.

### 2. Side-by-Side Video Stream Frames (Monitor Board)
- Replace the simple participant cards with side-by-side mock video call frames representing "Patient Caller" and "Nurse Sarah" (the clinician).
- Inside each stream frame:
  - A mock high-definition video view with a professional avatar or static image placeholder (representing a patient/baby for the patient, and a professional doctor/nurse with a headset for the clinician).
  - **Floating Upper Dark Pills**:
    - Patient Frame: Floating clinic label ("ACT GP") and elapsed call timer ("03:15" or running timer).
    - Clinician Frame: Signal connectivity indicator icon and HD icon.
  - **Floating Hover Control Bars**: At the bottom center of each stream, a horizontal dark pill control bar containing modern white icons:
    - Patient Frame: [Pin], [Mute/Unmute Mic], [Snapshot], [Full Screen], [Picture-in-Picture].
    - Clinician Frame: [Pin], [Snapshot], [Full Screen], [Minimise], [Flip].
  - **Active-Speaker Indicator**: Display a premium glowing border around the active speaker's stream container (Coral-Orange glow for the Patient, Teal-Cyan or Navy glow for the Clinician).

### 3. Integrated Audio Mixer Dashboard
- Style the cross-fader and mixer as a physical hardware mixer console integrated directly below the video streams.
- Use a high-end sliding track, marked with ticks (`100% Patient`, `Bilingual Mix 50/50`, `100% English`), a subtle color gradient trail, and responsive handle hover states.

### 4. Consolidated Right Sidebar (Live Transcript & Glossary)
- Instead of taking up the entire bottom space, the Live Conversation Transcript and Clinical Glossary will be structured as sleek side-by-side vertical panels or a unified right-side console mimicking the "Video Call Apps" panel.
- This creates an immersive single-screen workspace layout (Call streams on the left, interactive data apps on the right).
- Features clean scroll bars, search bars, and filter chips.

## Acceptance Criteria
- Web UI transitions fully to a gorgeous Light Mode.
- Video call stream look-and-feel closely matches the provided HealthDirect screenshot.
- Zero feature regressions: All scenarios, models, pacing controls, and glossary/transcript highlight streams continue to work perfectly.
