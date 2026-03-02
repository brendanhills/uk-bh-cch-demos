# Deployment Plan (Google Cloud)

## Overview
How to take the `loan-approval-agent` from local development to a production-like environment on Google Cloud.

## Strategy Options

### Option 1: The "Demo Monolith" (Recommended for Simplicity)
Package `external_services`, `loan_agent`, and `demo_frontend` into a **single Docker container** deployed to **Cloud Run**.
*   **Pros**: 
    *   Easiest to deploy (1 artifact).
    *   Zero network latency between components.
    *   Cheapest (1 service).
*   **Cons**: Tightly coupled; doesn't show "microservices" architecture in infrastructure (though code is modular).

### Option 2: Microservices on Cloud Run
deploy 2-3 separate Cloud Run services.
1.  **Frontend Service**: `demo_frontend` (Streamlit).
2.  **Agent Service**: `loan_agent` wrapped in a FastAPI server.
3.  *(Optional)* **External Service**: `external_services` wrapped in FastAPI.
*   **Pros**: Real network boundaries; independent scaling.
*   **Cons**: Higher complexity (auth, service-to-service networking, 3x deployment pipelines).

### Option 3: Vertex AI Agent Engine (The "Google Way")
Deploy the `loan_agent` to **Vertex AI Agent Engine** and the frontend to Cloud Run.
*   **Pros**: Managed agent runtime, built-in reasoning/tracing, integrates with Agent Builder.
*   **Cons**: Requires adhering to specific Agent Engine protocols; less control than raw Python.

## Recommended Path: Phase 0 -> Option 1 -> Option 3
1.  **Phase 0 (Current)**: **Local Machine**. Run everything locally (`streamlit run demo_frontend/app.py`). This is the primary demo environment.
2.  **Phase 1 (Future)**: Deploy as **Option 1 (Monolith)** to get it running on Cloud Run for shared demos.
3.  **Phase 2 (Long Term)**: Refactor `loan_agent` to **Vertex AI Agent Engine**.

## Implementation Steps (Phase 1)
1.  **Containerize**: Create a `Dockerfile` at the root that installs dependencies and runs `streamlit run demo_frontend/app.py`.
2.  **Infrastructure**:
    *   **Artifact Registry**: Store the Docker image.
    *   **Cloud Run**: Run the container (HTTPS).
    *   **Service Account**: Identity for the agent to access Vertex AI (Gemini) and Discovery Engine.
3.  **CI/CD**:
    *   (Optional) Cloud Build trigger on git push.

## Prerequisites
*   GCP Project with billing enabled.
*   APIs enabled: `run.googleapis.com`, `aiplatform.googleapis.com`, `discoveryengine.googleapis.com`.
