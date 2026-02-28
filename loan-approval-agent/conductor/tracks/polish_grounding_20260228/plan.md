# Implementation Plan: Demo Polish, Enhanced Grounding, and Test Hardening

## Phase 1: Unit Testing Hardening (Scenario-Based)
- [ ] Task: Implement `tests/test_scenario_tools.py` to test each tool (Credit, Employment, Fraud, DTI) individually using values from the demo scenarios (Sarah Speed, Gary Escalate, Jane Fraud).
- [ ] Task: Implement `tests/test_scenario_agents.py` to test each agent persona (Investigator, Policy Expert, Underwriter) using mocked tools but real scenario inputs to verify their reasoning logic.
- [ ] Task: Conductor - User Manual Verification 'Unit Testing Hardening' (Protocol in workflow.md)

## Phase 2: PDF Database Expansion
- [ ] Task: Generate `loan_agent/data/policy_docs/Standard_Underwriting_Guidelines_2026.pdf` with granular rules (interest rates per credit tier, DTI thresholds, tenure requirements).
- [ ] Task: Update `loan_agent/sub_agents/policy_expert/tools.py` to ensure retrieval is optimized for the new comprehensive policy file.
- [ ] Task: Conductor - User Manual Verification 'PDF Database Expansion' (Protocol in workflow.md)

## Phase 3: Prompt Cleanup & Logic Simplification
- [ ] Task: Create `tests/test_policy_grounding.py` to verify that agents correctly fail or request info when policy data is missing from context (proving no hardcoded fallbacks).
- [ ] Task: Strip hardcoded interest rate tiers and DTI thresholds from prompts in `loan_agent/sub_agents/*/prompt.py`.
- [ ] Task: Refactor `loan_agent/agent.py` and core tools to remove redundant logging and simplify the "trace" for presentation clarity.
- [ ] Task: Conductor - User Manual Verification 'Prompt Cleanup & Logic Simplification' (Protocol in workflow.md)

## Phase 4: Demo Script Alignment
- [ ] Task: Perform a full end-to-end dry run of the Streamlit application and capture the sequence of agent "thoughts" and tool calls.
- [ ] Task: Update `docs/DEMO.md` to perfectly match the observed application flow and narrative.
- [ ] Task: Conductor - User Manual Verification 'Demo Script Alignment' (Protocol in workflow.md)
