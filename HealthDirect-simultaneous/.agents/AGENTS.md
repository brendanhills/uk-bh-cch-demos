# Project Rules

- **Gemini Live Translate Compatibility**: Under developer API mode, `gemini-3.5-live-translate-preview` does not support `system_instruction` when used in tandem with `translation_config`. To avoid WebSocket 1011 crashes, always omit the `system_instruction` parameter in `LiveConnectConfig` for live translation models.
- **Robust Glossary Schema Parsing**: Clinical glossary translation values can be flat strings, arrays of strings, or dictionaries (with `.formal` and `.informal` keys). Any function parsing these translations (frontend/backend) must recursively map and join all sub-elements to prevent returning empty strings or throwing TypeErrors.
- **Model Compatibility Limit**: Only select, configure, or use Gemini 3.0 and later models (such as `gemini-3.5-live-translate-preview` or newer) for live translation or bilingual transcription tasks. Do not attempt to fall back to older legacy version families (such as Gemini 2.x, 1.x, etc.) to ensure seamless multi-client audio streaming compatibility.

