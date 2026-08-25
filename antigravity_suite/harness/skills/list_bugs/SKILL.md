---
name: list_bugs
description: List registered bugs in a structured markdown table with filtering, sorting, and priority tiering.
---

# List Bugs Command (`/list_bugs`)

When the user runs `/list_bugs` (or `/list bugs`):

## 1. Determine Scope
Check if the user specified a filter in their request:
- **Type filters**: "fr" / "feature" (filter strictly for entries where `type` is `"FR"`), "bug" (filter strictly for entries where `type` is `"Bug"`).
- **Reporter filters**: "my" / "mine" (filter items where `reporter` matches the active git user or current user identity), or "reporter:<name>" / "<name>" (filter items where `reporter` matches specific name).
- **Status filters**: "all" (include all items), "resolved" (include only items with status `"Fix Verified"`, `"Closed"`, or `"Obsolete"`).
- **Default**: include active unresolved items (status is NOT `"Fix Verified"`, `"Closed"`, or `"Obsolete"`).

## 2. Verify Existence
Read and parse `<workspace-root>/.agents/bugs.json`. If no items exist in the file, or if the filter returns zero results, announce:
> "No matching items found! Workspace is clean."
and halt.

## 3. Sort and Group
Group items by status into distinct sections so outstanding items are clearly separated:
1. **Outstanding / Needs Fix or Feature Implementation** (status: `"Reported"`, `"Investigated"`, `"Fix Proposed"`)
2. **Fix Implemented / Resolved** (status: `"Fix Implemented"`, `"Fix Verified"`, `"Closed"`, `"Obsolete"`)

Within each status group, sort the items by priority: `P0` first, then `P1`, `P2`, `P3`. Within each priority tier, sort chronologically by `id` (or `date_reported`).

## 4. Format Output
When displaying items across multiple status groups (such as default or `/list_bugs all`), render **two distinct markdown tables** under explicit section headers:
- `### Outstanding / Needs Fix`
- `### Fix Implemented / Resolved`

Every table MUST include the following columns:
| Column | Description | Format / Source |
| :--- | :--- | :--- |
| **ID** | Bug identifier | `#<id>` |
| **Type** | Classification | `Bug` or `FR` |
| **Reporter** | Reporting user | e.g. `brendanhills` |
| **Priority** | Priority level | **P0**, **P1**, **P2**, **P3** |
| **Impact** | Impact severity | `Critical`, `High`, `Medium`, `Low` |
| **Status** | Lifecycle status | `Reported`, `Investigated`, `Fix Implemented`, `Fix Verified`, etc. |
| **Description** | Summary description | The description text |
| **Date Reported**| Date created | `YYYY-MM-DD` |
| **Date Resolved**| Date resolved | `YYYY-MM-DD` (for resolved table) |
