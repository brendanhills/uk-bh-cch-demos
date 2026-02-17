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

### 1. Start the ADK Web Server (Technical View)
*Open a new terminal tab* and run:
```bash
uv run adk web . --port 8503
```
*Open `http://127.0.0.1:8503` in your browser.*

### 2. Select the Agent
*   In the top-left dropdown, ensure **`loan_manager`** (or `agents`) is selected.

### 3. Key Features to Demonstrate
*   **The Orchestrator**: Show how `loan_manager` delegates to sub-agents.
*   **The Trace**: Expand the "Reasoning Trace" to show the step-by-step logic.
*   **Tool Calls**: Point out specific tool executions like `investigator_agent` calling `analyze_document`.

### 4. Interactive Walkthrough Scenarios

> [!NOTE]
> **Data Handling**: The agent uses the `applicant_id` to look up "Basic Info" (Income, Employer) from its internal records (`applicants.json`), simulating a backend lookup of a submitted application. 
> *   If the data is found, it proceeds (Scenarios 1-4).
> *   If data is missing, it asks the user (Scenario 5).
> *   Loan Amount and Purpose must be provided in the prompt (simulating the web form submission).

Use these prompts to demonstrate different agent behaviors.

**Scenario 1: Happy Path (Sarah)**
> "Assess loan for applicant 12345. Requesting $10,000 for Debt Consolidation."
*   **Attributes**: Strong credit, sensible amount.
*   **Expected Result**: ✅ **APPROVE**.

**Scenario 1b: Over-Leveraged (Sarah - High DTI)**
> "Assess loan for applicant 12345. Requesting $50,000 for Home Improvement."
*   **Attributes**: Same applicant, but higher amount pushes DTI too high.
*   **Expected Result**: ❌ **DENY** (Excessive DTI).

**Scenario 2: High Earner Exception (David)**
> "Assess loan for applicant 12346. Requesting $100,000 to buy a yacht."
*   **Attributes**: High Income ($175k). Large loan but within limits.
*   **Expected Result**: ✅ **APPROVE** (High Earner).

**Scenario 4: Borderline Case (Gary - Escalation)**
> "Assess loan for applicant 12348. Requesting $15,000 for Debt Consolidation."
*   **Attributes**: 620 Score, High DTI, Recent late payment.
*   **Expected Result**: ⚠️ **ESCALATE** (Requires Manual Review).

**Scenario 5: Missing Information (Jane)**
> "Assess loan for applicant 12349. Requesting $5,000 for Personal use."
*   **Attributes**: No stated income in profile.
*   **Expected Result**: ❓ **ASK USER** (Agent should ask for income details rather than deny).

**Tip**: You can follow up individual decisions with:
> "Why did you make that decision?"
---

## 📝 Key Files to Show (Optional)

If someone asks "How does it work?", show them:
1.  **`config.py`**: "This is where we define the brain." (Shows Model selection).
2.  **`loan_approval_agent/agent.py`**: "This is the Commander." (Shows the Orchestrator setup).
3.  **`loan_approval_agent/sub_agents/policy_expert/prompt.py`**: "This is the Rulebook." (Shows how we instruct it to cite specific policies).
