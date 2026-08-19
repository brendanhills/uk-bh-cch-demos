# Master Specification: Cymbal Children's Hospital Assistant

> **Status**: APPROVED MASTER SPECIFICATION  
> **Project Scope**: Public Event & Customer Showcase Demo (Not Production Code)  
> **Target Version**: ADK 2.0 / Gemini Live API (Gemini 3.1 Flash Live / Gemini 3 Flash)  
> **Last Updated**: 2026-08-19  
> **Author**: Brendan Hills  

---

## 1. Executive Summary & Vision

The **Cymbal Children's Hospital (CCH) Early Support & Discharge Assistant** is an interactive, real-time bidirectional streaming AI demonstration built using Google's **Agent Development Kit (ADK) 2.0**, **FastAPI**, and **Gemini Live API**.

> [!IMPORTANT]
> **Project Purpose & Demo Scope**:
> This project is designed specifically as a **high-impact demonstration application for public events, customer showcases, technical keynotes, and executive briefings** to present state-of-the-art Google Cloud AI, ADK 2.0 multi-agent delegation, and Gemini Live API streaming capabilities. **It is not production software.** Architectural decisions, UI event consoles, and workflow features are optimized for presentation excellence, sub-second responsiveness, and stakeholder engagement.

The application provides sub-second multimodal interaction—combining low-latency voice streaming, live camera vision, and text chat—to assist pediatric patients' families during home care transition. It automates discharge paperwork verification, financial subsidy navigation (Medicare / NDIS), home-care nurse visit scheduling, structured clinical SOAP note generation, and medical terminology explanations.

---

## 2. Target Audience & Presentation Scope

1. **Public Sector IT & Healthcare Technical Decision Makers (Primary Demo Audience)**:
   - Government technology leaders, health IT directors, software engineers, and customer executives evaluating Google Cloud AI, Agent Development Kit (ADK), Vertex AI, and Gemini Live API for public sector and healthcare transformation.
2. **Demo Persona & Scenario End Users**:
   - **Families & Caregivers**: Parents navigating pediatric discharge instructions and home care management.
   - **Hospital Clinical Teams**: Pediatric nurses, discharge planners, and hospital EMR administrators.

---

## 3. System Architecture & Multi-Agent Concierge Pattern

Rather than a monolithic prompt, the system employs an **ADK 2.0 Multi-Agent Concierge Architecture**:

```
                              ┌──────────────────────────────────┐
                              │     WebSocket Client (Web UI)    │
                              └──────────────────────────────────┘
                                               │
                                  /ws/{user_id}/{session_id}
                                               ▼
                              ┌──────────────────────────────────┐
                              │  cch_concierge_router (Jennie)   │
                              │     (gemini-3.1-flash-live)      │
                              └──────────────────────────────────┘
                                 │            │            │
            ┌────────────────────┘            │            └───────────────────┐
            │ Direct Fast-Path (<10ms)        │ Search Grounding               │ Sub-Agent Delegation (≤0.5s)
            ▼                                 ▼                                ▼
┌───────────────────────────┐     ┌─────────────────────┐     ┌──────────────────────────────────┐
│  validate_phone_number    │     │    google_search    │     │  TimedAgentTool(sub_agent)       │
│  record_patient_identity  │     └─────────────────────┘     ├──────────────────────────────────┤
└───────────────────────────┘                                 │ 1. patient_verifier              │
                                                              │ 2. document_scanner              │
                                                              │ 3. visit_scheduler               │
                                                              │ 4. soap_generator                │
                                                              └──────────────────────────────────┘
```

### 3.1 Master Concierge Router Agent (`cch_concierge_router`)
- **Single Persona Guardrail**: Presents a unified, warm Australian healthcare coordinator persona named **Jennie**. Internal transfers, role titles, and sub-agent names are strictly hidden from callers.
- **Answering Script**: Upon session initiation/greeting, delivers:
  > *"Hello, thank you for calling Cymbal Children's Hospital. My name is Jennie. How can I help you today?"*
- **Fast-Path Execution (< 10 ms)**: Direct Python tools (`validate_phone_number`, `record_patient_identity`) execute in-memory on the router without initiating sub-agent turns.

