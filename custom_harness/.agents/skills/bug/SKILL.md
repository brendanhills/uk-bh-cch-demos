---
name: bug
description: Record a bug report in the workspace bugs registry without fixing it immediately.
---

# Bug Reporting Command (`/bug`)

When the user runs `/bug` (or reports a bug), do NOT try to fix it immediately.
1. Record the bug description, date, and workspace context into `<workspace-root>/.agents/bugs.json`.
2. Initialize separate `"priority"` and `"impact"` fields to empty (`""`).
3. Set status to `"Reported"`.
