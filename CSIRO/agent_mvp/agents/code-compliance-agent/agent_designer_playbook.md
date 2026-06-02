# CSIRO Security Compliance Agent: 3-Way Playbook

This master playbook provides the precise instructions, specifications, and testing recipes for the three versions of the CSIRO Security Compliance Agent.

---

## 🗺️ 3-Tier Agent Matrix

| Version | Host Environment | Core Technology | Integration / Tools | Grounding Data |
| :--- | :--- | :--- | :--- | :--- |
| **V1: Agent Designer** | GC Vertex AI Agent Designer | Pure-Prompt (Visual Flow) | Visual Canvas Node Input / Output | System Instructions & few-shots |
| **V2: Agent Builder** | GC Vertex AI Agent Builder | Generative Playbook + OpenAPI | `Get_Repository_Diff`, `Lookup_Exceptions_Registry` | Grounded search Data Store (SSDS) |
| **V3: ADK Framework** | Local Developer Environment | Python `google-adk` 2.x | Registered `FunctionTool` objects | Loaded local policy markdown file |

---

## 🛡️ Version 1: Agent Designer (No-Code Prompt-Based)

### Quick Start:
1. Open the Google Cloud Console and navigate to **Vertex AI Agent Builder**.
2. Click **Create Agent** -> Select **Single-step agent** (or create a custom Workflow node).
3. Under **Instructions**, paste the copy-pasteable prompts from [version_1_agent_designer_prompts.md](file:///home/brendanhills/dev/uk-bh-experiments/CSIRO/agent_mvp/agents/code-compliance-agent/version_1_agent_designer_prompts.md).
4. Run testing scenarios directly in the right-hand **Preview** simulator.

---

## 🧱 Version 2: Agent Builder (Low-Code Playbook-Based)

This version uses generative playbooks to dynamically route tasks, call REST APIs via OpenAPI specs, and query connected search data stores for grounding.

### Step 1: Create the Playbook Agent
1. In Vertex AI Agent Builder, click **Create Agent** -> Select **Playbook**.
2. Under **Instructions (Goal & Steps)**, copy and paste the markdown goal and steps from [version_2_agent_builder_playbook.md](file:///home/brendanhills/dev/uk-bh-experiments/CSIRO/agent_mvp/agents/code-compliance-agent/version_2_agent_builder_playbook.md).

### Step 2: Register OpenAPI Tools
1. Navigate to the **Tools** section in the sidebar.
2. Click **Create Tool** -> Set name to `Get_Repository_Diff` -> Choose **OPENAPI** -> Paste the YAML from [get_repository_diff_spec.yaml](file:///home/brendanhills/dev/uk-bh-experiments/CSIRO/agent_mvp/agents/code-compliance-agent/tools_openapi_specs/get_repository_diff_spec.yaml).
3. Click **Create Tool** -> Set name to `Lookup_Exceptions_Registry` -> Choose **OPENAPI** -> Paste the YAML from [lookup_exceptions_spec.yaml](file:///home/brendanhills/dev/uk-bh-experiments/CSIRO/agent_mvp/agents/code-compliance-agent/tools_openapi_specs/lookup_exceptions_spec.yaml).
4. Attach both tools to your Playbook Agent in the main designer pane.

### Step 3: Configure Grounding Data Store
1. Click **Data Stores** -> **Create Data Store** -> Select **Cloud Storage** or **File Upload** and upload [security_policy_ssds.md](file:///home/brendanhills/dev/uk-bh-experiments/CSIRO/agent_mvp/agents/code-compliance-agent/security_policy_ssds.md).
2. Attach this Data Store to your playbook to give the model real-time, zero-hallucination semantic search capabilities over the SSDS document.

---

## 🐍 Version 3: ADK Framework (Code-Based Python Agent)

This version runs on your local machine using the Python Agentic Development Kit (ADK) and can be fully run, debugged, and visualized with the visual developer tool.

### Step 1: Launch the Native ADK Web Companion
To interact with the agent in the browser, view tool traces, and visually debug reasoning steps:
```bash
cd agents/code-compliance-agent
uv run adk web .
```
This opens the local web workspace (typically at `http://localhost:8080` or similar) where you can select the `security_analyst` agent, type prompts, and observe execution traces.

### Step 2: Verify in the Enterprise Portal Dashboard
To run the agent within the unified multi-agent portal environment:
1. In Terminal 1, run the **Security Agent**:
   ```bash
   cd agents/code-compliance-agent && uv run adk api_server --port 8081 .
   ```
2. In Terminal 2, run the **Geopolitical Agent**:
   ```bash
   cd agents/geo-agent && uv run adk api_server --port 8082 .
   ```
3. In Terminal 3, run the **Enterprise Portal**:
   ```bash
   cd enterprise-portal && uv run python main.py
   ```
4. Access the portal at `http://localhost:8080`.

---

## 🧪 Testing Scenarios and Expected Outcomes

Use the following three test scenarios to verify that all three agent versions behave in a consistent, compliance-aligned manner.

### Scenario A: Unsafe SQL Concatenation & Hardcoded Credentials
- **Commit ID / Input**: `commit-secrets`
- **Expected Outcome**:
  - Agent detects **CRITICAL** violations for:
    1. Section 3.1 (hardcoded database password and Slack API key).
    2. Section 3.4 (broken hash algorithm `md5` used for session tokens).
  - Agent produces a detailed markdown audit report including line context and remediation code (recommending `os.environ` dynamic loading and `hashlib.sha256`).

### Scenario B: AI Model Serialization Violation
- **Commit ID / Input**: `commit-ai-model`
- **Expected Outcome**:
  - Agent detects **CRITICAL** violations for:
    1. Section 3.3 (AI Model Security: loading a legacy executable `.pkl` file via Python's `pickle` library).
    2. Section 2.1 (Critical Project exposure: references strategic "Project Genesis" in a public repository).
  - Agent blocks deployment and escalates to the Technical Design Authority (TDA).
  - Remediation suggests transitioning to `safetensors.torch.load_file`.

### Scenario C: Fully Compliant PR
- **Commit ID / Input**: `commit-safe`
- **Expected Outcome**:
  - Agent detects no violations.
  - Returns a bold **COMPLIANT** status and approves the pull request.
