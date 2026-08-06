# Specification: Passive Interpreter Guardrails & Translation Auditing

## Overview
This track addresses the safety and boundary compliance of standard, generic models (like `gemini-3.1-flash-live-preview`) operating as passive real-time interpreters. Standard multimodal models do not support closed translation modes and rely strictly on system prompts. In high-stress scenarios (such as distress calls or emergency situations), they may break character to converse with, reassure, or answer the patient. 

This track specifies three layers of runtime guardrails to programmatically detect and flag when the model behaves conversationally rather than translating.

## Functional Requirements
1. **Language & Character-Set Leakage Guardrail:**
   - Detect when the model speaks to the patient in their native language during Patient-to-Nurse (`p_to_n`) translation.
   - For `p_to_n` (translating non-English native speech to English for the clinician), scan the real-time transcription output for native character sets (e.g. Arabic script, Spanish/German non-ASCII keywords) or execute language classification.
   - Flag any native characters found in the `p_to_n` English translation stream as a direct conversational leakage violation.

2. **Conversational Phrase & Disclaimer Auditing:**
   - Implement real-time regular expression scanning on all model output text transcriptions.
   - Scan against defined patterns of conversational comfort (e.g. "stay calm", "sorry to hear that"), agentic identification (e.g. "as an AI", "I am an interpreter"), and medical disclaimers ("consult a doctor", "this is not medical advice").
   - Categorize and flag matches as compliance alerts.

3. **Asynchronous LLM-in-the-Loop Semantic Verification:**
   - Establish an out-of-band asynchronous evaluation process (e.g., using lightweight `gemini-2.5-flash` or `gemini-3.5-flash` HTTP endpoints).
   - Feed the evaluator the original segment text (input) and the generated translation (output).
   - Classify whether the translation contains extraneous reassuring remarks, instructions, or conversational replies that were absent from the original input.

## Acceptance Criteria
- [ ] Programmatic detection correctly flags native language characters (such as Arabic script) appearing in the clinician's English translation feed.
- [ ] Regular expression audit successfully flags typical conversational/disclaimer phrases.
- [ ] Async LLM evaluation successfully identifies semantic drift where the model reassures or answers a distressed caller.
- [ ] Detected compliance violations are cleanly logged and transmitted to the frontend client for UI warning display.
