# Spec-Driven Development (SDD) & Living Spec Maintenance Workflow

- **Positive Guardrail Framing (CRITICAL)**:
  - When writing or updating Product (BRD) or Specification (SDD) documents, express architectural constraints and operational guardrails as **positive statements of desired capability, target persona experience, and system behavior** (e.g., "1-click browser operations for non-technical maintainers", "defensive self-healing fallbacks during API disruptions") rather than negative/prohibitive rules ("Do not do X", "Never add Y").

- **3-Tier Spec Boundary Separation**:
  - **Tier 1: Product Definition / BRD (`conductor/product.md`)**: Defines the high-level business vision, target stakeholders, and foundational architectural invariants.
  - **Tier 2: Master Specification / SDD (`conductor/spec.md`)**: Defines high-level system architecture, functional modules, and clean REST/gRPC resource contracts. NEVER tightly couple the SDD to private internal method names, transient utility scripts, or rigid JSON schema permutations.
  - **Tier 3: Implementation Plans (`conductor/tracks/`)**: Holds step-by-step task breakdowns, TDD unit test plans, and refactoring steps for specific tracks.

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
