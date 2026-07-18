# Project Resume & Playbook: CSIRO Agent MVPs

This playbook outlines the logical path to run, test, and complete the four CSIRO Agent MVPs. It combines local codebase configuration with detailed console recipes for Google Cloud Platform (GCP) and the GE Agent Designer.

---

## 🗺️ Logical Flow of Tasks

To achieve the best results, proceed in this order:

```mermaid
graph TD
    Step1[1. Run Local Codebase] -->|Interactively Test| Step2[2. Model Armor & Garden Evaluation]
    Step2 -->|Transition to Console| Step3[3. Configure Google Cloud Console Guardrails]
    Step3 -->|Build Production Agent| Step4[4. Construct Agent in GE Agent Designer]
    Step4 -->|Publish and Host| Step5[5. Share & Monitor on GE Agent Platform]
```

---

## 🛠️ Step 1: Run the Local Web Dashboard (FastAPI + Glassmorphism SPA)

Antigravity has built a **unified, ultra-premium single-page web dashboard** served directly by the Enterprise Portal. It demonstrates all 4 MVPs in a cohesive, visual environment (including dynamic mock data, security audits, Model Armor intercept logs, and an onboarding wizard).

### Local Quick Start:
1. Ensure you have `uv` installed.
2. In terminal 1, run the **Security Agent**:
   ```bash
   cd agents/code-compliance-agent && uv run adk api_server --port 8081 .
   ```
3. In terminal 2, run the **Geopolitical Agent**:
   ```bash
   cd agents/geo-agent && uv run adk api_server --port 8082 .
   ```
4. In terminal 3, run the **Enterprise Portal**:
   ```bash
   cd enterprise-portal && uv run python main.py
   ```
5. Open your browser to **`http://localhost:8080`** to access the premium dashboard.

---

## 📔 Step 2: GCP & GE Agent Designer Playbook (Console Recipes)

Since many production steps must be done in the cloud consoles, use the following clear recipes when configuring your enterprise deployment:

### 🛡️ Recipe A: Creating the Security Compliance Assistant in GE Agent Designer

1. **Open GE Agent Designer:** Navigate to your Agent Console in Google Cloud Vertex AI Agent Builder.
2. **Create New Agent:** Click **"Create Agent"**, select **"Single-step agent"** or the **"New Workflow Mode"**, and name it `security_policy_compliance_assistant`.
3. **Configure System Instructions:** In the **Flow tab** or **Instructions** box, paste the professional guidelines:
   ```text
   You are the professional CSIRO Security Compliance Assistant. Your objective is to audit incoming repository code changes (diffs) against the CSIRO Secure Software Development Standard (SSDS) to determine if any changes require a **Manual Human-in-the-Loop Security Check**.

   Evaluate code changes line-by-line:
   1. Section 3.1: Cryptography Hashing: Any usage of md5 or sha1 without an approved TDA waiver.
   2. Section 3.3: AI Model Security: Any pickle or legacy PyTorch loads.
   3. Section 3.1: Zero-Credential Policy: Suspicious string constants that could be false-positive keys.
   4. Section 3.5: SQL Injection Prevention: Raw string concatenation in database queries.
   5. Section 2.1: Classification: References to Level-3 strategic projects (e.g., "Project Genesis").
   ```
4. **Link OpenAPI Tools:** In the **Tools** section of the designer pane, click **"Add Tool"** and add custom OpenAPI specs for:
   - `Get_Repository_Diff` (fetching pull request diff content).
   - `Lookup_Exceptions_Registry` (verifying active approved TDA security waivers).
5. **Troubleshooting Model Enablement Error:**
   If you receive the error *"No supported models are enabled in the project. Supported models: gemini-3.1-pro-preview Model is required."*:
   - **Region Check:** Ensure your agent is created in the **`us-central1`** region, where preview models are fully supported.
   - **API Enablement:** Verify that the **Vertex AI API** is fully enabled in your Google Cloud Project under **APIs & Services > Library**.
   - **Switch Model:** In the **Agent Settings** panel, switch the model to a stable, generally available model (such as `gemini-1.5-pro` or `gemini-1.5-flash`) if `gemini-3.1-pro-preview` is restricted.
6. **Test:** In the **Preview tab** simulator, run checks on commits like `Analyze csiro-core with PR commit-secrets` to verify compliance logging and manual check escalation.

---

