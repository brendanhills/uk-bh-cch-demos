# Spec vs. Codebase Discrepancy Review Matrix

Generated: 2026-09-03 (Audit performed via `/spec_drift`)

## Overview

This audit provides a multi-layer architectural and data drift comparison between the authoritative project specifications (`conductor/product.md`, `conductor/tech-stack.md`, `conductor/tracks/adk2_multi_agent_workflow_20260806/spec.md`, `conductor/tracks/stage_demo_soap_controls_20260902/spec.md`, `docs/RCH_CONCIERGE_DOCUMENTATION.md`) and the implemented codebase (`app/`).

---

## Discrepancy Review Matrix

| ID | Domain / Component | Specification Version | Implemented Codebase Version | Resolution Status | Recommended Action |
|:---|:---|:---|:---|:---:|:---|
| **D-1** | AI Engine / Model Endpoint | `gemini-2.0-flash-exp` (`conductor/tech-stack.md`) | `gemini-live-2.5-flash-native-audio` (`app/cch_agent/agent.py`) | 🟡 Open | **Update Spec**: Update `conductor/tech-stack.md` to document Gemini 2.5 Live API native audio. |
| **D-2** | **Agent Architecture & Routing** | Sub-agent delegation via `AgentTool` (`adk2_multi_agent_workflow_20260806/spec.md`) | Single router with direct domain tools attached (`app/cch_agent/agent.py`) | 🟢 Resolved (Reverted) | **Branch Context**: ADK 2.0 multi-agent track was reverted and moved to a separate branch. On `cch-agent-demo`, single-agent concierge architecture is the intentional production baseline. |
| **D-3** | Clinical Tool Signature (`schedule_home_care_visit`) | `schedule_home_care_visit(slot_id, child_name, parent_name)` (`docs/RCH_CONCIERGE_DOCUMENTATION.md`) | `schedule_home_care_visit(date, time, child_name, parent_name, service_type, practitioner)` (`app/cch_agent/tools/scheduling.py`) | 🟡 Open | **Update Spec**: Align documentation and sample dialogues to match the implemented natural date/time/practitioner signature. |
| **D-4** | Clinical SOAP Note Endpoints | `POST /api/session/soap_note` & `GET /api/soap/{session_id}` (`adk2` & `stage_demo` track specs) | Missing; only `GET /`, `GET /favicon.ico`, `WS /ws/{user_id}/{session_id}` exist (`app/main.py`) | 🟡 Open | **Code Fix**: Implement SOAP note generation endpoint and background task in `app/main.py` (Phase 3 of ADK2 track). |
| **D-5** | Stage Demo Call Controls & SOAP Modal | Dedicated `📞 Start Call`, `📞 End Call`, and `#soapModal` popup (`stage_demo_soap_controls_20260902/spec.md`) | Legacy controls (`Start Audio`, `Stop Mic`, `Camera`, `Send`, `New Session`); no SOAP modal (`app/static/index.html`) | 🟡 Open | **Code Fix**: Implement stage demo buttons and post-call modal in `index.html`, `style.css`, and `app.js`. |
| **D-6** | Document Attachment Disk Persistence | Raw JPEG saved to `app/logs/attachments/<session_id>_<timestamp>.jpg` and logged in transcript (`adk2` spec / #BUG-45) | In-memory forwarding to Live API only; not written to disk (`app/main.py`) | 🟡 Open | **Code Fix**: Persist incoming document images to disk and append file paths to `call_transcripts.log` (Phase 2 of ADK2 track). |
| **D-7** | Proactivity Feature Availability | Supported proactive turn toggle (`conductor/product.md`, `docs/RCH_CONCIERGE_DOCUMENTATION.md`) | Explicitly bypassed due to Gemini Live API Error 1000 (`app/main.py`, `app.js`) | 🟡 Open | **Update Spec**: Add note in product documentation explaining proactivity is paused pending upstream Live API support. |
| **D-8** | Speech Recognition Language Hints | Broad multilingual ASR for AU English, Arabic, Hindi, Mandarin, Vietnamese (`product.md`, `RCH_CONCIERGE_DOCUMENTATION.md`) | Hardcoded static hints `language_codes=["en-AU", "ar"]` (`app/main.py`) causing script confusion (#BUG-37) | 🟡 Open | **Code Fix**: Update `AudioTranscriptionConfig` to support dynamic language auto-detection (#BUG-37). |
| **D-9** | External Web Search Grounding | `google_search` tool enabled on agent (`adk2` spec / #BUG-25) | Omitted from active router agent tools list (`app/cch_agent/agent.py`) | 🟡 Open | **Code Fix / Align**: Evaluate latency impact before integrating `google_search` tool into Live API session. |
| **D-10** | Cloud Monitoring Uptime Health Endpoints | Not documented in `tech-stack.md` or `product.md` | `GET /health` and `GET /health/live` in `app/health.py` | 🟡 Open | **Update Spec**: Document the health check proxy and monitoring architecture in `conductor/tech-stack.md`. |

---

## Detailed Triage & Recommendations

### 1. Architectural Evolution (Recommend Spec Updates)
- **D-1 (Model Endpoint)**: The project upgraded from the early experimental `gemini-2.0-flash-exp` to the production `gemini-live-2.5-flash-native-audio` (and `gemini-2.5-flash` for sub-agents). `conductor/tech-stack.md` should be updated to reflect current models.
- **D-2 (Agent Architecture)**: The original track spec called for nested `AgentTool` sub-agent routing. During testing, it was found that Gemini Live API BIDI WebSocket sessions require direct function tools on the active streaming connection for low-latency voice responses. Sub-agents were preserved in `app/cch_agent/sub_agents/` for out-of-band operations (e.g., SOAP note generation). The track spec should be amended to document this hybrid architecture.
- **D-3 (Scheduling Tool Parameters)**: Taking natural `date`, `time`, and `practitioner` strings directly from spoken user turns proved superior to synthetic `slot_id` lookups. Documentation in `docs/RCH_CONCIERGE_DOCUMENTATION.md` should be refreshed to reflect this.
- **D-7 (Proactivity Status)**: Live API upstream error 1000 forced proactivity to be bypassed in code. The spec should document this temporary upstream limitation.
- **D-10 (Health Endpoints)**: The uptime check proxy in `app/health.py` was added to support Cloud Run deployments with Cloud Monitoring. `tech-stack.md` should document this component.

### 2. Implementation Gaps (Recommend Code Fixes)
- **D-4 & D-5 (Clinical SOAP Export & Stage Call Controls)**: High priority for stage demo readiness. The implementation tasks defined in `conductor/tracks/stage_demo_soap_controls_20260902/` and `adk2_multi_agent_workflow_20260806/` are planned but not yet executed in `main.py` and `index.html`.
- **D-6 (Attachment Persistence - #BUG-45)**: Capturing document JPEGs to disk is required for audit trails and clinical review. Code update needed in `app/main.py`.
- **D-8 (Multilingual ASR - #BUG-37)**: Hardcoded `["en-AU", "ar"]` causes English speech to occasionally be transcribed in Arabic script. Dynamic language hints or removing restricted hints will improve transcription accuracy.
- **D-9 (Google Search Grounding - #BUG-25)**: Currently pending in the track plan.
