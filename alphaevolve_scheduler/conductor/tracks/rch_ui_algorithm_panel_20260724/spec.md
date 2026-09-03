# Track Specification: RCH UI Algorithm Display Panel

## 1. Overview
Implement a real-time, collapsible Algorithm Display Panel in the RCH UI that showcases the exact Python code being evaluated by AlphaEvolve at every step of the evolution. This brings feature parity with the original Kmart demo's translucent algorithmic transparency, adding a spectacular "Wow" factor as users watch the AI actively rewrite the heuristics.

## 2. Functional Requirements

### 2.1 UI/UX Implementation
- Create a new collapsible panel at the bottom of the main RCH dashboard, matching the elegant dark theme and design language of the dashboard.
- Default to collapsed, and expand gracefully when clicked (matching the Kmart demo exactly).
- Inside the panel, render a syntax-highlighted block displaying the current step's Python code.

### 2.2 Replay Integration
- Hook into the UI trace replay logic so that as the trace replays, or as the user clicks different dots on the charts or steps through the history, the code panel dynamically and instantly updates to show the exact Python code evaluated at that specific moment.
- The UI MUST be updated to read the `code` string from the trace steps.

### 2.3 Backend & Trace Schema Update
- Update the Trace Generation logic (which we are about to build in Phase 3 of the backend track) to include the full `code` string of each candidate in the streamed `data/traces.jsonl` snapshots.
- Ensure the streaming exporter handles the increased file size elegantly without breaking the real-time polling.

## 3. Non-Functional Requirements

### 3.1 Performance
- Real-time syntax highlighting and DOM updates must be highly performant so that fast replay (e.g., stepping through 50 candidates in a few seconds) remains smooth and does not lag the charts or Gantt animations.

### 3.2 Backward Compatibility
- If a trace step does not contain a `code` string, the panel should gracefully display a helpful fallback message (e.g., "Code not available for this step") without breaking the UI.

## 4. Acceptance Criteria
- A collapsible panel is visible at the bottom of the RCH dashboard.
- Clicking the panel expands it, showing a beautifully formatted and highlighted Python code block.
- During trace replay (either mock or real), the code updates dynamically and perfectly in sync with the step counter and charts.
- The backend traces schema is successfully updated to include the `code` field.

## 5. Out of Scope for this Track
- Code editing or interactive mutation triggering from the UI (strictly read-only display).

## 6. Future Considerations
- Implement Pseudocode translations or high-level summaries as a later refinement to make the logic perfectly accessible to non-technical users.
