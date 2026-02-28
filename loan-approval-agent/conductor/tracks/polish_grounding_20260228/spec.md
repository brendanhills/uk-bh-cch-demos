# Specification: Demo Polish, Code Simplification, and Enhanced Grounding

## Overview
Simplify the Loan Approval Agent codebase for improved demo clarity, synchronize the `demo.md` documentation with the application flow, and enhance the policy grounding by expanding the PDF database. The goal is to make the system "simple, clear, and easy to explain" while ensuring all decision-making rules are strictly derived from policy documents rather than hardcoded in prompts.

## Functional Requirements
1.  **Enhanced Policy Grounding**:
    *   Expand the policy PDF database (`loan_agent/data/policy_docs/`) with more realistic and detailed content, including specific interest rate tiers based on credit scores.
    *   Ensure the database provides enough detail to support all demo scenarios (Sarah Speed, Gary Escalate, Jane Fraud, etc.) without needing hardcoded logic in prompts.
2.  **Prompt Cleanup**:
    *   Remove hardcoded policy rules (e.g., interest rate tiers, DTI thresholds) from agent prompts (Underwriter, Policy Expert).
    *   Ensure agents are explicitly instructed to use only retrieved policy data for decision-making.
3.  **Core Logic Simplification**:
    *   Audit and clean up `loan_agent/agent.py` and sub-agent definitions.
    *   Simplify `loan_agent/tools/` to focus on the essential logic required for the demo narrative.
4.  **Documentation Alignment**: 
    *   Verify the exact sequence of events in the Streamlit UI.
    *   Update `docs/DEMO.md` to reflect the actual flow (Intake -> Investigation -> Policy -> Decision).

## Non-Functional Requirements
*   **Maintain Integrity**: All existing unit and integration tests must pass.
*   **Clarity**: Code should follow the "General Code Style Principles" (readability, simplicity).

## Acceptance Criteria
*   `docs/DEMO.md` matches the actual application flow 1:1.
*   All underwriting rules (rates, thresholds) are retrieved from PDFs during the "Policy Review" step.
*   Prompts are free of hardcoded lending thresholds.
*   Code is simplified and verified through passing tests.

## Out of Scope
*   Fixing deprecation warnings.
*   Adding new features or tools.
*   Major UI redesign.
