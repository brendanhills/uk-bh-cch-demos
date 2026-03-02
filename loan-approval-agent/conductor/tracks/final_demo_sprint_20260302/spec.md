# Specification: Demo Polish & Strategic Roadmap

## Overview
This track addresses final missing requirements from `docs/demo_task.txt`. It focuses on ensuring the system delivers detailed, regulatory-compliant Risk Reports and integrates missing internal data points (ML Scores, Decision History), while providing a robust design framework for enterprise scaling.

## Functional Requirements (Live Demo)
1. **Intelligence & Data Integration**:
   - Implement `get_ml_risk_score` tool (simulates custom ML model returning 0-100).
   - Implement `lookup_historical_decisions` tool (minimal mock for demo personas).
   - Generate mock ML scores and historical data for Sarah, Gary, and Jane.
2. **Enhanced Reasoning Trace (Risk Report)**:
   - Update `Underwriter Agent` to generate a structured Markdown "Risk Analysis Report" using ML and history data.
   - Ensure the report is clearly visible in Streamlit and exported to the Decision PDF.
3. **Resilient "API Failure" Persona**:
   - Update `Investigator Agent` prompt to handle and explain tool failures (e.g., Credit Bureau offline) without crashing.
4. **Conversational Document Intake**:
   - Agent can request a "Bank Statement" in chat if income validation is needed.
   - Provide static mock bank statement PDFs for the demo scenarios.

## Design Requirements (Roadmap / Presentation Only)
1. **Pub/Sub High-Throughput Architecture**:
   - Design an event-driven architecture using **Google Cloud Pub/Sub** to ingest up to 10,000 applications/day and distribute them to worker agents.
2. **Deterministic Rate Limiting**:
   - Design the logic for a centralized rate-limiter service to enforce the 100 calls/minute constraint across external APIs.

## Non-Functional Requirements
- **Safety**: Minimal changes to core orchestration to avoid regression before the demo.
- **Explainability**: 100% of decision logic must be visible in the structured report.
- **Stateless PII Compliance**: Sensitive credit data must not be stored beyond the session lifecycle. No credit data should be persisted to disk or external databases.

## Acceptance Criteria
- [ ] UI and PDF show a "Risk Analysis Report" section with step-by-step logic.
- [ ] Agent correctly identifies and explains an "API Failure" scenario.
- [ ] Agent requests a "Bank Statement" during the Jane Fraud scenario.
- [ ] Production Roadmap document is ready for presentation.
