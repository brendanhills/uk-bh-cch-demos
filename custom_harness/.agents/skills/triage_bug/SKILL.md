---
name: triage_bug
description: Investigate cause, plan solution, and assign priority/impact for bugs without executing fixes.
---

# Bug Triage Command (`/triage_bug`)

When the user runs `/triage_bug`:
- **With Argument (`/triage_bug #id`)**: Look up the bug ID in `<workspace-root>/.agents/bugs.json`. Investigate cause, outline proposed plan, assign `priority` (`P0`-`P3`) and `impact` (`Critical`-`Low`), and update status to `"Investigated"`. Do NOT execute the fix.
- **Without Argument (`/triage_bug`)**: Find all untriaged bugs (where `priority` and `impact` are empty `""`) in `.agents/bugs.json` and triage each sequentially without executing fixes.
