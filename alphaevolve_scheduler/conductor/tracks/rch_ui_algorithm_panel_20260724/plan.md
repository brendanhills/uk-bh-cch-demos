# Implementation Plan: RCH UI Algorithm Display Panel

## Phase 1: Trace Schema & Exporter Updates
- [x] Task: Exporter Adaptation
  - [x] Modify the Trace Exporter (which we are about to build in Phase 3 of the main backend track) to include the `code` string in the streamed `data/traces.jsonl` snapshots
- [x] Task: Execution Verification
  - [x] Verify that running a test iteration successfully generates a `traces.jsonl` containing the `code` property without breaking JSON parsers
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: UI Implementation & Replay Binding
- [x] Task: DOM Structure & Styling
  - [x] Add the collapsible panel HTML to the bottom of `rch/index.html` matching the elegant dark theme
- [x] Task: Trace Replay Integration
  - [x] Hook into the state management and trace polling logic
  - [x] Ensure that clicking step dots on the chart or replaying the traces dynamically updates the text content of the code panel
- [x] Task: Syntax Highlighting
  - [x] Implement beautiful pre-formatted styling or integrate a lightweight client-side syntax highlighter for the Python code
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Demonstration & Polishing
- [~] Task: Inject Fatigue Violations card and Operational Scenario dropdown
- [ ] Task: End-to-End Verification
  - [ ] Run the complete pipeline and verify that as the AlphaEvolve traces stream and replay, the code panel seamlessly updates in perfect synchronization with the Gantt and metric charts
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
