# Phased Bug Implementation Plan (Balanced Mode)

Executive summary and risk-balanced execution roadmap for resolving all active bugs and feature enhancements in [.agents/bugs.json](file:///home/brendanhills/dev/uk-bh-experiments/CCH_demo/.agents/bugs.json).

---

## Executive Summary
- **Total Active Bugs / Feature Enhancements**: 9 Active Items (27 Items Resolved / Implemented / Obsolete)
- **Target Strategy**: Balanced Risk-Based Execution Roadmap
- **Sprint Focus**:
  - **Phase 1 (Immediate Focus)**: High-impact clinical export (#BUG-23) for PSN demo.
  - **Phase 2 (Multilingual & Medical Glossary)**: Zero-config dynamic multilingual ASR speech recognition (#BUG-37, #BUG-44), in-context LLM medical terminology explanations, and transcript rendering.
  - **Phase 3 (Codebase Refactoring & UI Simplification)**: Reorganizing folder structures, moving docs/scripts (#BUG-41), and privacy-first inline medical document scanner (#BUG-42).
  - **Phase 4 (Enterprise Compliance & Upgrades)**: PII redaction (Model Armor), immutable clinical audit trail (#BUG-39), attached document image persistence (#BUG-45), and Gemini Live API model endpoint upgrades.

---

## Phase 1: Immediate Low-Risk Focus (PSN Demo)

| ID | Title | Root Cause / Scope | Fix Strategy | Risk | Impact | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **#BUG-23** | Clinical SOAP Note Export & Modal | Clinicians/parents need downloadable SOAP summary notes | Implement `@app.post("/api/session/soap_note")` in `main.py` & `#soapModal` overlay with Copy/Print PDF in `index.html` | Low | High | **Active** |
| **#BUG-35** | Enable Proactivity & Affective Dialog Checkboxes | Proactivity and Affective Dialog checkboxes currently disconnected | Pass checkbox state in WS payload; dynamically inject Proactive Guidance & Affective Empathy directives into system instruction | Low | Medium | **Fix Implemented** |

---

## Phase 2: Multilingual & Medical Glossary Experience

| ID | Title | Root Cause / Scope | Fix Strategy | Risk | Impact | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **#BUG-37** | Zero-Config Dynamic Multilingual ASR | Need seamless ASR auto-detection across any language without static hints | Configure dynamic multi-language ASR auto-detection in `AudioTranscriptionConfig` in `main.py` | Medium | High | **Active** |
| **#BUG-44** | Human Speech Transcription Accuracy | Human speech audio occasionally misrecognized during live streams | Optimize ASR transcription parameters and noise floor handling for human speech turns | Medium | High | **Active** |
| **Glossary** | HealthDirect Medical Glossary Integration | Parents need friendly explanations of formal medical jargon | Add Constraint #14 (*LLM-Driven Medical Term Explanation*) in `agent.py` & link to Australian/native public health portals | Low | Medium | **Active** |

---

## Phase 3: Codebase Reorganization & UI Simplification

| ID | Title | Root Cause / Scope | Fix Strategy | Risk | Impact | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **#BUG-41** | Codebase Refactoring & Folder Reorganization | Disorganized directory structure (`google_search_agent.py`) | Rename `google_search_agent/agent.py` to `hospital_agent/agent.py`, organize `docs/`, `scripts/`, `logs/` | Low | Medium | **Active** |
| **#BUG-42** | Camera Input Mode Simplification | Simplify camera controls for inspecting medical documents | Inline portrait viewfinder, Google Pixel round shutter, Google Drive focus guide, and privacy auto-off | Low | Medium | **Fix Implemented** |
| **#BUG-32** | Gemini Live API WebSocket 1011 Recovery | Upstream 1011 service unavailable drops connection | Wrap `runner.run_live()` in `try...except APIError` to handle reconnects gracefully without crashing | Low | High | **Fix Implemented** |
| **#BUG-34** | OpenTelemetry Context Detach Warning | OpenTelemetry raises context error on GeneratorExit | Suppress context detachment warnings gracefully in `main.py` on session disconnect | Low | Low | **Fix Implemented** |

---

## Phase 4: Enterprise Security, Compliance & Upgrades

| ID | Title | Root Cause / Scope | Fix Strategy | Risk | Impact | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **#BUG-39** | Secure, Immutable Clinical Audit Trail | Compliance requirement for patient-keyed advice logs | Implement encrypted, append-only audit trail logging for medical discharge advice | Medium | Medium | **Active** |
| **#BUG-45** | Persist Document Image Attachments to Disk | Visual document artifact persistence for clinical audit trail | Save JPEG images to `app/logs/attachments/<session_id>_<timestamp>.jpg` and log file path in `call_transcripts.log` | Low | Medium | **Active** |
| **#BUG-38** | Sensitive Data Protection & PII Redaction | PII in stored call transcripts | Integrate Google Model Armor / Sensitive Data Protection API masking prior to transcript storage | Medium | Medium | **Active** |
| **#BUG-24** | Call Transcript File Logging | Need dedicated audit file for session transcripts | Configure backend logger to write full audio & text transcripts to `logs/call_transcripts.log` | Low | Medium | **Fix Implemented** |
| **#BUG-43** | Evaluate Upgrade to Gemini 2.5 / 3.x Live API | Upgrade streaming model endpoints & ADK versions | Evaluate latest Gemini Live API model endpoints and Google ADK SDK versions | Medium | Low | **Active** |
| **#BUG-22** | Pytest `BaseAgentConfig` Deprecation Filter | Deprecation warning during pytest import | Add `filterwarnings = ["ignore::DeprecationWarning:google.adk.*"]` to `pyproject.toml` | Low | Low | **Fix Implemented** |
| **#BUG-25** | Google Search Grounding Integration | External web search grounding | Re-enable `google_search` tool for background or non-latency-sensitive agent queries | Low | Low | **Active** |
