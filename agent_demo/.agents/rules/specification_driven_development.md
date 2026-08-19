# Specification-Driven Development (SDD) & Workflow Enforcement

All AI coding agents working in this repository MUST strictly adhere to the following Specification-Driven Development (SDD) and task verification rules:

1. **Specification First (SDD Principle)**:
   - Before writing or modifying application code for any feature, tool, API, or architecture change, inspect `conductor/spec.md` (or the active track's `spec.md`).
   - All proposed structural changes must be specified and aligned with the Master Specification before implementation. The specification is the authoritative blueprint.

2. **Automated Unit Testing Policy (Large Changes Only)**:
   - Agents MUST write and execute `.venv/bin/pytest` **ONLY when making large code modifications, major refactors, or structural additions** (e.g. altering multi-agent router delegation, adding new REST endpoints, or changing state schemas).
   - **DO NOT OVER-TEST**: Do not write redundant unit tests or run heavy test suites for minor text tweaks, prompt instruction edits, or simple UI layout adjustments.

3. **Mandatory User Manual Verification & Sign-Off Gate**:
   - All new features (Feature Requests / FRs) and all bugs or feature requests categorized with **Medium**, **High**, or **Critical** impact MUST be **manually verified and signed off by Brendan Hills (`brendanhills`)** before their status can be recorded as `"Fix Verified"` or `"Completed"` in `.agents/bugs.json` or Conductor track registries.
   - Passing automated tests alone does NOT grant permission to mark Medium/High/Critical items as complete. You MUST present a step-by-step manual verification plan to the user and receive explicit confirmation.

4. **Reference `conductor/workflow.md`**:
   - For task planning, git note summaries, commit message formatting, and checkpointing steps, follow `conductor/workflow.md`.
