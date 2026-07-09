# Project Rules

- **Finish for the day**: When requested to finish for the day, update the README.md, Resume.md (compaction summary), and track status, commit all modified files with a descriptive message, and push the branch to the remote repository.
- **checkpoint**: When requested with "checkpoint" (or when you say "checkpoint"), update the README.md and Resume.md (compaction summary), track status, commit all modified files with a descriptive message, and push the branch to the remote repository.
- **Gemini Live Translate Compatibility**: Under developer API mode, `gemini-3.5-live-translate-preview` does not support `system_instruction` when used in tandem with `translation_config`. To avoid WebSocket 1011 crashes, always omit the `system_instruction` parameter in `LiveConnectConfig` for live translation models.
- **Robust Glossary Schema Parsing**: Clinical glossary translation values can be flat strings, arrays of strings, or dictionaries (with `.formal` and `.informal` keys). Any function parsing these translations (frontend/backend) must recursively map and join all sub-elements to prevent returning empty strings or throwing TypeErrors.

