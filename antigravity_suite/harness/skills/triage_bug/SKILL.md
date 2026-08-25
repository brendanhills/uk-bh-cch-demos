---
name: triage_bug
description: Investigate cause, plan solution, and assign priority/impact for bugs without executing fixes.
---

# Bug Triage Command (`/triage_bug`)

When the user runs `/triage_bug`:

- **With Argument (`/triage_bug #id`)**:
  1. Look up the specified bug ID in `<workspace-root>/.agents/bugs.json`.
  2. Check that the bug's status is NOT resolved, fixed, closed, or obsolete (if status is `"Fix Verified"`, `"Closed"`, or `"Obsolete"`, notify the user and halt).
  3. Investigate the root cause and outline a proposed solution plan.
  4. Assign `priority` (`"P0"`, `"P1"`, `"P2"`, or `"P3"`), `impact` (`"Critical"`, `"High"`, `"Medium"`, or `"Low"`), and `risk` (`"Low"`, `"Medium"`, or `"High"`).
  5. Set `"date_triaged"` to current date (`YYYY-MM-DD`).
  6. **MANDATORY STATUS**: Update `"status"` to `"Investigated"` (do NOT set to `"Triaged"`).
  7. Present findings in conversation. Under NO circumstances execute the code fix or edit source code.

- **Without Argument (`/triage_bug`)**:
  1. Iterate through all items in `<workspace-root>/.agents/bugs.json`.
  2. Identify untriaged bugs (where `priority`, `impact`, or `risk` are empty `""`).
  3. Skip any bugs that are already resolved, fixed, closed, or obsolete.
  4. Sequentially triage each active untriaged bug: investigate root cause, assign `priority`, `impact`, `risk`, set `"date_triaged"` to current date (`YYYY-MM-DD`), and update `"status"` strictly to `"Investigated"`.
  5. Save updates to `<workspace-root>/.agents/bugs.json` and present a structured triage summary in conversation without executing fixes.
