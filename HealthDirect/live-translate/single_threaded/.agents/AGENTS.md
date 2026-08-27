# HealthDirect — Single-Threaded Streaming Rules

> **Note**: Inherits all baseline HealthDirect project rules from `HealthDirect/.agents/AGENTS.md`.

This workspace operates the single-client audio streaming pipeline. Key baseline constraints applied:
- **Gemini Live Translate Compatibility**: Always omit `system_instruction` in `LiveConnectConfig` when using `translation_config` to avoid WebSocket 1011 crashes.
- **Universal Passive Interpreter Constraints**: Explicitly forbids conversational talkback, empathy responses, or comforting the speaker during real-time translation.
- **Audio Routing**: Left Channel (Channel 1) = Patient (foreign language), Right Channel (Channel 2) = Nurse (English).
- **Test Isolation**: All slow or real-time simulation tests must remain isolated under `long_tests/`.
