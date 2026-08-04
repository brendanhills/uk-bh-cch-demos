# Specification: Glossary Translation Highlighting (Track: `highlight_glossary_20260630`)

## Overview
This track introduces real-time, high-contrast visual highlighting of clinical glossary terms within both the CLI and Web UIs of the Bilingual Medical Interpreter. When an English clinical term or its foreign-language translation from the HealthDirect clinical glossary is detected in either speech input (original) or translation output (translation), it will be highlighted dynamically to draw the user's attention to verified terminology.

## Functional Requirements
1. **Glossary Access & API Endpoint**:
   - Add a GET `/api/glossary` endpoint to the root `web_server.py` that loads `dictionary/glossary.json` and serves the glossary terms (with optional language filtering) to the frontend.
2. **Terminal CLI Highlight (`live_translate_demo.py`)**:
   - Load `dictionary/glossary.json` and perform case-insensitive, word-boundary-aware search matching on completed turns.
   - Bold and color-code matched terms in the double-column console display:
     - Highlight English medical terms in **bold green**.
     - Highlight target language medical terms in **bold magenta**.
3. **Web UI Highlight (`web/main.js` & `web/style.css`)**:
   - Fetch the active glossary on preset change/initial connection.
   - When a speech turn is completed (`turn_complete`), sanitize the accumulated text and replace glossary terms with marked HTML structures: `<mark class="glossary-highlight" title="[Glossary Definition/Translation]">[Term]</mark>`.
   - Provide premium, glowing CSS styles with subtle micro-animations for `.glossary-highlight` in `web/style.css`.
4. **Boundary-Aware Term Matching**:
   - Match terms case-insensitively using regex boundaries or safe text-matching algorithms to avoid matching partial substrings of larger words (e.g., matching "ear" in "hearing").

## Non-Functional Requirements
- **Performance**: Highlighting must not degrade terminal rendering speeds or stutter real-time WebSocket communication.
- **UI Pacing**: Apply highlighting only on completed speech turns (`turn_complete`) to avoid broken HTML rendering during incremental, real-time streaming segments.

## Acceptance Criteria
- [ ] Glossary terms are highlighted in the CLI double-column console on turn completion.
- [ ] Glossary terms are highlighted in the Web UI speech bubbles on turn completion.
- [ ] English clinical terms (original/translation) are highlighted in green.
- [ ] Foreign target language terms (original/translation) are highlighted in magenta/distinct color.
- [ ] Hovering over highlighted terms in the Web UI displays the matching glossary definition as a tooltip.
- [ ] Substring false-positives (e.g., "ear" in "bear") are not matched.
- [ ] Automated tests verify the term-matching regex and rendering safety.
