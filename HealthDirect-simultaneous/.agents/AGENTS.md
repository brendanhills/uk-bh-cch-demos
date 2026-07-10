# Project Rules

- **Gemini Live Translate Compatibility**: Under developer API mode, `gemini-3.5-live-translate-preview` does not support `system_instruction` when used in tandem with `translation_config`. To avoid WebSocket 1011 crashes, always omit the `system_instruction` parameter in `LiveConnectConfig` for live translation models.
- **Robust Glossary Schema Parsing**: Clinical glossary translation values can be flat strings, arrays of strings, or dictionaries (with `.formal` and `.informal` keys). Any function parsing these translations (frontend/backend) must recursively map and join all sub-elements to prevent returning empty strings or throwing TypeErrors.

