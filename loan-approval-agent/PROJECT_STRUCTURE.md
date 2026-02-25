# Loan Agent Project Structure

This project has been refactored into a modular architecture to support local simulation, security (DLP), and a clear separation of concerns.

## 📂 1. external_services/
Simulates external APIs and data sources. These modules are "outside" the agent's trust boundary.

- `credit_bureau.py`: Simulates Equifax/Experian. Returns credit reports.
- `employment_registry.py`: Simulates Workday/TWN. Returns income/tenure.
- `fraud_service.py`: Simulates Fraud.net. checks for identity risk.
- `confluence/`: Stores PDF policy documents (Rule of Law).
- `data/`: JSON files for Applicants (`applicants.json`) and Scenarios (`scenarios.json`).
- `simulation_utils.py`: Centralized latency control (`LATENCY_MODE`).

## 🤖 2. loan_agent/
The core AI Agent logic (Google Cloud ADK).

- `agent.py`: The Main Orchestrator (`LoanManager`).
- `config.py`: Central configuration (Models, Latency, Project ID).
- `tools/`:
    - `tool_dispatcher.py`: **MCP-Lite Pattern**. Maps tool names to implementations.
    - `intake.py`: Handles initial application storage.
    - `doc_analyzer.py`: **Multimodal** Paystub analysis using Gemini Vision.
    - `credit_bureau.py`, etc.: Wrappers that call `external_services` + Security Layer.
- `utils/`:
    - `dlp_guardian.py`: **Security**. Redacts PII (SSN, Email) using Cloud DLP (or Regex fallback).
    - `token_vault.py`: Tokenizes sensitive IDs before logging.
    - `audit_logger.py`: Centralized logging to `data/audit_logs/events.jsonl`.
    - `model_client.py`: **Resilience**. Smart fallback (Gemini 3 -> 2.5).
- `sub_agents/`: Specialized agents (`investigator`, `policy_expert`, `underwriter`).

## 🖥️ 3. demo_frontend/
The User Interface (Streamlit).

- `app.py`: The main dashboard.
- Features:
    - **Intake Form**: auto-fill from `scenarios.json`.
    - **Chat Interface**: Talk to the Loan Manager.
    - **File Uploader**: Upload Paystubs/Bank Statements for analysis.
    - **Live Audit Log**: See what the agent is thinking/doing in real-time.
    - **Decision PDF**: Download the final compliance record.

## 🚀 How to Run

1. **Install Dependencies**:
   ```bash
   uv sync
   ```

2. **Setup Environment**:
   - Copy `.env.example` to `.env`.
   - Set `GOOGLE_CLOUD_PROJECT`.
   - Run `gcloud auth application-default login` if using Cloud APIs (DLP, Gemini).

3. **Run Demo**:
   ```bash
   uv run streamlit run demo_frontend/app.py
   ```

## 🧪 Testing & Verification

- **CLI Runner**: `uv run python loan_agent/cli_runner.py` (End-to-End flow in terminal).
- **DLP Test**: `uv run python scripts/test_dlp.py`.
- **Latency Control**: Toggle `REALISTIC` vs `TESTING` in the UI sidebar.
