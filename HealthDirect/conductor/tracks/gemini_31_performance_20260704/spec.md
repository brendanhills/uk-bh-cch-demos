# Specification: Improving Gemini 3.1 Flash Live Performance

## Overview
This track addresses major performance, latency, and vocal matching limitations with the standard Gemini 3.1 Flash Live model (`gemini-3.1-flash-live-preview`). Standard models are required to enforce clinical glossaries (since `gemini-3.5-live-translate-preview` does not support custom system instructions or vocabulary injections), but they suffer from specific issues: default female voices for male patients, high-latency transcription displays, pacing hangs due to missing `turn_complete` events, and loss of emotional/urgency tone in translations.

## Functional Requirements
1. **Dynamic Output Voice Gender Matching:**
   - Automatically assign the correct prebuilt voice gender to Gemini Live session configurations based on the speaker's true gender.
   - For Patient session (`session_p_to_n`): Set a voice (e.g. Puck/Charon for male, Kore/Aoede for female) matching the active preset's patient voice configuration.
   - For Nurse session (`session_n_to_p`): Default to a female voice (e.g. Kore) to match Nurse Sarah's gender.
2. **Real-Time Streamed Transcriptions (Low Latency):**
   - Ensure translated transcripts are shown on-screen in real-time as the audio is playing, rather than delaying until the end of a turn.
   - Capture and forward the text chunk segments from `server_content.model_turn.parts[].text` instantly via WebSocket when using standard models, instead of solely relying on delayed `output_transcription` events.
3. **Tone and Emotion Preservation:**
   - Enhance passive constraint prompt instructions to strictly direct the standard model to match the emotion, concern, clinical warmth, urgency, and tone of the original spoken utterance.
4. **Pacing Connection Resilience & Freeze Mitigation:**
   - Ensure the pacing state machine does not lock up or freeze if the standard model delays or fails to emit standard `turn_complete` signals.
   - Integrate safety turn-completion fallback timeouts or audio power envelope monitoring to guarantee playhead progression.

## Acceptance Criteria
- [ ] Voice gender of the translated speaker matches the original input speaker's gender (male patient translated to male voice, female nurse translated to female voice).
- [ ] Translation transcription updates incrementally on-screen in real-time during playback.
- [ ] Translated speech preserves the original speaker's tone, concern, and urgency.
- [ ] No simulation freezes or deadlocks occur when playing long sessions under standard 3.1 Flash Live.
