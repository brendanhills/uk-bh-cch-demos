# Spec-Driven Development (SDD) & Living Spec Maintenance Workflow

- **Draft-First Specification Workflow**:
  - When creating, updating, or overhauling system specifications, design documents, or Conductor architecture definitions, ALWAYS create a draft specification file first (e.g. `conductor/spec_draft.md`).
  - Present the draft for user comparison, diffing, and manual review. Temporary discrepancy matrices/triage tables are strictly for review purposes and MUST be stripped before promoting to the authoritative SDD (`conductor/spec.md`).
  - NEVER overwrite or replace the active master specification (`conductor/spec.md` or `conductor/product.md`) until the user has explicitly reviewed and approved the draft.

- **Living Spec Synchronization Barrier**:
  - Conductor serves as the single source of truth for high-level product vision (`conductor/product.md`), technical invariants (`conductor/tech-stack.md`), and the Master System Specification (`conductor/spec.md`).
  - When Conductor tracks (`conductor/tracks/`) or major bug fixes are completed, review and update the Master Specification to guarantee 100% alignment between code and documentation.

- **Conductor & Bug Management Roles**:
  - **Conductor**: Master Specification Document, Architecture Standards, and Feature Track Planning (`conductor/tracks/`).
  - **`.agents/bugs.json`**: Operational Defect Tracking. All bug fixes MUST begin with an automated reproduction unit test before code changes are applied.
