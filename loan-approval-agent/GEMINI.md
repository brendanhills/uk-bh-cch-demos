# Loan Approval Agent Context

This project is a sophisticated multi-agent system designed for automated loan underwriting, built using the Google Cloud Agent Development Kit (ADK) and Vertex AI.

## Project Overview

- **Purpose**: Automates the complex, regulated workflow of loan approval, including data collection, policy verification, and risk analysis.
- **Main Technologies**: 
    - **Language**: Python 3.12+ (managed with `uv`)
    - **AI Framework**: Google Cloud ADK (`google-adk`)
    - **Models**: 
        - **Flash**: `gemini-3-flash-preview` for high-speed orchestration and data gathering.
        - **Pro**: `gemini-3.1-pro-preview` with **ThinkingLevel: HIGH** for complex policy reasoning and underwriting.
    - **UI**: Streamlit (for the interactive dashboard).
    - **Data/Docs**: Local mock databases (JSON) and PDF policy documents (RAG).

## Architecture

The system uses a hierarchical multi-agent structure:
- **Loan Manager (Orchestrator)**: The root agent (`loan_agent/agent.py`) using **Gemini 3 Flash**. Manages the interaction flow and delegates tasks.
- **Investigator Agent**: Gathers applicant data using **Gemini 3 Flash**.
- **Policy Expert Agent**: Performs RAG against policy PDFs using **Gemini 3.1 Pro (Thinking: HIGH)**.
- **Underwriter Agent (Risk Analyst)**: Synthesizes findings using **Gemini 3.1 Pro (Thinking: HIGH)** to make the final decision.

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
- **Deploy to Vertex AI**: 
  ```bash
  uv run deployment/deploy.py --create
  ```

## Development Conventions

- **Tool Execution**: Always use `uv` to run any Python script or tool (e.g., `uv run ...`).
- **Model Usage**: Mandatory use of Gemini models version 3 or higher.
- **Agent Structure**: Agents are defined using `google.adk` and are located in `loan_agent/` and `loan_agent/sub_agents/`.
- **Latency Mode**: Controlled via `LATENCY_MODE` in `.env`. Set to `TESTING` for near-instant responses during development/testing, or `REALISTIC` for demo simulations.
- **Mock Data**: Use the standardized mock applicants and IDs (e.g., `900-00-1234` for "Sarah Speed") found in `loan_agent/data/demo_data/applicants.json`.
- **Policy Documents**: Policy PDFs are located in `loan_agent/data/policy_docs/`.

## Key Files & Directories

- `loan_agent/agent.py`: Root agent definition.
- `loan_agent/sub_agents/`: Directory containing specialized agents.
- `loan_agent/tools/`: Shared tools for data retrieval, logging, and decision making.
- `demo_frontend/app.py`: Main Streamlit application entry point.
- `.agents/rules/`: Project-specific AI agent instructions and constraints.
- `docs/`: Technical documentation, including `IMPLEMENTATION_PLAN.md` and `DEMO.md`.
