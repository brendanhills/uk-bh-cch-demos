# Implementation Plan: Arabic Demo Language & RTL Layout (Track: `arabic_demo_20260701`)

## Phase 1: Pipeline & Glossary Support
- [x] **Task 1.1: Update `import_glossary.py` for Arabic translations** 8117004
  - Add `ar` target language code mapping.
  - Integrate Arabic translation pipeline inside `pre_translate_terms`.
- [ ] **Task 1.2: Run import pipeline to populate glossary**
  - Execute `uv run import_glossary.py` to translate existing medical terms to Arabic in `dictionary/glossary.json`.
- [ ] **Task 1.3: Seed and verify matching clinical terms for the asthma scenario**
  - Ensure the following clinical terms exist in `dictionary/glossary.json` and have accurate Arabic translations:
    - `asthma`
    - `dyspnea` (and/or `shortness of breath`)
    - `wheezing`
    - `bronchodilator` (and/or `inhaler`)
    - `spacer`
    - `emergency department`
- [ ] **Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)**

## Phase 2: Bilingual Audio Generation
- [ ] **Task 2.1: Create `generate_arabic_audio.py`**
  - Design a dialogue scenario for an asthma/breathing difficulty emergency.
  - Setup Google Cloud TTS voice configuration with standard Arabic (`ar-XA`) and Australian English (`en-AU`).
  - Overlay synthesized audio segments into a dual-channel stereo WAV file at `samples/ar_asthma_session.wav`.
- [ ] **Task 2.2: Verify generated audio**
  - Confirm the file is stereo and can be processed correctly by the audio utilities.
- [ ] **Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)**

## Phase 3: Web Server & Web UI RTL Support
- [ ] **Task 3.1: Add Arabic preset to `web_server.py`**
  - Map `"arabic"` preset to `samples/ar_asthma_session.wav`.
- [ ] **Task 3.2: Update Web Front-End (`web/main.js` & `web/index.html`)**
  - Add the Arabic option to the UI dropdown list.
  - Implement language configuration mapping for `arabic` inside `web/main.js`.
- [ ] **Task 3.3: Implement RTL/LTR Styling in Web UI**
  - Update `web/style.css` and transcript rendering in `web/main.js` to dynamically add an `rtl` class or set CSS properties (`direction: rtl`, `text-align: right`) for the patient column when the selected language is Arabic.
  - Ensure font size and line height are optimized for Arabic script.
- [ ] **Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)**

## Phase 4: E2E Verification & Review
- [ ] **Task 4.1: Run E2E test with Arabic Demo**
  - Start the web server and test the Arabic demo session.
  - Verify that both patient transcriptions (Arabic) and translations render beautifully with correct alignment and RTL direction.
- [ ] **Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)**
