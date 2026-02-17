# Loan Approval Agent: Demo Script

This script guides you through demonstrating the **Loan Approval Agent**. It covers two modes:
1.  **Streamlit Dashboard**: A visual, scenario-based demo.
2.  **Interactive Agent (ADK Web)**: A conversational demo showing the agent's reasoning.

---

## 🚀 Part 1: Streamlit Dashboard (Visual Demo)

**Goal**: Show how the agent handles different risk profiles automatically.

### 1. Start the App
Run this command in your terminal:
```bash
uv run streamlit run demo_app.py
```
*Open the provided URL (usually `http://localhost:8501`) in your browser.*

### 2. Scenario 1: Clear Approval (The "Happy Path")
*   **Action**: In the Sidebar, select **"Scenario 1: Clear Approval (High Credit)"**.
*   **Observe**:
    *   Applicant: **Mock Applicant 2505** (High Credit, Low DTI).
    *   Click **"Start Assessment"**.
    *   **Watch the logs**: The agent checks credit (Score > 700), verifies employment (Income verified), and checks policy.
    *   **Result**: ✅ **APPROVE**. The agent might even suggest an interest rate (e.g., Base + 1.5%).

### 3. Scenario 2: Borderline Case (The "Human-in-the-Loop")
*   **Action**: In the Sidebar, select **"Scenario 2: The Unblocker (Borderline)"**.
*   **Observe**:
    *   Applicant: **Mock Applicant 3078** (High Income but questionable factors).
    *   Click **"Start Assessment"**.
    *   **Watch the logs**: The agent gathers data. The Policy Expert might flag a specific rule (e.g., DTI is high, or history is short).
    *   **Result**: ⚠️ **MANUAL_REVIEW**. The agent correctly identifies that it cannot auto-approve and escalates to a human underwriter.

### 4. Scenario 3: Auto-Decline (The "Risk Shield")
*   **Action**: In the Sidebar, select **"Scenario 3: Auto-Decline (High Risk)"**.
*   **Observe**:
    *   Applicant: **Mock Applicant 9850** (Low Credit).
    *   Click **"Start Assessment"**.
    *   **Watch the logs**: The Investigator finds a low credit score (< 640) or high debt.
    *   **Result**: ❌ **DENY**. The Policy Expert cites the specific policy section violated (e.g., "Credit Score < 640").

---

## 💬 Part 2: Interactive Agent (ADK Web)

**Goal**: Show the "Mind of the Agent" – how it thinks, calls tools, and answers questions.

### 1. Start the ADK Web Server
*Open a new terminal tab* and run:
```bash
uv run python -m google.adk.cli web . --port 8503
```
*Open `http://127.0.0.1:8503` in your browser.*

### 2. Select the Agent
*   In the top-left dropdown, ensure **`loan_manager`** (or `agents`) is selected.

### 3. Interactive Walkthrough

**Prompt 1: The Introduction**
> "Hi, who are you and what can you do?"

*   **Observe**: The agent introduces itself as the Loan Manager and mentions its team (Investigator, Policy Expert, Risk Analyst).

**Prompt 2: Starting a Case (Manual IDs)**
> "Assess loan for applicant 9813ee1d"

*   *(Note: `9813ee1d` is a "High Credit" applicant from our mock DB)*
*   **Observe**:
    *   The agent calls `investigator_agent`.
    *   You see the **Tool Calls** in the UI (e.g., `get_credit_report`, `verify_employment`).
    *   It passes the data to `policy_expert_agent`.
    *   It finally calls `risk_analyst_agent` to make the decision.
    *   **Response**: It should return a structured approval decision.

**Prompt 3: Asking for Reasoning**
> "Why was this applicant approved?"

*   **Observe**: The agent recalls the context (Credit Score, DTI) and explains the decision based on the Policy Expert's assessment.

**Prompt 4: Handling Edge Cases (Fraud)**
> "Assess loan for applicant 874796df"

*   *(Note: `874796df` is a "Fraud Risk" applicant)*
*   **Observe**:
    *   The `check_fraud_risk` tool returns a high fraud score.
    *   The agent should immediately **DENY** based on fraud, possibly skipping detailed policy analysis or flagging it as high priority.

---

## 📝 Key Files to Show (Optional)

If someone asks "How does it work?", show them:
1.  **`config.py`**: "This is where we define the brain." (Shows Model selection).
2.  **`loan_approval_agent/agent.py`**: "This is the Commander." (Shows the Orchestrator setup).
3.  **`loan_approval_agent/sub_agents/policy_expert/prompt.py`**: "This is the Rulebook." (Shows how we instruct it to cite specific policies).
