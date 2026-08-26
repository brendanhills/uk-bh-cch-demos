# Spec Drift Guardrails & Verification Standards

## Objective
Ensure code evolution remains strictly aligned with authoritative specifications (`conductor/spec.md`, SDD documents, and frontmatter-declared specs `*spec.md`), preventing silent architecture and API drift.

## Multi-Layer Verification
When reviewing changes or performing drift audits:
1. **Data Contracts & Schemas**: Verify field naming (camelCase vs snake_case), optionality, and structure against the schema specifications.
2. **API & Endpoints**: Check that route paths, HTTP methods, and status codes match documented endpoint contracts.
3. **UI Components & Features**: Ensure UI tabs, actions, and KPI pillars match functional requirements.
4. **AI & Pipeline Configs**: Verify model parameters, prompts, and extraction flows against the specification.