### 🧱 Recipe B: Setting Up Model Armor in Google Cloud Console
1. **Open Vertex AI Console:** Navigate to the Vertex AI dashboard in the GCP Console.
2. **Access Model Armor:** Under the **"Safety"** or **"Model Armor"** menu, click **"Create Security Profile"**.
3. **Define Filters:**
   *   **PII & Secrets:** Enable automatic redaction for common info types (e.g., `EMAIL_ADDRESS`, `IP_ADDRESS`, `CREDENTIALS`, `API_KEY`).
   *   **Blocked Terms:** Under "Custom Dictionaries", add terms like `SECRET_PROJECT_X`, `INTERNAL_ONLY`. Set the action to **"REDACT"** or **"BLOCK"** (returns a fallback message).
   *   **Toxicity & Hate Speech:** Adjust thresholds (Low, Medium, High) depending on CSIRO corporate safety standards.
4. **Generate Profile ID:** Click **"Save"**. Copy the resulting **Security Profile Resource Name** (looks like `projects/.../locations/.../securityProfiles/...`).
5. **Add to Code:** Put this Profile ID in your portal configuration (`enterprise-portal/main.py`) to replace the mock regex engine with the live Vertex AI Model Armor API client.

---

### 🌐 Recipe C: Accessing Third-Party Models in Vertex AI Model Garden
1. **Open Model Garden:** In the GCP Console, go to **Vertex AI** -> **Model Garden**.
2. **Select Model:** Search for third-party models like **Anthropic Claude 3.5 Sonnet** or **Meta Llama 3.1 70B**.
3. **Request Access / Enable:** Click on the model card and click **"Enable"** or **"Subscribe"** (this binds the model APIs to your GCP billing account).
4. **Retrieve API Endpoint:**
   *   For Llama 3.1: Vertex AI will deploy it to a dedicated endpoint. Copy the **Endpoint URL** (e.g., `https://us-central1-aiplatform.googleapis.com/...`).
   *   For Claude 3.5: Enable the Anthropic Vertex AI integration and obtain the location-specific endpoint.
5. **Incorporate into Single Interface:** In your Enterprise Portal chat, requests routed to these third-party models will make authenticated POST calls to these GCP endpoints using the `google-cloud-aiplatform` client library.

---

### 🤝 Recipe D: Agent Onboarding, Sharing, and IM&T Platform Hosting
This recipe simulates a Researcher passing an agent to Information Management & Technology (IM&T) for central governance.

#### Part 1: Researcher Creation (GE Agent Designer)
1. In GE Agent Designer, create a new agent named `Geopolitical_Research_Agent`.
2. Under **Data Stores**, click **"Create Data Store"**.
3. Select **"BigQuery"**: Point it to your GE geopolitical database (APAC and EMEA stability datasets). Use `sqlglot` schemas to structure queries.
4. Select **"Google Drive"**: Connect it to a secure research folder containing PDF reports and briefings.
5. Under **Instructions**, define the tool routing rules: "If the user asks about regional stability, query the BigQuery database. If they ask about historical briefings, search Google Drive."

#### Part 2: Sharing with IM&T
1. Under Agent Settings -> **"Share / Access Control"**, add the IM&T service account or group (e.g., `imt-agent-host@csiro.au`) as **"Viewer"** or **"Editor"**.
2. Click **"Export Agent"** -> choose **"Cloud Storage"** (to export the zip configuration) or use the **"Publish to GE Agent Platform"** feature.

#### Part 3: IM&T Deployment & Hosting (GE Agent Platform)
1. **Import Agent:** The IM&T Administrator logs into the **GE Agent Platform Console**.
2. Click **"Onboard Shared Agent"**, select the exported zip or find the shared agent ID in the shared registry.
3. **Map Control Guardrails:** In the platform settings, select the imported Geopolitical Agent, click **"Assign Guardrails"**, and link the **Model Armor Security Profile ID** created in Recipe B.
4. **Configure Monitoring:** Enable **"Vertex AI Telemetry and Logging"**. This forwards all prompts, tool execution records (BigQuery SQL queries, Drive extracts), and Model Armor blocks to BigQuery tables.
5. **Audit Controls:** In the IM&T Platform Console, inspect the live graphs for:
   *   **Latency Traces:** Ensure average latency is under 3 seconds.
   *   **Cost Metrics:** Monitor total Vertex AI API spend.
   *   **Guardrail Triggers:** Track how many times Model Armor redacted information or blocked out-of-scope prompts (e.g., a user trying to ask the geopolitical agent to write code).
