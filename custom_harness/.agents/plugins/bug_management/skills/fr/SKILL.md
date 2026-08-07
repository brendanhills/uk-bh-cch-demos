---
name: fr
description: Record a feature request (FR) in the workspace registry without implementing it immediately.
---

# Feature Request Command (`/fr`)

> [!CAUTION]
> **CRITICAL HARD CONSTRAINT**: Under NO CIRCUMSTANCES should you write code modifications, edit files, run tests, or attempt to implement the feature when `/fr` is called. Code changes are EXCLUSIVELY PERMITTED when the user explicitly invokes `/fix_bug`. Running tests is STRICTLY PROHIBITED during `/fr`.

When the user runs `/fr` (or submits a feature request):
1. Record feature description and workspace context into `<workspace-root>/.agents/bugs.json`.
2. Auto-detect `"reporter"` using `git config user.name` (fallback `$USER` or system user name).
3. Use the next sequential integer ID (e.g. 4, not BUG-4 or FR-2).
4. Set `"type"` to `"FR"`.
5. Set `"date_reported"` to current date (`YYYY-MM-DD`). Initialize `"date_triaged"` and `"date_resolved"` to empty (`""`).
6. Initialize `"priority"`, `"impact"`, `"risk"`, and `"phase"` fields to empty (`""`).
7. Set status to `"Reported"`.
8. Acknowledge recording the feature request to the user and HALT. Do NOT write/modify code or run tests.
