# Product Definition: Cymbal Children's Hospital - Early Support & Discharge Assistant

## Vision
A real-time, bidirectional streaming AI assistant for Cymbal Children's Hospital built with Google ADK (Agent Development Kit), FastAPI, and Gemini Live API. It provides 24/7 multimodal support (low-latency voice, live camera vision, and text) to assist families with home care plans, discharge paperwork verification, financial subsidy navigation (Medicare/NDIS), and home-care nurse appointment scheduling.

## Target Audience
1. **Public Sector IT Decision Makers & Technical Teams (Demo Audience)**:
   - Government technology leaders, health IT directors, and software engineers evaluating Google Cloud AI, Agent Development Kit (ADK), Vertex AI, and Gemini Live API capabilities for public sector and healthcare transformation.
2. **End Users of the Demo Application**:
   - **Families & Caregivers**: Parents and guardians navigating pediatric hospital discharge instructions and home care management for their children.
   - **Hospital Clinical Teams**: Pediatric nurses, discharge coordinators, and EMR administrators seeking automated support for home-care visit scheduling and post-discharge engagement.

## Core Features
1. **Real-time Bidirectional Streaming (BIDI)**:
   - Low-latency WebSocket audio streaming powered by Gemini Live API (`run_live`).
   - Natural voice conversations with turn pacing and pause-on-question guardrails.
2. **Multimodal Visual Inspection**:
   - Live 720p camera stream processing to inspect printed discharge papers, medication dosages, and wound care instructions.
3. **Conversational EMR Navigation & Nurse Booking**:
   - Automated scheduling of home care visits with specific pediatric nurses (`schedule_home_care_visit`).
   - Dynamic date context injection (`datetime.now()`) for accurate appointment availability checks.
4. **Financial Subsidy Assistance**:
   - Automated calculation and application of Medicare (15% rebate) and NDIS home care subsidies.
5. **Multilingual Accessibility**:
   - Real-time speech recognition and bilingual support for Australian English (`en-AU`), Arabic (`ar`), and Hindi (`hi`), including RTL text layout rendering.

## Success Criteria
- **Demonstration Excellence**: Sub-second audio streaming responsiveness via WebSockets, showcasing cutting-edge Google Cloud AI & ADK streaming capabilities to Public Sector IT decision makers.
- **Accuracy & Safety**: Zero hallucination on single-page vs multi-page document inspection, accurate practitioner scheduling, and professional clinical refusal guardrails.
