---
name: fr
description: Record a feature request (FR) in the workspace registry without implementing it immediately.
---

# Feature Request Command (`/fr`)

When the user runs `/fr` (or submits a feature request):

1. Do NOT try to implement the feature request immediately.
2. Record the feature description, date, and workspace context into `<workspace-root>/.agents/bugs.json`.
3. Use the next sequential `BUG-N` ID.
4. Set `"type"` to `"FR"`.
5. Initialize `"priority"`, `"impact"`, `"risk"`, and `"phase"` fields to empty (`""`).
6. Set status to `"Reported"`.
