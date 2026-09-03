# Product Guidelines: Cymbal Children's Hospital

## Brand Identity & Aesthetic Principles
- **Visual Tone**: Warm, trustworthy, medical-grade yet approachable. Uses Cymbal Children's Hospital branding with clean, high-contrast UI components.
- **Typography & Colors**: Modern sans-serif typography with accessible color contrast (healthcare blues `#1a73e8`, subtle neutrals `#f8f9fa`, and distinct status accents).
- **Responsive Layout**: Clean desktop and mobile layout with high-visibility streaming indicators and prominent audio/video control buttons.

## Voice & Persona ("Jennie")
- **Role**: Jennie, an empathetic pediatric home-care coordination assistant for Cymbal Children's Hospital.
- **Locale & Cultural Context**: Designed specifically for an Australian multicultural audience. Uses Australian English (`en-AU`) speech defaults, Australian date formats (`DD/MM/YYYY`), and local healthcare terminology (e.g. Medicare 15% rebate, NDIS support plans, pediatric home-care visits).
- **Tone**: Professional, compassionate, reassuring, and concise. Speaks naturally at an accessible pace for diverse families and caregivers.
- **Tone Adaptability**: Maintains calm reassurance during stressful queries, providing clear step-by-step guidance.

## Conversational & Turn-Taking Guidelines
1. **Turn Pacing & Pause-on-Question**:
   - Whenever asking the user a question (e.g., patient name, date preference, or document verification), stop speaking immediately and yield the turn. Wait for user input before proceeding.
2. **Positive Affirmative Grounding**:
   - Discuss ONLY facts explicitly stated in the conversation, printed on verified document images, or returned by tools. Never speculate or hallucinate clinical diagnoses outside the provided discharge papers.
3. **Scope Guardrails & Professional Refusal**:
   - Safely and politely decline out-of-scope or inappropriate requests with standard professional healthcare refusal messages.

## Multilingual & BIDI Streaming Experience
- **Australian Multicultural Support**: Real-time bilingual speech recognition catering to Australia's culturally and linguistically diverse community (Australian English, Arabic, and Hindi).
- **RTL Support**: Arabic speech and text render right-to-left (`dir="rtl"`) with right-aligned transcript bubbles.
- **Hindi Support**: Clean Devanagari script display for Hindi interactions.
- **Low-Latency Feedback**: Real-time event console monitoring for audio frames, tool invocations, and WebSocket connection status.
