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
Sort the filtered bugs by priority: `P0` first, then `P1`, `P2`, `P3`. Within each priority tier, sort chronologically by `id` (or `date_reported`).

## 4. Format Output
Render a clear, structured markdown table. For each bug, display:
- **ID**: `#<id>`
- **Priority**: Bolded (e.g. **P0**, **P1**)
- **Impact**: e.g., Critical, High
- **Status**: e.g., New, Investigating, Fix Implemented
- **Description**: The summary description
- **Date**: Format as `YYYY-MM-DD` (if available)
