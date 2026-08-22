---
name: spec_drift
description: Audits the codebase against the Conductor Master Specification (or SDD) to detect architecture and data drift, generating a structured Discrepancy Matrix.
---

# Spec Drift Audit Command (`/spec_drift` or `/drift`)

When the user runs `/spec_drift` or `/drift` or asks to check for specification drift:

### 1. Locate Authoritative Specification & Codebase
1. Look for the project's Master Specification Document:
   - `conductor/spec.md` (or `conductor/spec_draft.md` if in drafting phase)
   - `conductor/product.md` and `conductor/tech-stack.md`
   - Alternatively, search for any designated SDD markdown file in the workspace.
2. If no specification is found, notify the user and ask for the target spec file.

### 2. Multi-Layer Discrepancy Audit
Perform a systematic comparison between the specification and the actual codebase across 4 core layers:
1. **Data Contracts & Schemas**:
   - Compare sample/production JSON, database schemas, or DTO models against the schemas documented in the spec.
   - Check for snake_case vs. camelCase mismatches, missing or extra fields, and structural differences (Arrays vs. Maps/Objects).
2. **API & Server Endpoints**:
   - Compare route handlers in `server.py` (or backend routers) against the documented REST/gRPC endpoints.
   - Flag undocumented endpoints or documented endpoints that lack implementation.
3. **UI Components & Features**:
   - Compare UI tabs, navigation bars, KPI banners, filter controls, and modals in `index.html` (or frontend components) against the Functional Requirements (FR) list.
4. **AI & Ingestion Pipelines**:
   - Check model versions, prompt templates (`prompts/`), extraction scripts (`scripts/`), and audio/TTS generators against the specification.

### 3. Generate the Discrepancy Review Matrix
Render and write the discrepancy analysis to `conductor/spec_discrepancies.md` (and display in chat/artifact):

```markdown
# Spec vs. Codebase Discrepancy Review Matrix

| ID | Domain / Component | Specification Version | Implemented Codebase Version | Recommendation | Resolution Status | User Decision / Action |
|:---|:---|:---|:---|:---|:---:|:---|
| **D-1** | `config.json` | Basic theme colors & URLs | Rich `kpiPillars` & feature toggles | **Adopt Code** (Update Spec) | 🟡 Open | *Awaiting review* |
| **D-2** | `risks.json` | snake_case fields | camelCase domain fields | **Adopt Code** (Update Spec) | 🟡 Open | *Awaiting review* |
```

### 4. Provide Triage Recommendations
For each discrepancy:
- State whether the codebase evolved intentionally (recommending a Spec update to match), or
- If code drifted unintentionally from a required architectural invariant (recommending a Code fix).
- Allow the user to decide on the resolution for each item before applying changes.
