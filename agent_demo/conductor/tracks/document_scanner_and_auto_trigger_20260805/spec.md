# Specification: Document Scanner & Agentic Auto-Trigger (#BUG-42 & #BUG-48)

## Dependencies
- **Depends on Track**: [`adk2_multi_agent_workflow_20260806`](../adk2_multi_agent_workflow_20260806/index.md) (ADK 2.0 Multi-Agent Concierge Workflow). The `request_document_scan` tool will be added directly to the `document_scanner` sub-agent.

## Functional Requirements
1. **Guided Viewfinder UI (#BUG-42)**:
   - Provide a clean A4 portrait scanning guide overlay (`Align document inside box`).
   - Hands-Free Presenter Shortcut: Pressing **Space bar** or **Enter key** while the document camera is open captures the photo instantly with a shutter chime.
   - Privacy Auto-Power-Off: Snapping a photo immediately stops camera media tracks (`track.stop()`) and powers down camera hardware.
   - Chrome Window Style Header: Display a Chrome window titlebar with `📷 Document Scanner` title, `🗖` orientation toggle, and top-right `✕` close button.

2. **Agentic Tool-Driven Auto-Camera Trigger (#BUG-48)**:
   - Define a custom ADK tool `request_document_scan(document_type, prompt_reason)` in `app/cch_agent/agent.py`.
   - Update system instruction procedures so Jennie invokes `request_document_scan` whenever a procedure workflow step requires a clinical document (discharge papers, prescriptions, lab results).
   - In `app/static/js/app.js`, listen for the `request_document_scan` function call event and automatically open the camera viewfinder.

3. **Dynamic Attachment Badging**:
   - Attachment badges default to `📄 Document Attached` upon capture, and dynamically update to match recognized document headings (e.g. `📄 Document Attached - Discharge Summary`, `📄 Document Attached - Patient & Admission Overview`).

## Non-Functional Requirements
- **Performance**: Zero CPU canvas frame sampling overhead.
- **Reliability**: 100% deterministic operation across all webcams, indoor lighting conditions, white background walls, and paper angles.

## Acceptance Criteria
- Pressing Space bar or Enter when camera is active snaps and sends the document photo.
- When Jennie prompts for a document in the workflow, the camera viewfinder opens automatically via ADK tool call.
- Snapping a photo powers off camera hardware immediately.
