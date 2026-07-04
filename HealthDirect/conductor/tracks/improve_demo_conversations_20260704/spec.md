# Specification: Improving Demo Sample Conversations

## Overview
This track aims to improve the conversational naturalness, timing, and linguistic quality of the four primary bilingual sample conversation files:
*   `de_fever_session.wav` (German)
*   `es_ear_session.wav` (Spanish)
*   `ar_asthma_session.wav` (Arabic)
*   `paediatric_vietnamese_demo.wav` (Vietnamese)

By refining the dialogue scripts to use natural idioms, empathetic clinical tones, and proper timing, we will ensure that both sides of the conversation sound as authentic as possible, while tuning pacing configurations to prevent speaker overlap and excessive gaps.

## Functional Requirements

### 1. Dialogue Script Enhancements (Authenticity & Idioms)
*   **German (de_fever_session):**
    *   Refine German dialogue to sound like a natural, polite native caller describing a fever and headache with normal German medical idioms.
*   **Spanish (es_ear_session):**
    *   Refine Spanish dialogue to sound like a concerned native speaker calling about their young son's severe earache and fever.
*   **Arabic (ar_asthma_session):**
    *   Refine Arabic dialogue to sound like an anxious parent dealing with an asthma flare-up. Ensure natural phrasing for respiratory symptoms (e.g., "أزيز في الصدر" for wheezing) and proper idioms.
*   **Vietnamese (paediatric_vietnamese_demo):**
    *   Create a dedicated script `generate_vietnamese_audio.py` to synthesize this conversation programmatically.
    *   Refine Vietnamese dialogue to sound like a concerned Vietnamese parent calling about a child's health issue with natural phrasing, proper medical expressions, and polite honorifics.
*   **Tone & Voice Selection:**
    *   Verify voice selection parameters (`voice_name`, `gender`, and optionally `speaking_rate` / `pitch`) to ensure they sound warm, clear, and empathetic.

### 2. Dialogue Timing & Silence Gaps Optimization
*   **Timestamp Recalibration:**
    *   Re-adjust `start_ms` for each turn in all python audio generation scripts (including the new `generate_vietnamese_audio.py`) to minimize "dead air" silence gaps between speakers.
    *   Align speech start offsets to ensure adequate but not excessive transition time for translations.
*   **Pacing Config Adaptation:**
    *   Fine-tune pacing engine parameters (e.g., silence skip thresholds, playhead step rates, or hold thresholds) in the demo runtime to align with the optimized audio streams and prevent overlaps.

### 3. Automated Synthesis & GCS Upload
*   **Regeneration Scripts:**
    *   Maintain robust generation commands (`uv run generate_*.py`) that successfully synthesize audio via the Google Cloud Text-to-Speech API.
    *   Ensure generated files are correctly exported to the `samples/` directory.

## Non-Functional Requirements
*   **Compatibility:** All generated files must be valid 16kHz 2-channel linear16 PCM stereo WAV files (Left channel = caller/patient, Right channel = English nurse).
*   **Test Suite:** Maintain full green status on all 68 existing tests.
*   **Reliability:** Synthesizer scripts must handle API throttling or optional GCS credential absence gracefully.

## Acceptance Criteria
1. Dialogue texts are linguistically native, idiomatic, and clinically realistic for German, Spanish, Arabic, and Vietnamese.
2. Long gaps in the Arabic asthma session are resolved.
3. No overlaps exist between patient/caller utterances and nurse/translation playbacks under standard pacing modes (autopaced).
4. All four audio files are successfully generated and stored locally in `samples/`.
5. Existing test coverage and passing status are preserved.

## Out of Scope
*   Adding entirely new languages or medical conditions beyond German, Spanish, Arabic, and Vietnamese.
*   Creating a graphical user interface (GUI) or browser web-app for this specific audio library track.
