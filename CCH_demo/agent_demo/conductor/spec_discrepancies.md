# Master Specification vs. Codebase Discrepancy & Comparison Review Matrix

> **Generated on**: 2026-08-19  
> **Purpose**: Audits the legacy Master Specification (`conductor/product.md`) against the implemented codebase and the updated proposed Master Specification (`conductor/spec_draft.md`).

---

## 1. Executive Summary of Specification Drift

As the project evolved through **Tracks 1–3** and 59 logged bugs/FRs, significant architectural and functional enhancements were introduced into the codebase that were not captured in the original `conductor/product.md`:

1. **Project Scope & Purpose**: Explicitly designated as a **high-impact demonstration application for public events, customer showcases, technical keynotes, and executive briefings**. It is not production healthcare code.
2. **Architecture Evolution**: Transitioned from a single monolithic agent prompt to an **ADK 2.0 Multi-Agent Concierge Router** (`cch_concierge_router`) delegating to 4 specialized sub-agents (`patient_verifier`, `document_scanner`, `visit_scheduler`, `soap_generator`) with sub-500ms delegation latency bounds.
3. **Project Development Workflow & SDD Methodology**: Explicitly documented Specification-Driven Development (SDD), automated unit testing (`.venv/bin/pytest`) for structural changes, and mandatory user manual verification sign-off for new features and Medium+ impact bugs/FRs.
4. **Prompting Best Practices & Prompt Caching**: Added dedicated Prompting Architecture section detailing XML tagging (`<persona>`, `<role>`, `<instructions>`), single persona consolidation (`CCH_SHARED_PERSONA`), positive situational guidance, zero-filler rules, and Gemini Prompt Caching (`CachedContent`) for ~75% cost savings.
5. **Clinical Export Capabilities**: Added structured clinical SOAP note generation and REST endpoint (`/api/session/soap_note`) with frontend `#soapModal` overlay (#BUG-23).
6. **Multimodal Document Audit**: Added snapshot image attachment persistence to `app/logs/attachments/<session_id>_<timestamp>.jpg` and transcript file audit logging (#BUG-45).
7. **Agentic UI Controls**: Introduced custom tool `request_document_scan` to automatically open the guided camera viewfinder UI on demand (#BUG-48).
8. **Zero-Config Multilingual ASR & RTL**: Replaced static language hints with dynamic multilingual ASR auto-detection (#BUG-37) and expanded RTL rendering to Arabic and other right-to-left languages (Hebrew, Urdu, Farsi).
9. **Constructive Vision Behavior**: Refined vision guardrails to provide constructive situational guidance (helping users take clear photos or troubleshooting camera state) rather than negative refusal rules.
10. **Dynamic EMR Practitioner Mapping**: Replaced hardcoded prompt nurse names with dynamic EMR lookup values from `get_available_support_times`.
11. **Phone & Identity Session Memory**: Integrated global/Australian phone validator with ADK session state memory (`tool_context.state`) to eliminate redundant prompts (#BUG-46).
12. **Gemini 3+ Models & ADK 2.0 Tech Environment**: Enforced Gemini 3+ policy for all Flash models (`gemini-3.1-flash-live-preview`, `gemini-3-flash`), updated Python runtime spec to Python 3.13+ (managed via `uv`), and updated SDK specs to `google-adk>=2.0.0` and `google-genai>=2.0.0`.

---

## 2. Specification Comparison Matrix

| ID | Domain / Feature | Original Spec (`product.md`) | Current Implemented Codebase | Proposed Draft Spec (`spec_draft.md`) | Triage Action / Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **D-1** | **Project Purpose** | General demo mention | Interactive public event / customer showcase app | Explicit Public Event & Customer Showcase Demo Scope (Not Production Code) | 🟢 **Spec Updated (`spec_draft.md`)** |
| **D-2** | **Health Endpoint** | `/health` endpoint documented in `app/health.py` | Route missing from `@app` in `app/main.py` | Explicit `@app.get("/health")` mounted route | 🟢 **Tracked as `#BUG-55`** |
| **D-3** | **Live AI Models** | Legacy Gemini models (`gemini-2.5-flash-native-audio`) | `gemini-live-2.5-flash-native-audio` | Gemini 3 BIDI Live (`gemini-3.1-flash-live-preview`) + Gemini 3 Unary (`gemini-3-flash`) | 🟢 **Spec Updated (`spec_draft.md`)** |
| **D-4** | **Multilingual ASR & RTL** | Static language hints (`en-AU`, `ar`) | Dynamic `AudioTranscriptionConfig()` | Zero-config dynamic ASR + RTL layout for Arabic, Hebrew, Urdu, Farsi | 🟢 **Spec Aligned (`#BUG-37`)** |
| **D-5** | **Legacy UI Checkboxes** | Removal specified in cleanup track | `#enableProactivity` & `#enableAffectiveDialog` still in `index.html` header | Deprecated legacy controls removed from header | 🟢 **Tracked as `#BUG-56`** |
| **D-6** | **Agent Architecture** | Monolithic prompt | ADK 2.0 Router + 4 Sub-Agents + Direct Fast-Path Tools | ADK 2.0 Multi-Agent Router (`cch_concierge_router`) | 🟢 **Proposed Spec Master Update** |
| **D-7** | **Development Workflow** | General TDD guidelines | SDD + pytest for structural changes + user sign-off | Specification-Driven Development (SDD) + mandatory user sign-off for Med+ items | 🟢 **Proposed Spec Master Update** |
| **D-8** | **Prompting & Caching** | Unstructured prompt | Shared persona module (`persona.py`) | Hybrid Markdown & XML tagging, `CCH_SHARED_PERSONA`, positive guidance, Gemini Prompt Caching | 🟢 **Proposed Spec Master Update** |
| **D-9** | **Document Scanner & Vision** | Video streaming camera | Guided A4 viewfinder + single snap + JPEG persistence | Constructive situational vision rules + JPEG persistence + camera trigger | 🟢 **Proposed Spec Master Update** |
| **D-10** | **Clinical SOAP Export** | Not specified | Endpoint `@app.post("/api/session/soap_note")` + `#soapModal` | REST API + Paper Modal UI Export | 🟢 **Proposed Spec Master Update** |
| **D-11** | **Session State Memory** | Basic conversation history | ADK `tool_context.state` identity persistence | Persistent patient/phone context across sub-agents | 🟢 **Proposed Spec Master Update** |
| **D-12** | **Sub-Agent Telemetry** | Not specified | `time.perf_counter()` latency logging | Sub-agent delegation latency target (≤ 0.5s / 500ms) | 🟢 **Proposed Spec Master Update** |
| **D-13** | **Medical Glossary** | Not specified | HealthDirect integration planned in Track 4 | Planned Future Enhancement (Track 4) | 🟢 **Proposed Spec Master Update** |
| **D-14** | **Python & Tech Environment** | Python 3.10 | Python 3.13 (`.venv`) | Python 3.13+ managed via `uv`, GCP Cloud Run / Agent Engine | 🟢 **Proposed Spec Master Update** |
| **D-15** | **SDK Dependencies** | `google-adk>=1.32.0` | `google-adk>=1.32.0` | `google-adk>=2.0.0`, `google-genai>=2.0.0` | 🟢 **Proposed Spec Master Update** |

---

## 3. Discrepancy Review & Triage Recommendations

### Recommendation 1: Adopt Updated Draft Master Specification (`conductor/spec_draft.md`)
- **Justification**: Incorporates user feedback regarding event showcase demo scope (not production code), SDD project workflow, unit testing policy for structural changes, user manual sign-off gate for Med+ items, XML/Markdown hybrid prompting, Gemini Prompt Caching (`CachedContent`), Gemini 3 Flash model policy (`gemini-3.1-flash-live-preview`, `gemini-3-flash`), updated SDK versions (`google-adk>=2.0.0`, `google-genai>=2.0.0`), constructive vision rules, RTL language scope, dynamic EMR practitioner mapping, planned future enhancements, Python 3.13+ runtime, and GCP technical specs.

### Recommendation 2: Address Outstanding Technical Debt Bugs
- **`#BUG-55`**: Mount `@app.get('/health')` in `app/main.py`.
- **`#BUG-56`**: Remove legacy header checkboxes from `app/static/index.html`.
- **`#BUG-58` / `#BUG-59`**: Verify frontend WebSocket event handling for `request_document_scan` tool calls during document steps.

### Recommendation 3: Proceed to Track 4 (Medical Glossary) & Track 5 (2FA)
- **Justification**: Core multi-agent routing and document scanning foundation (Track 3) is verified complete with all unit tests passing.
