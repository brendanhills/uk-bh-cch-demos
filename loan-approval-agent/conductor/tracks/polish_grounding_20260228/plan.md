# Implementation Plan: Demo Polish, Enhanced Grounding, and Test Hardening

## Phase 1: Unit Testing Hardening (Scenario-Based)
- [x] Task: Implement `tests/test_scenario_tools.py` to test each tool (Credit, Employment, Fraud, DTI) individually using values from the demo scenarios (Sarah Speed, Gary Escalate, Jane Fraud).
- [x] Task: Implement `tests/test_scenario_agents.py` to test each agent persona (Investigator, Policy Expert, Underwriter) using mocked tools but real scenario inputs to verify their reasoning logic.
    - [x] *Sub-task*: Verify Investigator parallel tool execution logic.
    - [x] *Sub-task*: Verify Underwriter synthesis logic (handling contradictory or missing data).
- [x] Task: Conductor - User Manual Verification 'Unit Testing Hardening' (Protocol in workflow.md)

## Phase 2: PDF Database Expansion & Grounding Logic
- [x] Task: Update `loan_agent/sub_agents/policy_expert/tools.py` to ensure it extracts *citations* (Section #, Rule Name) as required by the "Explainability" goal in the prompt.
- [x] Task: Verify the `Standard_Underwriting_Guidelines_2026.pdf` content supports the "Sarah Speed" auto-approval path AND the "Gary Escalate" manual review path.
- [x] Task: Conductor - User Manual Verification 'PDF Database Expansion' (Protocol in workflow.md)

## Phase 3: Prompt Cleanup & Logic Simplification
- [x] Task: Create `tests/test_policy_grounding.py` to verify that agents correctly fail or request info when policy data is missing from context (proving no hardcoded fallbacks).
- [x] Task: Refactor `loan_agent/agent.py` and core tools to remove redundant logging and simplify the "trace" for presentation clarity.
- [x] Task: *PRESENTATION TARGET*: Update Underwriter prompt to explicitly include the "Reasoning Chain" with citations in the `final_decision_output`.
- [x] Task: Conductor - User Manual Verification 'Prompt Cleanup & Logic Simplification' (Protocol in workflow.md)

## Phase 4: Demo Script & Presentation Alignment
- [x] Task: Update `docs/PRESENTATION.md` to reflect the Gemini 3.1 architecture and "Thinking: HIGH" differentiator.
- [x] Task: Map every demo scenario to a specific requirement in `demo_task.txt` (e.g., Sarah Speed = Requirement #4: Auto-approve in < 5 mins).
- [x] Task: Perform a full 10-minute dry run using `docs/DEMO.md` and capture the exact sequence of agent "thoughts" and tool calls in the Streamlit UI.
- [x] Task: Update `docs/DEMO.md` to explicitly mention the time-saving metrics (48h manual wait vs 10s agent execution).
- [x] Task: Refresh architecture diagrams in `docs/diagrams/` to ensure they 100% match the consolidated `loan_agent/` structure.
- [x] Task: Conductor - User Manual Verification 'Demo Script Alignment' (Protocol in workflow.md)
