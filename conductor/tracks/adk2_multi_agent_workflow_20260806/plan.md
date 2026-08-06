# Implementation Plan - ADK 2.0 Multi-Agent Concierge Workflow

## Phase 1: ADK 2.0 Sub-Agent Architecture & Routing (`app/cch_agent/`)
- [x] Task: Create sub-agent modules in `app/cch_agent/sub_agents/`: `patient_verifier.py`, `document_scanner.py`, `visit_scheduler.py`, and `soap_generator.py` (#BUG-43)
- [x] Task: Configure root `cch_concierge_router` agent in `app/cch_agent/agent.py` equipped with sub-agent delegation tools (#BUG-43)
- [x] Task: Add Australian phone number validation rules to `patient_verifier` sub-agent instruction (#BUG-46)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Document Snapshot Attachment Persistence (`#BUG-45`)
- [ ] Task: Update WebSocket image upload handler in `app/main.py` to persist incoming base64 document frames to `app/logs/attachments/<session_id>_<timestamp>.jpg` (#BUG-45)
- [ ] Task: Log saved attachment file paths in `app/logs/transcripts/call_transcripts.log` (#BUG-45)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Backend SOAP Endpoint & Google Search Grounding (#BUG-23 & #BUG-25)
- [ ] Task: Implement FastAPI endpoint `@app.post("/api/session/soap_note")` in `app/main.py` using `soap_generator` sub-agent (#BUG-23)
- [ ] Task: Integrate `google_search` tool into agent tools list (#BUG-25)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Frontend SOAP Export Modal & UI Clean-Up (#BUG-23)
- [ ] Task: Add `#soapNoteButton` (`📄 SOAP Note`) and `#soapModal` dialog structure in `app/static/index.html` (#BUG-23)
- [ ] Task: Add CSS styles for `.soap-modal`, `.soap-doc-paper`, and print formatting in `app/static/css/style.css` (#BUG-23)
- [ ] Task: Implement `#soapNoteButton` click handler, `/api/session/soap_note` fetch, clipboard copy, and print handlers in `app/static/js/app.js` (#BUG-23)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 5: Automated Testing & Verification
- [ ] Task: Write unit tests for sub-agent routing, Australian phone number parsing, attachment saving, and SOAP endpoint in `tests/`
- [ ] Task: Run full test suite (`uv run python -m pytest`) and verify clean pass
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
