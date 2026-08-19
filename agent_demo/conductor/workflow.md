# Project Workflow & SDD Methodology

## Guiding Principles

1. **Specification-Driven Development (SDD):** All development is driven by specification documents (`conductor/spec.md` or `conductor/spec_draft.md`). Specifications precede code implementation and act as the single source of truth.
2. **The Plan is the Source of Truth:** All work must be tracked in the active track's `plan.md`.
3. **Automated Unit Testing for Large Changes Only:** Unit testing (`uv run pytest`) is required **ONLY when making large code modifications or structural changes** (e.g. multi-agent routing refactors, API endpoint additions, schema alterations). Do not over-test or write unnecessary unit tests for minor edits, prompt text tweaks, or simple styling changes.
4. **Mandatory User Manual Verification & Sign-Off:** All new features (Feature Requests / FRs) and all Medium, High, or Critical impact bugs/FRs MUST be manually verified and signed off by the user (`brendanhills`) before being marked complete in `.agents/bugs.json` or track registries.
5. **The Tech Stack is Deliberate:** Changes to the tech stack must be documented in `tech-stack.md` *before* implementation.
6. **User Experience First:** Every decision should prioritize user experience and low-latency voice streaming.
7. **Non-Interactive & CI-Aware:** Prefer non-interactive commands. Use `CI=true` for watch-mode tools to ensure single execution.

## Task Workflow

All tasks follow a strict Specification-Driven Development (SDD) lifecycle:

### Standard Task Workflow

1. **Review Specification:** Consult `conductor/spec_draft.md` or the active track `spec.md` to understand requirement bounds and acceptance criteria.
2. **Select Task:** Choose the next available task from `plan.md` in sequential order.
3. **Mark In Progress:** Before beginning work, edit `plan.md` and change the task from `[ ]` to `[~]`.
4. **Implement Code & Selective Testing:**
   - **ONLY for large or structural changes**, write corresponding unit tests in `tests/` validating acceptance criteria.
   - Run test suite: `.venv/bin/pytest`
5. **Execute Verification:**
   - Run automated tests to ensure zero regression when implementing structural changes.
   - **For New Features (FRs) and Medium+ Impact Bugs/FRs**: Present a detailed manual verification plan to the user (`brendanhills`) and await explicit manual confirmation/sign-off before changing status to `"Fix Verified"` or `"Completed"`.
6. **Commit Code & Update Plan:**
   - Stage and commit code changes with descriptive commit messages.
   - Update `plan.md` task status from `[~]` to `[x]` with commit SHA.

### Quality Gates

Before marking any task complete, verify:

- [ ] Implementation matches the authoritative Specification document (`spec_draft.md`).
- [ ] Automated unit tests pass cleanly (`.venv/bin/pytest`) for large/structural changes.
- [ ] Explicit user (`brendanhills`) manual verification sign-off obtained for all new features and Medium+ impact bugs/FRs.
- [ ] Code follows project code style guidelines (as defined in `code_styleguides/`).
- [ ] No static analysis or linting errors (`uv run ruff check`).
