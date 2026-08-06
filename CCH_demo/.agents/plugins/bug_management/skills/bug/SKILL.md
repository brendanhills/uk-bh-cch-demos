---
name: bug
description: Record a bug report in the workspace bugs registry without fixing it immediately.
---

# Bug Reporting Command (`/bug`)

> [!CAUTION]
> **CRITICAL HARD CONSTRAINT**: Under NO CIRCUMSTANCES should you write code modifications, edit files, run tests, or attempt to fix the bug when `/bug` is called. Code changes are EXCLUSIVELY PERMITTED when the user explicitly invokes `/fix_bug`. Running tests is STRICTLY PROHIBITED during `/bug`.

When the user runs `/bug` (or reports an issue):
1. Record the description, date, and workspace context into `<workspace-root>/.agents/bugs.json`.
2. Evaluate context: if the report is explicitly a new feature or enhancement request, set `"type"` to `"FR"`, otherwise set `"type"` to `"Bug"`.
3. Initialize `"priority"`, `"impact"`, `"risk"`, and `"phase"` fields to empty (`""`).
4. Set status to `"Reported"`.
5. Acknowledge recording the bug report to the user and HALT. Do NOT write/modify code or run tests.
