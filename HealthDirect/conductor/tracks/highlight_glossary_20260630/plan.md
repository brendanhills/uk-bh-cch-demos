# Implementation Plan: Glossary Translation Highlighting (Track: `highlight_glossary_20260630`)

## Phase 1: API Endpoint & Highlight Engine [checkpoint: f880560]
- [x] Task: Setup & Test Foundations b1e3f1c
    - [x] Write failing unit tests in `tests/test_web_server.py` (or equivalent) for the new GET `/api/glossary` endpoint.
    - [x] Write failing unit tests in `tests/test_highlighter.py` verifying boundary-safe regex matching and ANSI-color substitution.
- [x] Task: Implement GET `/api/glossary` b1e3f1c
    - [x] Add `/api/glossary` endpoint to `web_server.py` that loads and returns data from `dictionary/glossary.json`.
- [x] Task: Implement Highlighter Backend Engine b1e3f1c
    - [x] Create `glossary_highlighter.py` to contain backend match and highlight logic using compiled patterns with word boundaries.
    - [x] Run the test suite to verify green state and assert >80% coverage for the new module.
- [x] Task: Conductor - User Manual Verification 'Phase 1: API Endpoint & Highlight Engine' (Protocol in workflow.md)



## Phase 2: Terminal CLI Highlight Integration
- [ ] Task: Integration & CLI Testing
    - [ ] Write failing integration tests for `live_translate_demo.py` ensuring ANSI highlighted terms are produced in terminal outputs.
- [ ] Task: Inject Term Highlighting into CLI Demo
    - [ ] Integrate the backend highlighter engine into `live_translate_demo.py` to process and highlight text outputs upon turn completion.
    - [ ] Run the tests and verify that the Terminal UI displays green and magenta highlights for matched terms.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Terminal CLI Highlight Integration' (Protocol in workflow.md)

## Phase 3: Web UI Highlighting & Style Polish
- [ ] Task: Fetch Glossary in Frontend
    - [ ] Modify `web/main.js` to fetch glossary terms from `/api/glossary` when a preset is loaded or session is established.
- [ ] Task: Web UI Replacement Logic
    - [ ] Implement a safe JS-based regex replacer in `web/main.js` that scans completed original and translation segments.
    - [ ] Inject `<mark class="glossary-highlight">` tags around matched terms without breaking standard HTML structures.
- [ ] Task: Premium Visual Styles & Effects
    - [ ] Add rules for `.glossary-highlight` in `web/style.css` featuring a professional colored badge/glow style, a tooltip for definitions, and soft hover transitions.
    - [ ] Run manual verification in a local browser session to verify alignment and aesthetics.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Web UI Highlighting & Style Polish' (Protocol in workflow.md)
