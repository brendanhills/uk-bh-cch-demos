---
description: Process for converting an idea into code with tests and verification.
---

1.  **Analyze the Idea**: Read the user's request. If it's vague, ask clarifying questions.

2.  **Create a Plan**:
    -   Analyze the codebase to understand the impact.
    -   Propose a step-by-step plan in `implementation_plan.md` or directly in the chat if simple.
    -   **CRITICAL**: Check for **Breaking Changes**.
        -   If the change breaks existing APIs, data structures, or tests in a way that requires significant refactoring or affects other components, **ALERT THE USER**.
        -   Suggest creating a feature branch or getting explicit approval for the breaking change.

3.  **Get Approval**: Wait for the user to approve the plan or the breaking change.

4.  **Implement Code**:
    -   Make the necessary code changes.
    -   Keep changes focused and minimal to the task.

5.  **Update Unit Tests**:
    -   Modify existing tests to reflect the changes.
    -   **CRITICAL**: Create NEW unit tests that specifically target the new functionality or fix.

6.  **Run Tests**:
    -   Run the relevant unit tests (e.g., `pytest tests/test_specific_feature.py`).
    -   Ensure all tests pass.

7.  **Fix and Iterate**:
    -   If tests fail, analyze the error.
    -   Fix the code or the test (if the test was wrong).
    -   Repeat steps 6-7 until all tests pass.

8.  **Final Verification**:
    -   Optionally run a manual verification step (e.g., CLI run or script) if unit tests aren't enough.
    -   Notify the user of completion.
