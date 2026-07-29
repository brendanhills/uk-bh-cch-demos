# Specification: WebSocket Pre-Warming & Model Preloading (`pre_warming_20260715`)

## Overview
Currently, establishing stateful, bidirectional Gemini Live API WebSocket connections incurs a 1.2s - 2.5s connection cold-start. This track implements process-level model pre-warming and client-handshake-driven WebSocket preloading to establish ready-state parallel Live sessions. Pre-warming is enabled by default, but can be fully deactivated using a configuration switch or command-line option.

## Functional Requirements
1. **Model Preloading (Process-Level):**
   - Pre-warm the Voice Activity Detection (VAD) state machines during application initialization so they do not incur on-demand setup delays.
2. **WebSocket Handshake Caching (Client Handshake Connection):**
   - **Default Behavior:** As soon as a user accesses the Single-Tab Unified Presentation Console, automatically initialize both Live Connect WebSocket handshakes (Patient-to-Nurse and Nurse-to-Patient) in the background.
3. **Deactivation Config / Switch:**
   - Add `"enable_prewarming": true` inside the central registry configuration file (`demo/interpreter_config.json`).
   - Add a command-line flag override `--no-prewarm` inside `demo/web_server.py` to bypass pre-warming.
4. **Sparse Keep-Alive Pings:**
   - To maintain these pre-connected WebSockets in a hot, standby state, stream sparse digital silence frames (`b'\x00'` mono 16kHz linear PCM) every 2.5 seconds.
5. **Stateful UI Indicators:**
   - Integrate a colored connection state bubble in the HTML presentation interface:
     - 🔴 Disconnected (Initial / offline or pre-warming deactivated)
     - 🟡 Connecting (Handshake in progress)
     - 🟢 Hot & Ready (Fully connected, authenticated, and pre-warmed)

## Non-Functional Requirements
- **Sub-100ms Swap Latency:** Switching from pre-warmed standby mode to raw streaming must be instantaneous (<10ms).
- **Zero WebSocket Leaks:** Unused pre-warmed connections must be closed properly on client disconnect or page unload.

## Acceptance Criteria
- [ ] VAD and model helpers load at startup.
- [ ] Both Patient and Nurse connections are pre-warmed automatically upon opening the Presentation console (unless disabled).
- [ ] Support `--no-prewarm` and `"enable_prewarming": false` settings to disable pre-warming.
- [ ] Status bubble transitions from Connecting (Yellow) to Hot & Ready (Green) within 3 seconds of load when active.
- [ ] Real-time speech stream starts instantly when speaking or streaming audio.
- [ ] All unit and integration tests for preloading and keep-alive are fully green.

## Out of Scope
- Pre-warming server-side models for multiple concurrent independent client sessions beyond the single-tab paired console.
