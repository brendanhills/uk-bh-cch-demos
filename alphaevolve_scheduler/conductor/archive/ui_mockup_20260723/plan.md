# Implementation Plan: Initial UI/UX Prototype Mockup

## Phase 1: Setup & HTML Skeleton
### Goal: Establish the single-file layout and base visual styles.
- [x] Task: Create initial `index.html` structure and layout
  - [x] Create basic HTML5 boilerplate
  - [x] Define CSS Grid/Flexbox layout for the 4 main panels (Gantt, Floor Plan, Metrics, Staff Grid)
  - [x] Apply RCH branding colors and professional base styles
- [x] Task: Phase Verification & Checkpoint
  - [ ] (Refer to workflow.md: Visual/Manual Approval in browser)

## Phase 2: Mock Data & State Architecture
### Goal: Design the underlying data structures to drive the replay animations.
- [x] Task: Design and embed the mock Phase 1 RCH Data
  - [x] Craft the baseline schedule (2 OTs, Staff, Appointments with severe resource overlaps/conflicts)
  - [x] Craft the AlphaEvolve optimized schedule (resolved conflicts, minimal overtime)
  - [x] Structure the data as an array of evolution steps/traces
- [x] Task: Implement state management JS
  - [x] Add state variables for current step, play/pause state, and baseline/evolved toggle
- [x] Task: Phase Verification & Checkpoint
  - [ ] (Refer to workflow.md: Visual/Manual Approval by inspecting the data object in console)

## Phase 3: SVG Floor Plan & Metrics UI
### Goal: Build the visual elements surrounding the main schedule.
- [x] Task: Implement the SVG Floor Plan
  - [x] Draw/embed inline SVG for the 2 Operating Theatres and pre-op areas
  - [x] Add CSS classes and IDs for active/pulsing states
- [x] Task: Implement the Metrics Panel & Staff Grid
  - [x] Add HTML counters and UI controls (Play button, Toggle)
  - [x] Render a clean, static Staff Availability Grid below the main layout
- [x] Task: Phase Verification & Checkpoint
  - [ ] (Refer to workflow.md: Visual/Manual Approval of static layout in browser)

## Phase 4: Gantt Chart & Replay Logic (The "Wow" Factor)
### Goal: Implement the core scheduling timeline and the animation logic.
- [x] Task: Implement the Interactive Gantt Chart
  - [x] Create the Time (Weekly/Daily) and Resource (2 OTs) grid structure
  - [x] Write JS to render shift and appointment blocks dynamically based on the current state data
- [x] Task: Implement Replay & Animation Logic
  - [x] Write a JS interval to step through the evolution traces when the "Play" button is clicked
  - [x] Add CSS transitions for smooth block shifting and Floor Plan room lighting up
  - [x] Wire up the Baseline vs. Evolved toggle to swap datasets smoothly and update counters
- [x] Task: Phase Verification & Checkpoint (Deferred Visual Verification by User)
  - [ ] (Refer to workflow.md: Visual/Manual Approval of the full animation loop)

## Phase 5: Final Polish & Zero-Network Review
### Goal: Ensure the demo is flawless, professional, and fully portable.
- [x] Task: Polish animations and labels
  - [x] Ensure all labels are strictly jargon-free and professional
  - [x] Fine-tune transition timings for optimal "Wow" effect
- [x] Task: Ensure Zero-Network compliance
  - [x] Verify that all styles, scripts, and SVGs are inline and work completely offline
- [x] Task: Track Completion & Handover
  - [x] Final visual review with the user to close the track
