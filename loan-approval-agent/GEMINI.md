# Loan Approval Agent Context

This project is a sophisticated multi-agent system designed for automated loan underwriting, built using the Google Cloud Agent Development Kit (ADK) and Vertex AI.

## Project Overview

- **Purpose**: Automates the complex, regulated workflow of loan approval, including data collection, policy verification, and risk analysis.
- **Main Technologies**: 
    - **Language**: Python 3.12+ (managed with `uv`)
    - **AI Framework**: Google Cloud ADK (`google-adk`)
    - **Security**: Google Cloud DLP (Sensitive Data Protection) for PII masking.
    - **Models**: 
        - **Flash**: `gemini-3.1-flash-preview` for high-speed orchestration and data gathering.
        - **Pro**: `gemini-3.1-pro-preview` with **ThinkingLevel: HIGH** for complex policy reasoning and underwriting.
    - **UI**: Streamlit (for the interactive dashboard).
    - **RAG Engine**: **Vertex AI RAG Engine** (Cloud-native retrieval grounded in GCS).

## Architecture

The system uses a hierarchical multi-agent structure:
- **Loan Manager (Orchestrator)**: The root agent (`loan_agent/agent.py`) using **Gemini 3.1 Flash**. Manages the interaction flow and delegates tasks.
- **Investigator Agent**: Gathers applicant data using **Gemini 3.1 Flash**.
- **Policy Expert Agent**: Performs **Hybrid RAG** (Vertex AI RAG Engine + Local fallback) against 300+ pages of policy PDFs using **Gemini 3.1 Pro (Thinking: HIGH)**.
- **Underwriter Agent (Risk Analyst)**: Synthesizes findings using **Gemini 3.1 Pro (Thinking: HIGH)** to make the final decision with strict policy citations.

## Building and Running

- **Install Dependencies**: 
  ```bash
  uv sync
  ```
- **Run Streamlit Dashboard**: 
  ```bash
  uv run streamlit run demo_frontend/app.py
  ```
- **Run Tests**: 
  ```bash
  uv run pytest
  ```
- **Sync Policy to RAG**:
  ```bash
  uv run python scripts/sync_policy_rag.py
  ```

## Development Conventions

- **Tool Execution**: Always use `uv` to run any Python script or tool (e.g., `uv run ...`).
- **Model Usage**: Mandatory use of Gemini models version 3.1 or higher.
- **Agent Structure**: Agents are defined using `google.adk` and are located in `loan_agent/` and `loan_agent/sub_agents/`.
- **Latency Mode**: Controlled via `LATENCY_MODE` in `.env`. Set to `TESTING` for near-instant responses during development/testing, or `REALISTIC` for demo simulations.
- **Mock Data**: 
    - **External Source**: Standardized mock applicants and IDs (e.g., `900-00-1234` for "Sarah Speed") found in `external_services/data/applicants.json`.
    - **Demo Scenarios**: Presentation scenarios and prompts found in `demo_frontend/data/scenarios.json`.
    - **Internal Logs**: Audit trails stored in `loan_agent/data/audit_logs/`.
- **Policy Documents**: Policy PDFs are located in `external_services/confluence/` and mirrored in the **Vertex AI RAG Corpus**.

## Key Files & Directories

- `loan_agent/agent.py`: Root agent definition.
- `loan_agent/sub_agents/`: Directory containing specialized agents.
- `loan_agent/tools/`: Shared tools for data retrieval, logging, and decision making.
- `demo_frontend/app.py`: Main Streamlit application entry point.
- `loan_agent/utils/dlp_guardian.py`: Cloud DLP integration for PII masking.
- `loan_agent/sub_agents/policy_expert/tools.py`: Hybrid RAG implementation.
