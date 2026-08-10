# Track Specification: Initial UI/UX Prototype Mockup

## 1. Overview
Build a high-fidelity, interactive static HTML/JS UX Mockup and Prototype for the RCH Co-Scheduling dashboard. This track focuses strictly on implementing the visual layout, animations, and the "Wow" factor for non-technical stakeholders, establishing the visual anchor and frontend architecture for the project before any backend logic is implemented.

## 2. Functional Requirements

### 2.1 Single-File Architecture
- The entire prototype must be contained within a single `index.html` file (including inline CSS and JS) to ensure zero network calls at demo time and maximum portability.

### 2.2 UI Layout & Visual Elements
- **Primary Schedule View:** An Interactive Schedule Grid / Gantt Chart with the 2 Operating Theatres on the Y-axis and Time (Weekly Roster with 8/12 hour shifts) on the X-axis. Surgeries and staff assignments are rendered as colorful, overlapping blocks.
- **SVG Floor Plan:** A stylized, simplified architectural outline of the 2 Operating Theatres and pre-op areas. Rooms must light up or pulse when active or selected in the schedule replay.
- **Real-Time Metrics Panel:** A side or top panel featuring counters for *Patients Scheduled*, *Overtime Hours*, and *Resource Idle Time* that tick up and down smoothly during the replay.
- **Comparison Toggle:** A prominent "Baseline vs. AlphaEvolve Plan" toggle to instantly switch views.
- **Staff Availability Grid:** A secondary, clean table or grid below the main Gantt chart showing staff shifts.

### 2.3 Interactivity & Animations
- **Replay Animation:** A prominent "Play Optimization" button that replays a hardcoded evolution trace. 
- As the trace progresses, shift blocks on the Gantt chart must smoothly animate into their new positions, resolving conflicts.
- Metrics counters and the SVG Floor Plan must update in sync with the replay.

### 2.4 Data
- Driven entirely by a hand-crafted, mocked JSON structure embedded in the file representing Phase 1 RCH Data (2 OTs, Doctors, Nurses, and a set of Surgery Appointments).

## 3. Non-Functional Requirements

### 3.1 UX & Branding
- **Branding:** Strict adherence to RCH Official Colors (Professional Green, Blue, and White).
- **Tone:** Professional, clear, action-oriented, and strictly jargon-free labels (no technical algorithm terminology).
- **Performance:** Smooth 60fps SVG and CSS transitions during animations.

## 4. Acceptance Criteria
- Opening the file in a browser successfully renders the full layout with all panels.
- Clicking the "Play Optimization" button successfully replays the mock trace, demonstrating simultaneous updates across the Gantt chart, Metrics, and Floor Plan.
- Toggling between Baseline and AlphaEvolve clearly and instantly shows the reduction in overtime and resource conflicts.
- Zero console errors and zero external network requests.

## 5. Out of Scope for this Track
- Integration with the Python AlphaEvolve backend or real evaluator logic.
- Dynamic data loading or API endpoints.
- Full mobile responsiveness (optimized strictly for desktop/dashboard presentation).
- Constraint violation alerts or algorithm code diff views (kept hidden/omitted for non-technical simplicity).
