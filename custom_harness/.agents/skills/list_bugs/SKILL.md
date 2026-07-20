---
name: list_bugs
description: List all recorded bugs from the workspace registry in a structured markdown table.
---

# List Bugs Command (`/list_bugs`)

When the user runs `/list_bugs` (or `/list bugs`):
1. Read `<workspace-root>/.agents/bugs.json` from the active workspace.
2. Render a clear, structured markdown table displaying all recorded bugs, their priority, impact, status, and description.
