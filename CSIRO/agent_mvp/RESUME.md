# Project Resume: CSIRO Agent MVP

This file serves as a hand-off document to resume work on the Agentic Development Kit (ADK) MVP for CSIRO.

## 🚀 Current Status
- **Architecture:** Distributed Microservices (Enterprise Portal + 2 Specialized Agents).
- **Dependency Management:** Managed via `uv` (strict mandate).
- **Source Control:** Committed and pushed to `origin-clone/main`.
- **Infrastructure:** Framework set up with `google-adk` 2.0 and `FastAPI`.

## ✅ Milestones Completed
1.  **Workspace Initialized:** Created `enterprise-portal`, `agents/security-agent`, and `agents/geo-agent`.
2.  **Environment Setup:** Virtual environments and lockfiles generated for all components using `uv`.
3.  **Model Armor:** Implemented core redaction/blocking logic in the Enterprise Portal.
4.  **Agent Skeletons:** Basic agent logic and `api_server` compatibility established for all agents.
5.  **Conductor Setup:** Initialized implementation tracks and design documentation in the `/conductor` directory.

## 🛠️ Tech Stack Details
- **Python:** 3.13
- **Core Libs:** `google-adk`, `fastapi`, `uvicorn`, `httpx`, `pydantic`.
- **Planned:** `sqlglot` (for NL-to-SQL), `mesop` (for UI).

## 📋 Pending Tasks (Immediate Next Steps)

### Track T002: Agent Tooling & Mock Data
- [ ] **NL-to-SQL:** Add `sqlglot` to `geo-agent` and implement the BigQuery simulation tool.
- [ ] **Security Policy:** Expand `security-agent` with realistic policy rules and GitHub diff analysis.
- [ ] **Data Ingestion:** Implement mock tools for simulated Audio and Google Drive context.

### Track T003: Mesop UI
- [ ] Build the Enterprise Portal dashboard using `Mesop`.
- [ ] Integrate chat interface and Model Armor telemetry logs.

### Track T004: A2A & Telemetry
- [ ] Transition from standard HTTP calls to ADK's A2A protocol.
- [ ] Implement OpenTelemetry (OTEL) logging to BigQuery.

## 💡 Quick Start to Resume
1.  Verify `uv` is installed.
2.  Start agent servers (for testing):
    ```bash
    cd agents/security-agent && uv run adk api_server --port 8081 .
    cd agents/geo-agent && uv run adk api_server --port 8082 .
    ```
3.  Start the portal:
    ```bash
    cd enterprise-portal && uv run python main.py
    ```
