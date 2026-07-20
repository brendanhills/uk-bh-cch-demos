---
name: fix_bug
description: Implement a bug fix by first writing a reproduction unit test, then modifying code until tests pass.
---

# Fix Bug Command (`/fix_bug`)

When the user runs `/fix_bug`:
- **With Argument (`/fix_bug #id`)**: Look up the bug ID in `.agents/bugs.json`. Formulate a plan. The **first task must be to write an automated reproduction unit test** that fails specifically due to this bug. Verify only that test fails, modify the code to fix the bug, verify all tests pass, and update status to `"Fix Implemented"`.
- **Without Argument (`/fix_bug`)**: Read `.agents/bugs.json`, identify open bugs, sort chronologically by priority (`P0` -> `P3`), and present a recommended sequence of resolution.
