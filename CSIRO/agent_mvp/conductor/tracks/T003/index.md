# Track T003: Agent Builder (Low-Code Playbook Version)

## Status
- **Status:** 🔄 IN_PROGRESS
- **Owner:** CSIRO Systems Architecture Team

## Objectives
Design and specify the architecture for a low-code **Generative Playbook Agent** inside Google Cloud Vertex AI Agent Builder. The agent coordinates multiple tool actions and retrieves policy guidance from grounded Enterprise Data Stores.

## Key Components & Specifications
1. **Playbook Flow Design:**
   - Define bullet-point structured objectives and step sequences following Vertex AI Playbooks format.
   - Enforce standard multi-tool orchestration (`Get_Repository_Diff` and `Lookup_Exceptions_Registry`).
2. **OpenAPI 3.0 Tool Specifications:**
   - Design valid OpenAPI 3.0 YAML files to expose local or remote services.
   - Map query parameters and JSON schema payloads for:
     - `/api/github/diff`: fetch pull request modifications.
     - `/api/security/exceptions`: fetch active TDA compliance waivers.
3. **Data Store Grounding:**
   - Specify ingestion formats (`.md` or `.pdf`) to ground the agent's policy evaluations directly in the CSIRO SSDS document, preventing LLM hallucinations.

## Checklist
- [x] Create valid OpenAPI YAML spec for `Get_Repository_Diff` (`get_repository_diff_spec.yaml`).
- [x] Create valid OpenAPI YAML spec for `Lookup_Exceptions_Registry` (`lookup_exceptions_spec.yaml`).
- [x] Write playbook structured system goals and execution steps.
- [x] Create copy-pasteable playbook integration file `agents/code-compliance-agent/version_2_agent_builder_playbook.md`.
