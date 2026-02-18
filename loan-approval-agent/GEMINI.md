# Loan Approval Agent Context

This project is a sophisticated multi-agent system designed for automated loan underwriting, built using the Google Cloud Agent Development Kit (ADK) and Vertex AI.

## Project Overview

- **Purpose**: Automates the complex, regulated workflow of loan approval, including data collection, policy verification, and risk analysis.
- **Main Technologies**: 
    - **Language**: Python 3.12+ (managed with `uv`)
    - **AI Framework**: Google Cloud ADK (`google-adk`)
    - **Models**: Gemini 2.5/3 (Flash/Pro) via Vertex AI.
    - **UI**: Streamlit (for the interactive dashboard).
    - **Data/Docs**: Local mock databases (JSON) and PDF policy documents (RAG).

## Architecture

The system uses a hierarchical multi-agent structure:
- **Loan Manager (Orchestrator)**: The root agent (`loan_approval_agent/agent.py`) that manages the interaction flow and delegates tasks to specialized sub-agents.
- **Investigator Agent**: Gathers applicant data from mock services (Credit, Employment, Fraud).
- **Policy Expert Agent**: Performs RAG against lending policy PDFs to provide guidance.
- **Underwriter Agent (Risk Analyst)**: Synthesizes findings and makes the final decision (Approve/Deny/Escalate).

## Building and Running

- **Install Dependencies**: 
  ```bash
  uv sync
  ```
- **Run Streamlit Dashboard**: 
  ```bash
  uv run streamlit run demo_app.py
  ```
- **Run Tests**: 
  ```bash
  uv run pytest
  ```
- **Deploy to Vertex AI**: 
  ```bash
  uv run deployment/deploy.py --create
  ```

## Development Conventions

- **Tool Execution**: Always use `uv` to run any Python script or tool (e.g., `uv run ...`).
- **Model Usage**: Mandatory use of Gemini models version 2.5 or higher.
- **Agent Structure**: Agents are defined using `google.adk` and are located in `loan_approval_agent/` and `loan_approval_agent/sub_agents/`.
- **Latency Mode**: Controlled via `LATENCY_MODE` in `.env`. Set to `TESTING` for near-instant responses during development/testing, or `REALISTIC` for demo simulations.
- **Mock Data**: Use the standardized mock applicants and IDs (e.g., `900-00-1234` for "Sarah Speed") found in `loan_approval_agent/data/demo_data/applicants.json`.
- **Policy Documents**: Policy PDFs are located in `loan_approval_agent/data/policy_docs/`.

## Key Files & Directories

- `loan_approval_agent/agent.py`: Root agent definition.
- `loan_approval_agent/sub_agents/`: Directory containing specialized agents.
- `loan_approval_agent/tools/`: Shared tools for data retrieval, logging, and decision making.
- `demo_app.py`: Main Streamlit application entry point.
- `.agents/rules/`: Project-specific AI agent instructions and constraints.
- `docs/`: Technical documentation, including `IMPLEMENTATION_PLAN.md` and `DEMO.md`.
