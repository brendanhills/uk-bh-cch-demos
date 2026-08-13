# Implementation Plan - ADK 2.0 Multi-Agent Concierge Workflow

## Phase 1: ADK 2.0 Sub-Agent Architecture & Routing (`app/cch_agent/`)
- [x] Task: Create sub-agent modules in `app/cch_agent/sub_agents/`: `patient_verifier.py`, `document_scanner.py`, `visit_scheduler.py`, and `soap_generator.py` (#BUG-43)
- [x] Task: Configure root `cch_concierge_router` agent in `app/cch_agent/agent.py` equipped with sub-agent delegation tools (#BUG-43)
- [x] Task: Add Australian phone number validation rules to `patient_verifier` sub-agent instruction (#BUG-46)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Sub-Agent Delegation Telemetry, Diagnosis & Latency Optimization
- [x] Task: Instrument sub-agent dispatch and tool execution with high-precision timestamp logging (`time.perf_counter()`) to measure delegation lag during Live WebSocket streaming sessions
- [x] Task: Benchmark sub-agent invocations, analyze log evidence, and diagnose the root cause of sub-agent delegation latency
- [x] Task: Propose and implement targeted fix/optimization (e.g., prompt/instruction tuning, tool invocation shortcuts, or runner delegation optimizations) to achieve target sub-agent call latency (≤ 0.5s / 500ms)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Document Snapshot Attachment Persistence & Scanner Auto-Trigger (#BUG-42, #BUG-45, #BUG-48)
- [x] Task: Update WebSocket image upload handler in `app/main.py` to persist incoming base64 document frames to `app/logs/attachments/<session_id>_<timestamp>.jpg` (#BUG-45)
- [x] Task: Log saved attachment file paths in `app/logs/transcripts/call_transcripts.log` (#BUG-45)
- [x] Task: Define `request_document_scan(document_type, prompt_reason)` ADK tool in `document_scanner` sub-agent and system instructions (#BUG-48)
- [x] Task: Add `functionCall` event listener for `request_document_scan` in `app/static/js/app.js` to auto-open camera viewfinder (#BUG-48)
- [x] Task: Finalize hands-free Space bar / Enter photo capture and privacy camera hardware auto-power-off in `app/static/js/app.js` (#BUG-42)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Backend SOAP Endpoint & Google Search Grounding (#BUG-23 & #BUG-25)
- [x] Task: Implement FastAPI endpoint `@app.post("/api/session/soap_note")` in `app/main.py` using `soap_generator` sub-agent (#BUG-23)
- [x] Task: Integrate `google_search` tool into agent tools list (#BUG-25)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 5: Frontend SOAP Export Modal & UI Clean-Up (#BUG-23)
- [x] Task: Add `#soapNoteButton` (`📄 SOAP Note`) and `#soapModal` dialog structure in `app/static/index.html` (#BUG-23)
- [x] Task: Add CSS styles for `.soap-modal`, `.soap-doc-paper`, and print formatting in `app/static/css/style.css` (#BUG-23)
- [x] Task: Implement `#soapNoteButton` click handler, `/api/session/soap_note` fetch, clipboard copy, and print handlers in `app/static/js/app.js` (#BUG-23)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 6: Automated Testing & Verification
- [x] Task: Write unit tests for sub-agent routing, Australian phone number parsing, attachment saving, telemetry, and SOAP endpoint in `tests/`
- [x] Task: Run full test suite (`uv run python -m pytest`) and verify clean pass
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)
