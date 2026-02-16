# CEBank International - Mock Compliance System

This is a mock application simulating a proprietary, legacy compliance system for CEBank International. It is designed to be used as a target for a custom connector, for example a Gemini Enterprise Custom Connector.

The system exposes three main data sets via a legacy SOAP API:
1. **Trading Rules**
2. **Regulatory Filings**
3. **Audit Logs**

The system enforces Access Control Lists (ACLs) to simulate real-world document permissions (e.g., HR seeing employee files, Traders seeing their own logs, Compliance Officers seeing cross-desk logs but not HR files). It also simulates legacy authentication by requiring HTTP Basic Auth over the SOAP transport.

## Requirements

- Python 3.10+
- `uv` (for fast and deterministic dependency management)

## Setup

1. **Install Dependencies:**
   Ensure you have `uv` installed. If not, follow instructions at [astral.sh/uv](https://docs.astral.sh/uv/). Then run:
   ```bash
   uv sync
   ```
   Or to just utilize the virtual environment manually:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e .
   ```

2. **Generate Mock Data:**
   Before running the service, generate the internal mock database containing the data and access lists.
   ```bash
   uv run python generate_mock_data.py
   ```
   This will create a `data/mock_db.json` file.

You can start both the SOAP Endpoint and the Streamlit Admin dashboard simultaneously by running:

```bash
uv run python launcher.py
```

Alternatively, you can run just the Streamlit app and manage the SOAP service from the "System Administration" page:
```bash
uv run streamlit run compliance_app.py
```

- **SOAP API WSDL:** `http://0.0.0.0:8000/?wsdl`
- **Streamlit App:** `http://0.0.0.0:8501`

### Authentication Credentials

For your connector demonstration, you can authenticate using one of these test profiles. The app also supports a "Simulated User" context switcher in the sidebar.

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Trader** | `tim.trader`<br>`tina.trader` | `password123` | Can read basic trading rules and their *own* audit logs. Cannot see regulatory filings. |
| **Compliance Officer** | `cathy.compliance`<br>`caleb.compliance` | `password123` | Can read extensive trading rules, regulatory filings, and *all* audit logs. Cannot see HR disciplinary forms. |
| **Human Resources** | `helen.hr` | `password123` | Can see HR disciplinary forms and their own logs. |
| **Investment Banking** | `ian.ibanker` | `password123` | Public-side banker. Has different access from a private-side trader (tests Information Barriers). |
| **Auditor** | `annie.auditor` | `password123` | External/Internal auditor testing role. Can see many regulatory filings. |
| **Executive** | `edward.exec`<br>`catherine.ceo` | `password123` | Top-level role that has access to almost everything, including restricted HR and Confidential SAR filings. |

## Verifying the API Locally

You can manually verify that the authentication and endpoint logic works using the provided client script:

```bash
uv run python connector_app/soap_client.py
```
*(Note: You may need to adjust `connector_app/soap_client.py` to run as a standalone script if you want to test it in isolation, or use `test_pbac.py` for logic verification)*
NOTE: Always run 'uv sync' or 'uv run' manually when starting work.

## Demo Script
For detailed step-by-step instructions on running the demo, see [DEMO_SCRIPT.md](DEMO_SCRIPT.md).
