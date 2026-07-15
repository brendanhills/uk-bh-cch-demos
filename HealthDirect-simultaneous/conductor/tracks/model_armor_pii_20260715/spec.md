# Specification: ModelArmor PII & Safety Guardrails (`model_armor_pii_20260715`)

This track implements Google Cloud ModelArmor integration into the real-time simultaneous translation stream to inspect, flag, and redact sensitive personal information (PII), profanities, and custom sensitive data categories prior to external API transmission.

## 1. Overview
In clinical conversations, safeguarding patient confidentiality is paramount. This feature integrates **Google Cloud ModelArmor** to analyze transcripts in real-time. Before text inputs or speech-to-speech frames are transmitted to external Gemini Live models, the system dynamically intercepts the data, filters out sensitive markers, and replaces them with clean redaction placeholders (e.g., `[REDACTED_NAME]`, `[REDACTED_ADDRESS]`). This prevents unauthorized PII leakage while maintaining fluid, uninterrupted clinical dialogues.

---

## 2. Functional Requirements

### 2.1 Configurable Category Selector (Web UI & Backend)
*   **Demo Customization**: Introduce interactive configuration controls in the sidebar of the `/nurse` dashboard.
*   **Selectable Categories**: Clinicians can toggle the following safety rules:
    *   `Patient PII` (Names, addresses, phone numbers, Medicare IDs).
    *   `Profanity & Abuse` (Filtering toxic or abusive expressions).
    *   `Financial Details` (Credit cards, bank account details).
*   **State Parity**: Toggled options are synchronized from the Clinician console to the Patient console via the `ActiveSession` coordinator and saved inside `interpreter_config.json`.

### 2.2 Pre-Transmission ModelArmor Filter
*   **Inspection Pipeline**: Intercept transcribed user utterances *prior* to sending them to Gemini translation streams.
*   **Inline Redaction Strategy**: For any flagged entity, replace the exact matching characters with standardized brackets:
    *   Names $\rightarrow$ `[REDACTED_NAME]`
    *   Phone Numbers / Emails $\rightarrow$ `[REDACTED_CONTACT]`
    *   Addresses $\rightarrow$ `[REDACTED_ADDRESS]`
    *   Profanities $\rightarrow$ `[REDACTED_PROFANITY]`
*   **Speech Alignment**: The redacted text is then forwarded to the translation engine, ensuring that translated text and speech outputs are fully sanitized.

### 2.3 Local & Offline Mock Fallback
*   **Development Safety**: Since direct ModelArmor API connection requires specific IAM credentials, provide a fully-functional local regex/dictionary-based fallback parser inside the class if the Google Cloud ModelArmor client fails to authenticate or when running offline unit tests.

---

## 3. Non-Functional Requirements
*   **Ultra-Low Latency Overhead**: The safety inspection overhead must be $< 15\text{ms}$ per utterance to prevent voice streaming pacing lag.
*   **State Parity**: Configuration changes made on the clinician side must instantly update active ModelArmor filtering policies on the server in real-time.

---

## 4. Acceptance Criteria
1.  **Safety Unit Tests Passing**: A dedicated test suite `tests/test_model_armor_safety.py` runs and verifies that:
    *   Toggling "Patient PII" cleanly redacts names and addresses in dummy patient scripts.
    *   Toggling "Profanity" censors abusive test strings.
    *   Offline mock fallbacks trigger transparently on authorization drops.
2.  **State Synchronization Verified**: Changing ModelArmor settings on the clinician frontend correctly propagates config updates to the server session coordinator.
3.  **Clean Dashboard Rendering**: Redacted brackets display in high-contrast styling (e.g., highlighted badges) in both nurse and patient speech bubbles.
