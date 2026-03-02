# Re-Architecture Implementation Plan

## Goal
Restructure the project into 3 distinct components (`external_services`, `loan_agent`, `demo_frontend`).
Implement **Real ID** data handling, **DLP Security**, **Paystub Upload**, **Model Fallback**, **MCP-Lite Pattern**, and **Continuous UAT**.

## User Review Required
> [!IMPORTANT]
> **Architecture Split**: Code moves to `external_services`, `loan_agent`, `demo_frontend`.
> **Data Handling**: Strict "Gov ID" required.
> **Security**: DLP sanitizes PII in logs.
> **Multimodal**: Users can upload Paystub PDFs/Images for income verification.
> **Model**: ALWAYS uses Gemini 3.1. Flash for orchestration, Pro with **Thinking: HIGH** for policy and underwriting.
> **MCP-Lite**: Tools are called via a central Dispatcher (mocking MCP).
> **UAT**: A `docs/UAT_CHECKLIST.md` will be created to map code features to `demo_task.txt` requirements.

## Proposed Changes

### 1. Directory Restructuring
#### [NEW] `external_services/`
- `data/`, `confluence/`, `credit_bureau.py`, `employment_registry.py`.

#### [NEW] `loan_agent/`
- `agent.py`, `sub_agents/`.
- `tools/`: **Refactored** to use the new Dispatcher pattern.
- `utils/dlp_guardian.py`: PII redaction.
- `utils/tool_dispatcher.py`: **New** MCP-Lite Registry & Router.

#### [NEW] `demo_frontend/`
- `app.py`: Streamlit UI.
- **New Feature**: File Uploader widget.

### 2. "Real ID" Implementation
- `external_services/data/applicants.json`: Use Gov IDs.

### 3. MCP-Lite Tool Pattern
- `loan_agent/utils/tool_dispatcher.py` handles `call_tool(name, args)`.

### 4. Security (DLP)
- implement `inspect_and_mask(text)` for logs.

### 5. Paystub Verification (Multimodal)
- **Frontend**: Add file uploader.
- **Agent**: Use `doc_analyzer.py` extract income.

### 6. Continuous UAT
#### [NEW] `docs/UAT_CHECKLIST.md`
- **Purpose**: A living document mapping `demo_task.txt` reqs to verification steps.
- **Content**:
    - [ ] Req 1: Parallel API Calls -> Verify logs show async execution.
    - [ ] Req 4: Auto-approve < 5 mins -> Verify "Sarah Speed" case.
    - [ ] Req 39: Rate Limits -> Verify `external_services` simulation.
- **Workflow**: We will check off items in this file as we build/verify phases.

## Verification Plan
1.  **DLP Test**: Verify SSN masking.
2.  **Dispatcher Test**: Verify `call_tool("get_credit_report")` works.
3.  **End-to-End**: Run full flow with all features.
4.  **UAT Run**: Walk through `docs/UAT_CHECKLIST.md` manually.
