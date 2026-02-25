# Loan Approval Agent Demo Script

This script guides you through demonstrating the **Loan Approval Agent**, ensuring you hit all requirements (NFRs, X-Factors) in **10 minutes**.

---

## 🏗️ Architecture: "Real ID" & Security
- **Primary Key**: Government ID (SSN format, e.g., `900-00-1234`).
- **Modular Design**: Split into `loan_agent` (Orchestrator) and `external_services` (Simulators).
- **Security**: **DLP Guardian** (`dlp_guardian.py`) sanitizes all PII input/output.


---

## 🎯 P0: The Core Value (Must Show)
**Time**: 5 Minutes
**Focus**: Speed, Business Rules, Human-in-the-Loop.
**Run**: `uv run streamlit run demo_frontend/app.py`
**URL**: `http://localhost:8501`

### 1. Auto-Approval (`sarah_speed`)
*   **Persona**: Sarah Speed (Nurse, $60k, 787 Score).
*   **Aims**: Parallel Orchestration, Auto-Approval (<5 mins).
*   **Action**: Select **"Scenario 1: Sarah (Debt Consolidation)"**. Click **Start**.
*   **📋 Copy/Paste Prompt**:
    ```text
    process a new loan application for 
    name: Sarah Speed, 
    gov_id: 900-00-1234, 
    income: 59758, 
    process a new loan application for
    name: Sarah Speed,
    gov_id: 900-00-1234,
    income: 59758,
    employer: City Hospital,
    amount: 20000,
    purpose: Debt Consolidation,
    monthly_payment: 300
    ```
*   **Result**: ✅ **APPROVE**.
*   **Talk Track- **Underwriter Agent**: Synthesizes all findings and makes the final decision (Approve/Deny/Escalate).
- **Loan Manager**: Orchestrates the entire process.

### 4. Scenario Execution (`demo_task.txt`)
- The **Loan Manager** delegates to the **Investigator**.
- The **Investigator** calls the **Fraud Service** (MOCKED).
- The **Policy Expert** checks the **Policy Documents** (RAG).
- The **Underwriter** makes the final decision.s Rules, Explainability.
*   **Action**: Select **"Scenario 1b: Sarah (Home Improvement)"**. Click **Start**.
*   **📋 Copy/Paste Prompt**:
    ```text
    income: 59758, 
    employer: City Hospital, 
    amount: 50000, 
    purpose: Home Improvement, 
    monthly_payment: 1200, 
    Loan-to-Value: 90%, 
    tenure: 5 years
    ```
*   **Result**: ❌ **DENY** (DTI > 43%).
*   **Talk Track**:
    > "Same person, different loan. The Risk Engine flagged DTI > 43% per the 'Responsible Lending' policy."

### 3. Seamless Handoff (`gary_escalate`)
*   **Persona**: Gary Escalate (Borderline Score, High DTI).
*   **Aims**: Human Escalation.
*   **Action**: Select **"Scenario 4: Gary (Borderline)"**. Click **Start**.
*   **📋 Copy/Paste Prompt**:
    ```text
    process a new loan application for 
    name: Gary Escalate, 
    gov_id: 900-00-3456, 
    income: 60000, 
    employer: Medianville Manufacturing, 
    amount: 25000, 
    purpose: Business, 
    monthly_payment: 300
    ```
*   **Result**: ⚠️ **ESCALATE**.
*   **Talk Track**:
    > "Borderline case routed to underwriter. Case file pre-populated. No data re-entry."

---

## 🚀 P1: The "X-Factors" (Key Differentiators)
**Time**: 4 Minutes
**Focus**: Resilience, Data Consistency, Security.
**URL**: `http://localhost:8501`

### 4. Security & DLP (`DLP Guardian`)
*   **Persona**: Malicious User / Privacy Audit.
*   **Aims**: Verify PII Redaction.
*   **Action**: Look at the **Terminal Output** or **Audit Log** during any run.
*   **Result**: 🛡️ **REDACTED**.
*   **Talk Track**:
    > "Our `DLP Guardian` intercepts every message. It uses Google Cloud DLP (or Regex fallback) to mask SSNs (`900-00-xxxx`) before they hit the logs or non-secure contexts."


### 6. Data Consistency (`jane_fraud`)
*   **Persona**: Jane Fraud (Fraudster).
*   **Aims**: LLM Cross-Check ("Stated Income $0" vs "No Tax Record").
*   **Action**: Paste the prompt below.
*   **📋 Copy/Paste Prompt**:
    ```text
    process a new loan application for 
    name: Jane Fraud, 
    gov_id: 900-00-9999, 
    income: 0, 
    employer: none, 
    amount: 5000, 
    purpose: personal
    ```
*   **Result**: 🚩 **FLAGGED**.
*   **Talk Track**:
    > "The LLM detected 'Stated Income $0' contradicts 'No Tax Record'. It blocked the fraud at the gate."



## ✅ Verification Results
- **Unit Tests**: Passed (Main suite + DLP + Model Fallback).
- **Data Integrity**: All JSON files Validated (`900-00-xxxx`).
- **End-to-End**: Validated in Streamlit.
