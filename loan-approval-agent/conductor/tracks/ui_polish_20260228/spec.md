# Specification: UI Polish and Runner Simplification

## Overview
Polish the Streamlit demo application by reverting complex `InMemoryRunner` configurations to their simplest working state, restoring the live functionality of the audit trace, and improving the user experience for starting new scenarios.

## Functional Requirements
1.  **Runner Simplification**: Revert recent `InMemoryRunner` refactors (e.g., `App` wrapping) back to the simplest working approach to ensure maximum stability for the demo.
2.  **Scenario Reset**: Add a prominent "Reset Session / New Scenario" button to the UI that clears the message history, session ID, and center chat panel.
3.  **Audit Trace Restore**: 
    *   Ensure the right-hand panel correctly tracks the `events.jsonl` file in real-time.
    *   Verify the panel title and icons align with the "Reasoning Trace" narrative.
4.  **UI Refinement**:
    *   Ensure the center panel maintains a "Corporate Clean" fintech aesthetic.
    *   The right panel should feel technical and "live," highlighting the agentic reasoning process.

## Non-Functional Requirements
*   **Demo Reliability**: The "Reset" must be 100% reliable during a live presentation.
*   **Latency**: The trace panel must update with minimal delay after an event is logged.

## Acceptance Criteria
*   A "Clear Chat" or "New Scenario" button successfully resets the entire app state.
*   The Reasoning Trace updates live during an agent run.
*   `InMemoryRunner` is initialized in the simplest possible way without `DeprecationWarning` workarounds if they introduce risk.

## Out of Scope
*   New agent logic or tool features.
*   Changing the underlying mock data.
