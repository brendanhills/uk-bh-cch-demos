---
name: spec_drift
description: Detects discrepancies between code changes and specifications (using frontmatter specs, spec mappings, or workspace design docs). Classifies severity, provides triage recommendations (Adopt Code vs Fix Code), and generates ready-to-apply spec patch diffs.
---

# Specification Drift Detection (`/spec_drift` or `/drift`)

When the user runs `/spec_drift` (or `/drift`) or asks to audit code against specifications:

## Overview

This skill detects when code changes drift from their specifications using a fast, two-pass decoupled approach:

1. **Pass 1 (Filtering & Discovery)**: Uses `drift_detector.py` to identify candidate specifications via:
   - **Frontmatter Declarations**: Markdown files matching `*spec.md` with `files: [...]` YAML frontmatter.
   - **Mapping Configs**: Static mappings defined in `spec_mappings.json` (if present).
   - **Workspace Design Documents**: Standard workspace architecture documents (e.g., `conductor/spec.md`, `docs/spec.md`, `SDD.md`) when broad architecture changes occur.
2. **Pass 2 (Divergence & Triage Evaluation)**: Compares the diff against the specification contracts across 3 core layers:
   - **Data Contracts & Schemas**: Field types, naming conventions, extra/missing fields.
   - **API & Interface Signatures**: Route signatures, parameters, return types, error contracts.
   - **Behavioral Invariants & Constraints**: Threshold limits, permitted bounds, thread-safety, validation rules.

---

## Instructions

### Step 1: Identify Modified Files & Diffs

1. **Target Files**:
   - If the prompt specifies files (e.g. `check spec drift for src/auth/token.py`), target those files.
   - Otherwise, detect modified/staged files via git (`git status --porcelain` or `git diff --name-only HEAD`).
   - If no modified files are found and no specific file is provided, scan workspace specs against corresponding implementations.
2. **Generate Diffs**:
   - Retrieve the unified diff using `git diff HEAD` (or staged diff `git diff --cached`).

### Step 2: Pass 1 — Relevance Filtering

Run the drift detector filtering script:
```bash
python3 <skill_path>/scripts/drift_detector.py --modified_files="<comma_separated_files>" --scan_specs
```

- **Exit Code 3 / Empty Array**: If no candidate specifications match the modified files, report `NO_DRIFT` (no mapped specs affected) and end the turn.
- **Exit Code 0**: Candidate specs matched. Proceed to Pass 2.
- **Exit Code 1**: Handle configuration/path error.

### Step 3: Pass 2 — Divergence, Severity & Triage Analysis

For each matched specification:
1. Read the specification content using `view_file`.
2. Compare the code diff against the specification clauses.
3. Determine the verdict:
   - **`NO_DRIFT`**: The code change aligns with the spec (e.g., within permitted value ranges, refactoring, comments, formatting, logging, bug fixes that restore spec compliance).
   - **`DRIFT`**: The code change introduces new behavior, alters contracts, or violates invariants documented in the spec.

For any detected **`DRIFT`**:
- **Severity Rating**:
  - `CRITICAL`: Breaking API/contract change, removed invariant/lock, security/boundary violation.
  - `WARNING`: Behavioral modification, altered constant, modified parameter or schema field.
  - `INFORMATIONAL`: Minor documentation discrepancy or wording misalignment.
- **Triage Recommendation**:
  - **`Adopt Code (Update Spec)`**: The code evolved intentionally; the specification should be updated to reflect the new behavior.
  - **`Fix Code (Violation)`**: The code change unintentionally broke a required architectural contract; the code should be fixed.
- **Suggested Spec Patch**:
  - Provide a clean markdown unified diff (```diff ... ```) showing the exact proposed update to the specification.

### Step 4: Output Structured Report

Render the findings in a clear, formatted summary:

#### If Drift is Detected:

> ### ⚠️ Specification Drift Detected
>
> | Spec | Matched Files | Severity | Section | Triage Recommendation |
> | :--- | :--- | :---: | :--- | :--- |
> | [`auth_spec.md`](file:///path/to/auth_spec.md) | `src/auth/token.py` | `CRITICAL` | `## Token Expiry` | **Adopt Code** (Update Spec) |
>
> **Reason**: Default token expiry duration was modified from 3600s to 86400s.
>
> **Suggested Spec Patch**:
> ```diff
> - Tokens expire after 3600 seconds (1 hour).
> + Tokens expire after 86400 seconds (24 hours).
> ```

#### If No Drift is Detected:
Summarize concisely:
> ✅ **No Specification Drift**: The modified files do not conflict with any mapped specifications or contract invariants.
