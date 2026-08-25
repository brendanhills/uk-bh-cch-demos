---
name: fix_bug
description: Implement a bug fix by first writing a reproduction unit test, then modifying code until tests pass.
---

# Fix Bug Command (`/fix_bug`)

When the user runs `/fix_bug`:

- **Without Argument (`/fix_bug`)**:
  1. Read `<workspace-root>/.agents/bugs.json`.
  2. Identify all open, unresolved bugs (status is NOT `"Fix Verified"`, `"Closed"`, or `"Obsolete"`).
  3. Sort the open bugs by priority (`P0` -> `P1` -> `P2` -> `P3`), then chronologically by ID.
  4. Present a clear, recommended sequence of resolution in conversation.
  5. **FAST PATH**: Do NOT write code modifications or construct test harnesses when called without an argument.

- **With Argument (`/fix_bug #id`)**:
  1. Look up the specified bug ID in `<workspace-root>/.agents/bugs.json`.
  2. Formulate a plan and adopt **Adaptive Tiered Verification**:
     - **Tier 1 (Simple / Low-Risk P2-P3 Bugs)**: Implement the fix directly in source files and verify using existing test suites (`pytest`). Do not build separate reproduction harnesses.
     - **Tier 2 (Standard P1-P2 Bugs)**: Implement the fix and add a lightweight test assertion to an existing test file.
     - **Tier 3 (Critical P0 Blocker Bugs)**: Write an automated reproduction unit test verifying failure before fix.
  3. **CIRCUIT BREAKER**: If test harness setup fails more than **1 time**, abandon reproduction test creation immediately, implement the fix directly, and verify against existing regression suites.
  4. After verification passes:
     - Set `"date_resolved"` to current date (`YYYY-MM-DD`).
     - Update `"status"` to `"Fix Implemented"` in `<workspace-root>/.agents/bugs.json`.
     - Confirm resolution to the user.
