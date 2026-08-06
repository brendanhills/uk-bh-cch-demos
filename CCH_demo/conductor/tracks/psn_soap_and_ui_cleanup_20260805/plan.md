# Implementation Plan - Clinical SOAP Note Export & UI Clean-Up (PSN Demo)

## Phase 1: Backend SOAP Endpoint & Hindi ASR Configuration
- [ ] Task: Add Hindi (`hi`) language hint to `AudioTranscriptionConfig` in `app/main.py` (#BUG-40)
- [ ] Task: Implement FastAPI endpoint `@app.post("/api/session/soap_note")` in `app/main.py` (#BUG-23)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Frontend SOAP Modal & Header UI Clean-Up
- [ ] Task: Remove `#proactivityCheckbox` and `#affectiveDialogCheckbox` from `app/static/index.html` and clean up `app/static/js/app.js` event listeners (#BUG-35)
- [ ] Task: Add `#soapNoteButton` (`📄 SOAP Note`) to `.input-wrapper` in `app/static/index.html` and add `#soapModal` overlay structure (#BUG-23)
- [ ] Task: Add CSS styles for `.soap-modal`, `.soap-doc-paper`, and `@media print` in `app/static/css/style.css` (#BUG-23)
- [ ] Task: Implement `#soapNoteButton` click handler, `/api/session/soap_note` fetch, clipboard copy, and print handlers in `app/static/js/app.js` (#BUG-23)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Automated Testing & Verification
- [ ] Task: Write unit tests in `tests/test_soap_endpoint.py` verifying `/api/session/soap_note` response structure and Hindi ASR hints in `tests/test_transcription_config.py`
- [ ] Task: Run automated test suite (`pytest`) and verify clean pass
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
