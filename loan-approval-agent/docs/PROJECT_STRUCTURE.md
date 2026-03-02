# Project Re-Architecture Plan

## Goal
Split the monolithic `loan-approval-agent` into 3 distinct, loosely coupled projects to improve clarity and demo realism.

## 1. `external_services/` (The "External World")
Simulates the external environment and 3rd party systems.
*   **Responsibility**: Hosting data and "external" APIs.
*   **Components**:
    *   `credit_bureau_api.py`: Serves credit reports (now using Real IDs).
    *   `employment_registry_api.py`: Serves employment data.
    *   `confluence_integration/`: Hosts the PDF policies (simulating an external KM system).
    *   `policy_docs/`: Moves the PDF files here.
*   **Tech**: Simple Python modules (simulated latency). No complex API server needed.

## 2. `loan_agent/` (The "Core Product")
The actual Agentic application we are building.
*   **Responsibility**: The business logic and AI agents.
*   **Components**:
    *   `agent.py`: The root `LoanManager` agent.
    *   `sub_agents/`: `Investigator`, `PolicyExpert`, `RiskAnalyst`.
    *   `tools/`: *Refactored* to call the `external_services` instead of reading JSON directly.
        *   `tools/credit_connector.py` (Client connector, not implementation).
*   **Tech**: Google Cloud ADK (`google-adk`), Python.

## 3. `demo_frontend/` (The "User Experience")
The interface for the demo.
*   **Responsibility**: Simulation of the "Bank Portal" or "Loan Origination System".
*   **Components**:
    *   `app.py`: The Streamlit dashboard.
    *   `pages/`: Different personas (Applicant, Underwriter).
*   **Tech**: Streamlit.

## Migration Steps
1.  **Setup**: Create the 3 top-level directories.
2.  **Move**:
    -   `data/` -> `external_services/data/`
    -   `tools/*.py` (Logic) -> `loan_agent/tools/`
    -   `demo_app.py` -> `demo_frontend/app.py`
3.  **Refactor**:
    -   Update imports in `loan_agent` to point to the new tool locations.
    -   Update `demo_frontend` to import the `LoanManager` (or call it via API).

## Visual Structure
```
.
├── external_services/   # [PROJECT 1] specific to the simulation
│   ├── data/
│   ├── api.py           # Unified entry point?
│   └── confluence/      # PDF storage
├── loan_agent/          # [PROJECT 2] specific to the AI
│   ├── agents/
│   ├── tools/           # Client tools
│   └── main.py
└── demo_frontend/       # [PROJECT 3] specific to the demo
    └── app.py
```
