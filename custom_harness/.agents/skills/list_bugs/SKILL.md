---
name: list_bugs
description: List registered bugs in a structured markdown table with filtering, sorting, and priority tiering.
---

# List Bugs Command (`/list_bugs`)

When the user runs `/list_bugs` (or `/list bugs`):

## 1. Determine Scope
Check if the user specified a scope in their request (e.g., "all" or "resolved"):
- If "all", include all bugs.
- If "resolved", include only bugs with status `"Fix Verified"`, `"Closed"`, or `"Obsolete"`.
- Otherwise (default), include only active unresolved bugs (status is NOT `"Fix Verified"`, `"Closed"`, or `"Obsolete"`).

## 2. Verify Existence
Read and parse `.agents/bugs.json`. If no bugs exist in the file, or if the filter returns zero results, announce:
> "No matching bugs found! Workspace is completely clean."
and halt.

## 3. Sort and Group
Group bugs by status into distinct sections so outstanding bugs are clearly separated:
1. **Outstanding / Needs Fix** (status: `"Reported"`, `"Investigated"`, `"Fix Proposed"`)
2. **Fix Implemented / Resolved** (status: `"Fix Implemented"`, `"Fix Verified"`, `"Closed"`, `"Obsolete"`)

Within each status group, sort the bugs by priority: `P0` first, then `P1`, `P2`, `P3`. Within each priority tier, sort chronologically by `id` (or `date_reported`).

## 4. Format Output
Render clear, structured markdown tables for each status group (or sub-tables under distinct section headers). For each bug, display:
- **ID**: `#<id>`
- **Priority**: Bolded (e.g. **P0**, **P1**)
- **Impact**: e.g., Critical, High
- **Status**: e.g., New, Investigated, Fix Implemented
- **Description**: The summary description
- **Date**: Format as `YYYY-MM-DD` (if available)
