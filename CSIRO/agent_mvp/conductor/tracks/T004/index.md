# Track T004: ADK Framework (Code-Based Agent in ADK Web Tool)

## Status
- **Status:** ⏳ TODO
- **Owner:** CSIRO Software Development Team

## Objectives
Enhance and finalize the local codebase-level **Python ADK Agent** (`agent.py`) so it runs seamlessly as an independent service and can be directly loaded, debugged, and visualized using the native **ADK Web companion tool** (`adk web`).

## Implementation details
1. **Tool Integration:**
   - Implement `fetch_github_diff` and `lookup_exceptions_registry` as registered `FunctionTool` objects.
   - Ground the agent's system prompt with line-by-line SSDS rules and waiver matching logic.
2. **Native Dev Tool Support:**
   - Configure the agent definition so running `uv run adk web .` from the `agents/security-agent` directory boots up the native GUI to chat, trace tool calls, and test the compliance audits.
3. **Dual-Mode FastAPI (Simultaneous Support):**
   - Provide REST API endpoints in the python setup that correspond to the OpenAPI specifications of Track T003. This lets you serve the tools locally to test both your Agent Builder console setup AND your ADK setup!

## Checklist
- [ ] Implement the `lookup_exceptions_registry` `FunctionTool` in python.
- [ ] Expand `agents/code-compliance-agent/agent.py` to match waivers with detected SSDS violations.
- [ ] Implement dual-mode FastAPI wrapper inside `agents/code-compliance-agent` supporting:
  - `/run` (ADK endpoint for Enterprise Portal).
  - `/api/github/diff` (REST endpoint for Agent Builder).
  - `/api/security/exceptions` (REST endpoint for Agent Builder).
- [ ] Add `fastapi` and `uvicorn` to python dependencies.
- [ ] Test local execution via `adk web .`.
