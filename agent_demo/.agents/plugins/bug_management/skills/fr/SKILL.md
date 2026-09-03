---
name: fr
description: Record a feature request (FR) in the workspace registry without implementing it immediately.
---

# Feature Request Command (`/fr`)

> [!CAUTION]
> **CRITICAL HARD CONSTRAINT**: Under NO CIRCUMSTANCES should you write code modifications, edit files, run tests, or attempt to implement the feature when `/fr` is called. Code changes are EXCLUSIVELY PERMITTED when the user explicitly invokes `/fix_bug`. Running tests is STRICTLY PROHIBITED during `/fr`.

When the user runs `/fr` (or submits a feature request):
1. Record the feature description, date, and workspace context into `<workspace-root>/.agents/bugs.json`.
2. Use the next sequential `BUG-N` ID.
3. Set `"type"` to `"FR"`.
4. Initialize `"priority"`, `"impact"`, `"risk"`, and `"phase"` fields to empty (`""`).
5. Set status to `"Reported"`.
6. Acknowledge recording the feature request to the user and HALT. Do NOT write/modify code or run tests.
