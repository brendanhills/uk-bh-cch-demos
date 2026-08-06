---
name: fix_bug
description: Implement a bug fix by first writing a reproduction unit test, then modifying code until tests pass.
---

# Fix Bug Command (`/fix_bug`)

When the user runs `/fix_bug`:
- **With Argument (`/fix_bug #id`)**: Look up the bug ID in `.agents/bugs.json`. Formulate a plan and adopt **Adaptive Tiered Verification**:
  1. **Tier 1 (Simple / Low-Risk P2-P3 Bugs)**: Implement the fix directly and verify using existing regression suites (`pytest`). Do not waste time building new reproduction harnesses.
  2. **Tier 2 (Standard P1-P2 Bugs)**: Implement the fix and add a simple, lightweight test case to an *existing* unit test file.
  3. **Tier 3 (Critical P0 Blocker Bugs)**: Attempt to write an automated reproduction unit test. **Circuit Breaker**: If test harness/mock setup fails more than **2 times**, abandon test creation immediately, implement the fix directly, and verify via existing regression suites.
  Once verified, set `"date_resolved"` to current date (`YYYY-MM-DD`), update status to `"Fix Implemented"`, commit on `dev`, and create annotated bugfix tag: `git tag -a "<subfolder>/bugfix-<bug_id>" -m "Fix verified for <bug_id> in <subfolder>"`.
- **Without Argument (`/fix_bug`)**: Read `.agents/bugs.json`, identify open bugs, sort chronologically by priority (`P0` -> `P3`), and present a recommended sequence of resolution.