### 3.2 Specialized Sub-Agents (`app/cch_agent/sub_agents/`)
1. **`patient_verifier`**: Handles identity capture, Australian phone validation (`04xx xxx xxx`, `02/03/07/08`), global country code mapping (+44, +1, +64, +65, +91), and ADK session memory persistence (`tool_context.state`). Prevents duplicate prompts for known details (e.g. child's name).
2. **`document_scanner`**: Performs OCR/multimodal vision analysis on captured discharge papers, invokes `request_document_scan` client UI trigger tool, and enforces constructive vision guidance (helping users take clear photos or troubleshooting camera state).
3. **`visit_scheduler`**: Manages nurse appointment availability (`get_available_support_times`), dynamic practitioner assignment mapping (using dynamic names returned by EMR lookup API rather than hardcoded prompt strings), cost calculation (`calculate_home_care_financials`), Medicare 15% rebate & NDIS subsidy application, and EMR database updates (`update_hospital_emr`).
4. **`soap_generator`**: Synthesizes clinical Subjective, Objective, Assessment, and Plan (SOAP) notes for session exports and FastAPI REST calls.

---

## 4. Functional Specifications

### 4.1 Real-Time Bidirectional Voice & Transcriptions
- **Streaming Mode**: Full BIDI audio streaming over WebSockets via Gemini Live API (`run_live`).
- **Dynamic Multilingual ASR**: Zero-config speech recognition auto-detects spoken languages (English, Arabic, Hindi, Spanish, Vietnamese, German, Japanese, etc.) without hardcoded hint arrays.
- **RTL Chat Interface**: Automatic right-to-left (`dir="rtl"`) text rendering and right-aligned bubble layout for Arabic and other right-to-left (RTL) languages (e.g., Arabic, Hebrew, Urdu, Farsi).
- **Sub-Agent Delegation Telemetry Bounds**: Delegation latency is logged (`time.perf_counter()`) and bound to **≤ 0.5 seconds (500 ms)** via `TimedAgentTool(..., skip_summarization=True)`.

### 4.2 Multimodal Document Inspection & Constructive Vision Behavior
- **Agentic Trigger**: `request_document_scan(document_type, prompt_reason)` tool opens browser camera viewfinder automatically during document steps.
- **Guided Viewfinder**: Inline camera viewfinder with portrait scanning guide, keyboard shortcuts (`Space` / `Enter` shutter), and automatic camera hardware shutdown after single capture.
- **Constructive Vision Guidance (Situational Behavioral Rules)**:
  - *No Image Received*: If no document image payload has arrived when paperwork is mentioned, constructively assist the caller by opening/triggering the camera scanner UI and explaining how to position the document.
  - *Blurry / Poor Capture*: If an uploaded image frame is out of focus, cut off, or poorly lit, constructively guide the caller to hold the paper steady, flatten the page, or adjust room lighting for a clear shot.
  - *Grounding*: Discuss clinical instructions strictly based on legible text visible on captured document frames.
- **Attachment Persistence & Audit Log**: Raw JPEG snapshots saved to `app/logs/attachments/<session_id>_<timestamp>.jpg` and logged in `app/logs/transcripts/call_transcripts.log`.

### 4.3 Patient Identity & Phone Verification
- **Global & Australian Phone Recognition**: Validates Australian mobile (`04xx xxx xxx`) and landline (`02/03/07/08`) formats as well as international numbers (+44, +1, +64, +65, +91).
- **ADK Session State**: Stores `caller_name`, `patient_name`, `phone_number`, and `phone_country` in `tool_context.state` so subsequent agents never re-prompt for known details.

### 4.4 Financial Subsidies & EMR Appointment Scheduling
- **Rebate Calculations**: Calculates base home care costs, Medicare 15% subsidies, and NDIS rebates (`calculate_home_care_financials`).
- **Dynamic Date Context**: System prompt injects `datetime.now()` to ensure accurate date context during scheduling.
- **Dynamic Practitioner Mapping**: Practitioner names (e.g. Nurse Sarah, Nurse Michael, Nurse Emily) are dynamically retrieved from EMR scheduling lookup tools (`get_available_support_times`) and mapped to bookings without hardcoding practitioner names in prompt instructions.

### 4.5 Structured Clinical SOAP Export & Modal
- **REST Endpoint**: `@app.post("/api/session/soap_note")` generates formal SOAP summary from session transcripts.
- **Export Modal UI**: UI `#soapModal` dialog featuring paper document styling, one-click clipboard copying, and print-to-PDF support.

### 4.6 HealthDirect Medical Glossary & Jargon Explanation [Planned Future Enhancement]
- **Medical Term Explanations**: Future enhancement to integrate HealthDirect guidelines for in-context LLM explanations translating complex clinical jargon (e.g. *tympanostomy*, *analgesic titration*, *debridement*) into plain, reassuring terms for parents.

### 4.7 Demo Performance & Optimizations [Planned Future Enhancements]
- **Startup Pre-Warming Pipeline**: Planned enhancement to eager-load ADK sub-agents into Python memory and pre-cache system instructions on boot.
- **Gemini Context Caching**: Planned enhancement utilizing `genai.caching.CachedContent` for shared system prompts (`CCH_SHARED_PERSONA`) to achieve ~75% token cost reduction and 40% faster TTFT.

### 4.8 Prompting Architecture & Best Practices
- **Hybrid Markdown & XML Tagging Architecture**: System instructions use semantic XML boundary tags (`<persona>`, `<role>`, `<instructions>`, `<common_guardrails>`) for boundary isolation combined with Markdown for headings, bold emphasis, and structured lists.
- **Single Persona Consolidation (`CCH_SHARED_PERSONA`)**: Shared baseline persona module ensures a single voice ("Jennie") across all sub-agents and suppresses canned re-greetings or filler platitudes.
- **Positive Situational Behavioral Guidance**: Instructs the model *how* to handle blurry or missing camera frames constructively.
- **Gemini Prompt & Context Caching (`CachedContent`)**: Caches shared system prompts and personas on Google Cloud infrastructure for ~75% token input cost savings and up to 40% faster TTFT.

---

## 5. Technical Specifications & Environment

### 5.1 Gemini Models Specification

> **Model Policy**: The project strictly uses **Gemini 3+** models for all Flash inference tasks. Legacy Flash models (pre-Gemini 3) are never used.

| Model Role | Primary Model Endpoint | Fallback / Alternative Endpoint | Purpose & Modality |
| :--- | :--- | :--- | :--- |
| **Master Concierge Router** | `gemini-3.1-flash-live-preview` (Gemini API) | `gemini-3.1-flash-live` (Vertex AI) | Low-latency native audio BIDI WebSocket streaming with turn pacing & persona guardrails. |
| **Domain Sub-Agents** | `gemini-3-flash` | `gemini-3.1-flash` | Low-cost unary reasoning for OCR document vision, Australian phone validation, scheduling, and SOAP note synthesis. |

### 5.2 Technical Environment Specification

#### Infrastructure & Hosting
- **Cloud Platform**: Google Cloud Platform (GCP) / Google AI Studio.
- **API Gateways**: Supported in both Vertex AI Live API mode (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`) and Google AI Studio API key mode (`GOOGLE_GENAI_USE_VERTEXAI=FALSE`).
- **Deployment Targets**: Google Cloud Run (containerized web app) or Vertex AI Agent Engine (managed agent backend).

#### Runtime & Dependencies
- **Programming Language**: **Python 3.13+** (managed via `uv` package & environment manager).
- **Web Framework & Server**: FastAPI 0.115+ with Uvicorn ASGI server (`uvicorn[standard]>=0.32.0`).
- **Agent Framework**: Google Agent Development Kit (`google-adk>=2.0.0`) & Google GenAI SDK (`google-genai>=2.0.0`).
- **Real-Time Protocol**: WebSockets (`/ws/{user_id}/{session_id}`).
- **Testing & Tooling**: Pytest 8.0+ (`pytest-asyncio`), Ruff linter/formatter (`target-version = "py310"`).

---

## 6. Project Development Workflow & SDD Methodology

Development on the Cymbal Children's Hospital Assistant follows a rigorous **Specification-Driven Development (SDD)** workflow and structured verification gates:

### 6.1 Specification-Driven Development (SDD) Principle
- **Specification First**: All architectural changes, multi-agent tools, API contracts, and user-facing features must be formally specified in `conductor/spec.md` *before* writing application code.
- **Specification as Authoritative Blueprint**: Code implementations and tests are audited against the Master Specification to prevent unauthorized drift or un-tracked feature additions.

### 6.2 Automated Unit Testing Policy (Large Changes Only)
- **Large & Structural Changes ONLY**: Automated unit testing (`.venv/bin/pytest`) is executed **ONLY when making large code modifications or structural architecture changes** (e.g. modifying sub-agent routing logic in `agent.py`, adding FastAPI REST endpoints, altering session memory schemas, or refactoring WebSocket queues).
- **No Over-Testing**: Agents must NOT write redundant unit tests or execute heavy test suites for minor text edits, prompt instruction tweaks, or simple UI styling changes.

### 6.3 Mandatory User Manual Verification & Sign-Off Gate
- **Verification Rule**: All new features (Feature Requests / FRs) and all bugs or feature requests categorized with **Medium**, **High**, or **Critical** impact MUST be **manually verified and signed off by the author (`brendanhills`)** before their status can be marked as `"Fix Verified"` or `"Completed"` in `.agents/bugs.json` or Conductor track plan registries.
- **Audit Workflow**: Automated unit tests passing is a prerequisite, but does *not* grant permission to mark a Medium/High/Critical item as complete. The user must manually test the live interface/flow and provide explicit sign-off.
