# CSIRO Agent MVP: Detailed Architecture & Design

## 1. Overview
The goal is to build a distributed agentic application for CSIRO using the Agentic Development Kit (ADK). The platform will feature an Enterprise Portal, a Security Analyst Agent, and a Geopolitical Research Agent, with built-in "Model Armor" for safety.

## 2. Technical Stack
- **Language:** Python 3.13
- **Dependency Manager:** `uv` (Mandatory)
- **Framework:** `google-adk` (ADK 2.0)
- **API Server:** `FastAPI` (serving agents and the portal)
- **UI:** `Mesop` (for a modern, interactive dashboard)
- **Deployment:** Google Cloud Run (for horizontal scaling)
- **Data & Integrations:**
    - **BigQuery:** For storing agent telemetry and geopolitical datasets.
    - **Google Drive:** For researcher data ingestion (via Drive API).
    - **Vertex AI:** For Gemini 2.0 models and Model Garden access.

## 3. Component Design

### 3.1 Enterprise Portal (The Gateway)
- **Function:** Routes requests, manages sessions, and enforces Model Armor.
- **Model Armor:** Middleware that intercepts prompts and responses. It uses regex for PII/Secret redaction and optionally calls a small Gemini model for "Safety Alignment" checking.
- **Interface:** A Mesop-based dashboard featuring:
    - Chat interface with the Portal Agent.
    - "Model Garden" selection to route queries to third-party models.
    - Monitoring logs for Model Armor triggers.

### 3.2 Security Analyst Agent
- **Function:** Monitors GitHub activity and evaluates security policy adherence.
- **Tools:**
    - `fetch_github_diff`: Simulates fetching commit data.
    - `policy_lookup`: Retrieves the latest security guidelines.
- **Logic:** Compares incoming code changes against hardcoded and dynamic policy documents.

### 3.3 Geopolitical Research Agent
- **Function:** Provides insights on global stability and trade.
- **Tools:**
    - `query_bigquery`: Uses `sqlglot` to translate natural language to SQL for geopolitical datasets.
    - `audio_transcriber`: Simulates processing audio briefings (using `openai-whisper` patterns).
    - `drive_fetcher`: Pulls context from specific Google Drive documents.
- **Onboarding:** Simulates the workflow of a researcher creating and sharing an agent with IM&T.

## 4. Security & Compliance
- All sensitive keywords (e.g., "SECRET_PROJECT_X") will be redacted by Model Armor.
- A2A (Agent-to-Agent) communication will be secured via internal VPC or service-to-service authentication in Google Cloud.

## 5. Implementation Phases (Revised)

### Phase 1: Foundation (Current)
- [x] Workspace initialization with `uv`.
- [x] Project skeletons for Portal and Agents.
- [x] Basic Model Armor implementation.

### Phase 2: Agent Tooling & Data
- Implement `sqlglot`-based BigQuery tool for the Geo Agent.
- Implement GitHub mock tool for the Security Agent.
- Set up Mesop UI base for the Enterprise Portal.

### Phase 3: Integration & Telemetry
- Connect agents via HTTP/A2A.
- Implement OpenTelemetry logging to BigQuery.
- Finalize Model Armor "Block/Redact" UI feedback.

### Phase 4: Deployment
- Dockerize components for Cloud Run.
- Configure Vertex AI Agent Engine for production-grade hosting.
