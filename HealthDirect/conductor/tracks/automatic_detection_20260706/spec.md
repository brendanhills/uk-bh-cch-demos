# Specification: Automatic Language & Gender Detection (`automatic_detection_20260706`)

This specification outlines the requirements to dynamically detect a caller's language and speaker gender from the initial seconds of an incoming audio stream, eliminating the need for hardcoded presets.

---

## 1. Overview

In a production scenario, the medical interpreter cannot pre-determine the language or gender of a caller. This track introduces a high-fidelity dynamic detection phase that analyzes the initial 3-5 seconds of caller audio to resolve these details, then automatically provisions and primes the appropriate bilingual Gemini Live sessions.

---

## 2. Functional Requirements

### Phase 1: Dynamic Initial Classifier & Routing
- **Short Audio Detection:** Analyze the first 3-5 seconds of the caller's audio stream.
- **Dual-Step Inference:** 
  1. Use a lightweight audio analyzer (or a fast Gemini audio-to-text prompt) to identify the spoken language (German, Spanish, Vietnamese, or Arabic) and the voice profile (male vs. female).
  2. Verify the classification results during the first turn of translation.
- **Preset Mapping:** Map the detected language to the correct locale code (`de`, `es`, `vi`, `ar`) and select the output voice based on gender (e.g., Puck for male, Kore for female/nurse).

### Phase 2: Dynamic Live Session Priming
- **Dynamic Handshake:** Update the WebSocket connection flow to initiate in "discovery mode" before establishing the dual translation sessions.
- **Seamless Spawning:** Once detection is verified, dynamically spawn the two Gemini Live connections with the appropriate system instructions and voice configurations on the fly.
- **Fail-Safe Fallbacks:** If detection is inconclusive within 5 seconds, default gracefully to the standard English/German preset and log a warning to `interpreter_session.log`.

---

## 3. Non-Functional Requirements
- **Low Latency:** Detection must complete in under 5.0 seconds from the playhead start.
- **Accuracy:** The classifier should achieve >90% accuracy on the current demo samples.

---

## 4. Acceptance Criteria
- [ ] Initiating a call without selecting a language preset successfully detects German, Spanish, Vietnamese, or Arabic.
- [ ] Output translation voice genders dynamically match the speaker's vocal characteristics (Puck for male, Kore for female).
- [ ] Complete E2E integration verified with existing audio samples.
