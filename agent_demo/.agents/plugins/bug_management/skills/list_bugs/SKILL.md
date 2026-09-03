---
name: list_bugs
description: List registered bugs in a structured markdown table with filtering, sorting, and priority tiering.
---

# List Bugs Command (`/list_bugs`)

When the user runs `/list_bugs` (or `/list bugs`):

## 1. Determine Scope
Check if the user specified a filter in their request:
- Type filters: "fr" / "feature" (show only Feature Requests), "bug" (show only Bugs).
- Status filters: "all" (include all items), "resolved" (include only items with status `"Fix Verified"`, `"Closed"`, or `"Obsolete"`).
- Default: include active unresolved items (status is NOT `"Fix Verified"`, `"Closed"`, or `"Obsolete"`).

## 2. Verify Existence
Read and parse `.agents/bugs.json`. If no items exist in the file, or if the filter returns zero results, announce:
> "No matching items found! Workspace is clean."
and halt.

## 3. Sort and Group
Group items by status into distinct sections so outstanding items are clearly separated:
1. **Outstanding / Needs Fix or Feature Implementation** (status: `"Reported"`, `"Investigated"`, `"Fix Proposed"`)
2. **Fix Implemented / Resolved** (status: `"Fix Implemented"`, `"Fix Verified"`, `"Closed"`, `"Obsolete"`)

Within each status group, sort the items by priority: `P0` first, then `P1`, `P2`, `P3`. Within each priority tier, sort chronologically by `id` (or `date_reported`).

## 4. Format Output
Render clear, structured markdown tables for each status group (or sub-tables under distinct section headers). For each item, display:
- **ID**: `#<id>`
- **Type**: `Bug` or `FR`
- **Priority**: Bolded (e.g. **P0**, **P1**)
- **Impact**: e.g., Critical, High
- **Status**: e.g., New, Investigated, Fix Implemented
- **Description**: The summary description
- **Date**: Format as `YYYY-MM-DD` (if available)
