# Specification-Driven Development (SDD) & Workflow Enforcement

All AI coding agents working in this repository MUST strictly adhere to the following Specification-Driven Development (SDD) and task verification rules:

1. **Specification First (SDD Principle)**:
   - Before writing or modifying application code for any feature, tool, API, or architecture change, inspect `conductor/spec.md`.
   - All proposed structural changes must be specified and aligned with the Master Specification before implementation. The specification is the authoritative blueprint.

2. **Clean Spec Invariant**:
   - `conductor/spec.md` MUST remain clean and forward-looking. Do NOT clutter `spec.md` with historical bug tags (`#BUG-xx`), past iteration track logs, or workflow process rules. Keep discrepancy matrices in `conductor/spec_discrepancies.md`, track history in `conductor/tracks.md`, and workflow rules in `conductor/workflow.md`.

3. **Automated Unit Testing Policy (Large Changes ONLY)**:
   - Agents MUST write and execute `.venv/bin/pytest` **ONLY when making large code modifications, major refactors, or structural additions** (e.g. altering multi-agent router delegation, adding new REST endpoints, or changing state schemas).
   - **DO NOT OVER-TEST**: Do not write redundant unit tests or run heavy test suites for minor text tweaks, prompt instruction edits, or simple UI layout adjustments.

4. **Mandatory User Manual Verification & Sign-Off Gate**:
   - All new features (Feature Requests / FRs) and all bugs or feature requests categorized with **Medium**, **High**, or **Critical** impact MUST be **manually verified and signed off by Brendan Hills (`brendanhills`)** before their status can be recorded as `"Fix Verified"` or `"Completed"` in `.agents/bugs.json` or Conductor track registries.
   - Passing automated tests alone does NOT grant permission to mark Medium/High/Critical items as complete. You MUST present a step-by-step manual verification plan to the user and receive explicit confirmation.

5. **Gemini 3+ Model & Prompting Policy**:
   - Flash models older than Gemini 3 are forbidden. Use `gemini-3.1-flash-live-preview` for BIDI Live streaming and `gemini-3-flash` for unary sub-agents.
   - Use Hybrid Markdown formatting inside semantic XML boundary tags (`<persona>`, `<role>`, `<instructions>`).
