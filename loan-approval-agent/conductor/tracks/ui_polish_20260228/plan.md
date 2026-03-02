# Implementation Plan: UI Polish and Runner Simplification

## Phase 1: Core Stability & Reset
- [x] Task: Revert `demo_frontend/app.py` and `tests/` to use the simplest `InMemoryRunner(agent=loan_manager)` pattern, removing `App` wrapping where it introduced complexity.
- [x] Task: Implement a "Reset Session" button in the center panel header or sidebar that clears `st.session_state["messages"]` and `st.session_state["session_id"]`.
- [x] Task: Conductor - User Manual Verification 'Core Stability & Reset' (Protocol in workflow.md)

## Phase 2: Live Trace & UI Polish
- [x] Task: Update the right-hand panel in `demo_frontend/app.py` to ensure it reads the latest events from `loan_agent/data/audit_logs/events.jsonl` on every Streamlit rerun.
- [x] Task: Rename the right panel to "Reasoning Trace" and verify icons/labels match the demo narrative.
- [x] Task: Final aesthetic audit of the "FastLoan Portal" center panel to ensure a clean, corporate look.
- [x] Task: Conductor - User Manual Verification 'Live Trace & UI Polish' (Protocol in workflow.md)
