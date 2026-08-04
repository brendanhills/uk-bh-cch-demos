# Track Specification: Server Hold-Loop Silence Frame Pacing

## Overview
Optimize server-side hold-loop keep-alive streaming in `demo/web_server.py` during conversational turn hold intervals, reducing unnecessary frame accrual while **guaranteeing 100% zero regression** to the existing turn detection, silence threshold monitoring, and audio envelope detection logic.

## Functional Requirements
1. **Preserve Existing Turn Detection & Audio Envelope Logic (CRITICAL):**
   - The existing turn-taking parameters (`ceased_audio_threshold`, `startup_audio_threshold`, `turn_timeout_sec`, and power envelope fallback monitoring) must remain 100% untouched and unchanged.
   - Active speech capture and turn completion triggers must operate with zero behavioral regression.
2. **Sparse Keep-Alive Pacing in Hold Loops:**
   - Modify the hold/transition wait loops in `demo/web_server.py` (lines 2280-2335) to stream sparse keep-alive silence frames every 100ms (`hold_silence_interval_ms`: 100) instead of continuous dense 20ms PCM frames.
3. **Configuration & Safety Control:**
   - Add `"hold_silence_interval_ms": 100` and `"enable_hold_pacing": true` under the `pacing` section in `demo/interpreter_config.json`.
   - If `"enable_hold_pacing"` is `false`, the server seamlessly falls back to legacy continuous frame streaming.

## Non-Functional Requirements
- **Zero Regression:** No impact on speech translation accuracy, turn-taking responsiveness, or connection stability.
- **Safety Fallback:** Immediate fallback to standard streaming if hold pacing is disabled in config.

## Acceptance Criteria
- [ ] Turn-taking timeout and envelope detection logic remain fully operational without behavior change.
- [ ] Server hold loop streams sparse keep-alive frames according to `hold_silence_interval_ms`.
- [ ] Unit tests verify that turn detection thresholds and hold pacing operate cleanly without breaking session keep-alives.

## Out of Scope
- Modifying client-side audio capture or microphone VAD thresholds.
