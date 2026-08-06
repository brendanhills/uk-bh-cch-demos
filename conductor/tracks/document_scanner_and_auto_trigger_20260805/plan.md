# Implementation Plan: Document Scanner & Agentic Auto-Trigger (#BUG-42 & #BUG-48)

## Phase 1: Custom ADK Tool & Agent System Instruction Update
- [ ] Task: Define `request_document_scan(document_type, prompt_reason)` ADK tool in `app/google_search_agent/agent.py`
- [ ] Task: Update system instruction procedures in `agent.py` to enforce calling `request_document_scan` during clinical document workflow steps
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Frontend WebSocket Tool Handler & Guided Viewfinder UI
- [ ] Task: Add `functionCall` event listener for `request_document_scan` in `app/static/js/app.js` to auto-open camera viewfinder
- [ ] Task: Finalize hands-free Space bar / Enter photo capture and privacy camera hardware auto-power-off in `app.js`
- [ ] Task: Verify Chrome-style window control header UI in `index.html` and `style.css`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Verification & Integration Testing
- [ ] Task: Run automated regression suite (`uv run pytest`)
- [ ] Task: Manual end-to-end verification on `http://127.0.0.1:8000`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
