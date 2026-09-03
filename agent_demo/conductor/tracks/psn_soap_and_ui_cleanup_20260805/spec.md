# Track Specification: Clinical SOAP Note Export & UI Feature Clean-Up (PSN Demo)

## Overview
This track implements key feature enhancements for the Public Sector Network (PSN) demo:
1. **Clinical SOAP Note Export & Document Modal (#BUG-23)**: Allows clinicians and parents to generate, preview, copy, and print a formatted clinical SOAP note (Subjective, Objective, Assessment, Plan) upon session completion.
2. **Proactivity & Affective Dialog Enablement (#BUG-35)**: Connects `#enableProactivity` and `#enableAffectiveDialog` UI checkboxes to the session connection parameters, dynamically activating proactive guidance turns and empathetic vocal adaptation in the agent.

## Functional Requirements
- **SOAP Note Backend Endpoint (`/api/session/soap_note`)**:
  - FastAPI endpoint in `app/main.py` that processes session transcript turns and EMR state to return formatted SOAP fields (`patient_name`, `parent_name`, `subjective`, `objective`, `assessment`, `plan`, `soap_markdown`).
- **SOAP Note Document Modal UI (`#soapModal`)**:
  - Add `#soapNoteButton` (`📄 SOAP Note`) in `.input-wrapper` bottom action bar in `app/static/index.html`.
  - Slide-over/modal overlay displaying a medical-grade letterhead document preview.
  - Interactive controls: `📋 Copy to Clipboard`, `🖨️ Print / Save as PDF`, and `❌ Close`.
- **Proactivity & Affective Dialog Wire-Up**:
  - Pass `#enableProactivity` and `#enableAffectiveDialog` state in WebSocket connection payload from `app.js`.
  - When enabled, `app/main.py` dynamically injects:
    - **Proactive Persona Directive**: *"Proactivity Enabled: If the user pauses or is reviewing discharge papers, proactively offer helpful guidance and check if they need assistance."*
    - **Affective Empathy Directive**: *"Affective Adaptation Enabled: Listen carefully to the user's emotional tone, adjusting voice cadence and expressing warmth, patience, and empathetic care when discussing pediatric health concerns."*

## Acceptance Criteria
1. Clicking **`📄 SOAP Note`** in the bottom input bar fetches session data from `/api/session/soap_note` and opens `#soapModal` displaying formatted SOAP sections.
2. Clicking **`📋 Copy to Clipboard`** copies the full text to the clipboard with visual confirmation.
3. Clicking **`🖨️ Print / Save as PDF`** opens the browser print dialog with styled print CSS rules.
4. Toggling `#enableProactivity` and `#enableAffectiveDialog` passes settings to backend and dynamically activates proactive and empathetic agent behavior.
5. Unit tests pass cleanly via `pytest`.
