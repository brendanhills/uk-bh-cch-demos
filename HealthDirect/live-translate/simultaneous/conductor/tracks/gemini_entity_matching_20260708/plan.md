# Plan: Contextual Clinical Entity Highlighting with Gemini NLU

## Phase 1: Backend Prompts & Configuration
- [ ] Task: Write unit tests verifying prompt compilation
  - [ ] Add tests to verify `assemble_system_instructions()` appends the Clinical Term Annotation rules correctly.
  - [ ] Verify that the glossary JSON can be structured properly as a schema prompt.
- [ ] Task: Implement passive prompt constraints
  - [ ] Modify `demo/web_server.py` to include the annotation instructions in system instructions.
  - [ ] Run backend tests and verify they compile without errors.

## Phase 2: Frontend Parsing & Interactive UI Rendering
- [ ] Task: Write frontend tests for XML tag parsing
  - [ ] Write unit/integration tests verifying `applyGeminiHTMLHighlight()` correctly parses XML-like tags.
  - [ ] Verify that mismatched or unclosed tags are gracefully stripped without breaking the UI.
- [ ] Task: Implement client-side parser
  - [ ] Modify `demo/web/main.js` to replace the regex-based `applyHTMLHighlight` with `applyGeminiHTMLHighlight` DOM-based tag parsing.
  - [ ] Ensure click events, hover tooltips, and sidebar persistent references are correctly wired to the newly rendered highlighted tags.

## Phase 3: Validation & Verification
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
