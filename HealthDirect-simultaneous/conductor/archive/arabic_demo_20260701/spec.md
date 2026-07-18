# Specification: Arabic Demo Language & RTL Layout (Track: `arabic_demo_20260701`)

## Overview
This track introduces Arabic as a fully supported demo language within the Bilingual Medical Interpreter simulator. Because Arabic uses a non-Latin, Right-to-Left (RTL) script, this track handles the visual complexities of displaying RTL text side-by-side with Left-to-Right (LTR) English text. It also includes generating a new high-fidelity Arabic-English bilingual audio session and adding Arabic glossary translation capabilities to the ingestion pipeline.

## Functional Requirements
1. **Arabic Glossary Ingestion**:
   - Update `import_glossary.py` to support translating medical terms into Arabic (`ar` language code).
   - Ingest and append Arabic translations for existing clinical terms in `dictionary/glossary.json`.

2. **Arabic Bilingual Audio Generation**:
   - Create `generate_arabic_audio.py` to synthesize a stereo call session between an Arabic-speaking patient (Left channel) and an English-speaking Australian nurse (Right channel).
   - Scenario: A parent calling about their child's sudden onset of breathing difficulty/asthma symptoms (dyspnea).
     - The patient uses simple, conversational Arabic (e.g. "إنه يتنفس بصعوبة" / "He is breathing with difficulty").
     - The nurse responds in English, utilizing medical/clinical terms like "asthma", "inhaler", and "bronchodilator".
   - Use Google Cloud Text-to-Speech API with standard, natural Arabic (`ar-XA`) and Australian English (`en-AU`) voices.

3. **RTL Alignment in the Web UI**:
   - Update `web/style.css` and `web/main.js` to automatically detect when the active session is Arabic and apply RTL formatting.
   - The patient's transcription and translation column/bubbles should be right-aligned with proper `direction: rtl` and appropriate typography (e.g., custom font weight/size suitable for Arabic scripts) to ensure high readability.
   - The English nurse column remains left-aligned (`direction: ltr`).

4. **Web Server Preset Integration**:
   - Register the Arabic preset in `web_server.py` and `web/main.js`.
   - Point the preset to `samples/ar_asthma_session.wav`.

## Non-Functional Requirements
- **Visual Harmony**: The Arabic script should render clearly without clipping, overlap, or generic font fallbacks that look out of place.
- **Bi-directional Text Flow**: Mixing numbers or English names within the Arabic text must not disrupt word order.

## Acceptance Criteria
- [ ] `import_glossary.py` successfully translates terms to Arabic and saves them in `dictionary/glossary.json`.
- [ ] `generate_arabic_audio.py` successfully generates `samples/ar_asthma_session.wav` as a 16kHz, 16-bit PCM stereo WAV file.
- [ ] Selecting "Arabic" in the Web UI loads the Arabic audio demo and successfully communicates with the Web Server.
- [ ] The patient's transcriptions and translations are beautifully right-aligned with `direction: rtl` text flow, while the nurse's column remains left-aligned.
