# Loan Approval Agent Demo Script

This script guides you through demonstrating the **Loan Approval Agent**, ensuring you hit all requirements (NFRs, X-Factors) in **10 minutes**.

---

## 🏗️ Architecture: "Real ID"
- **Primary Key**: Government ID (SSN format, e.g., `900-00-1234`).
- **Behavior**: Strict lookup. Invalid IDs return "Not Found" errors (Resilience).
- **Data**: All JSON files migrated to use these IDs.

---

## 🚀 Part 1: Streamlit (Operations View)
**Focus**: Speed, Business Rules, Human-in-the-Loop.
**Run**: `uv run streamlit run demo_app.py`
**URL**: `http://localhost:8501`


### 1. Auto-Approval Speed
*   **Persona**: Sarah Jenkins (Nurse, $60k, 787 Score).
*   **Aims**: Parallel Orchestration, Auto-Approval (<5 mins).
*   **Action**: Select **"Scenario 1: Sarah (Debt Consolidation)"**. Click **Start**.
*   **📋 Copy/Paste Prompt (Optional)**:
    > process a new loan application for name: Sarah Jenkins, gov_id: 900-00-1234, income: 59758, employer: City Hospital, amount: 20000, purpose: Debt Consolidation
*   **Result**: ✅ **APPROVE**.
*   **Talk Track**:
    > "The agent parallelized 3 external API calls (Credit, Employment, Fraud) and approved in seconds."

### 2. Explainable Decline
*   **Persona**: Sarah Jenkins (Same applicant, higher loan).
*   **Aims**: Business Rules, Explainability.
*   **Action**: Select **"Scenario 1b: Sarah (Home Improvement)"**. Click **Start**.
*   **📋 Copy/Paste Prompt (Optional)**:
    > process a new loan application for name: Sarah Jenkins, gov_id: 900-00-1234, income: 59758, employer: City Hospital, amount: 50000, purpose: Home Improvement
*   **Result**: ❌ **DENY** (DTI > 43%).
*   **Talk Track**:
    > "Same person, different loan. The Risk Engine flagged DTI > 43% per the 'Responsible Lending' policy."

### 3. Seamless Handoff
*   **Persona**: Gary Gray (Borderline Score, High DTI).
*   **Aims**: Human Escalation.
*   **Action**: Select **"Scenario 4: Gary (Borderline)"**. Click **Start**.
*   **📋 Copy/Paste Prompt (Optional)**:
    > process a new loan application for name: Gary Gray, gov_id: 900-00-3456, income: 60000, employer: Medianville Manufacturing, amount: 25000, purpose: Business
*   **Result**: ⚠️ **ESCALATE**.
*   **Talk Track**:
    > "Borderline case routed to underwriter. Case file pre-populated. No data re-entry."

---

## 🛠️ Part 2: ADK Web (Technical View)
**Focus**: Resilience, Data Consistency, Policy Agility.
**URL**: `http://localhost:8503`

### 4. Data Consistency (X-Factor)
*   **Persona**: Jane Doe (Fraudster).
*   **Aims**: LLM Cross-Check ("Stated Income $0" vs "No Tax Record").
*   **Action**: Paste the prompt below.
*   **📋 Copy/Paste Prompt**:
    > process a new loan application for name: Jane Doe, gov_id: 900-00-9999, income: 0, employer: none, amount: 5000, purpose: personal
*   **Result**: 🚩 **FLAGGED**.
*   **Talk Track**:
    > "The LLM detected 'Stated Income $0' contradicts 'No Tax Record'. It blocked the fraud at the gate."

### 5. Resilience (Graceful Failure)
*   **Persona**: Ghost User (Invalid ID).
*   **Aims**: Graceful API Failure Handling.
*   **Action**: Paste the prompt below.
*   **📋 Copy/Paste Prompt**:
    > process a new loan application for name: Ghost User, gov_id: 000-00-0000, income: 50000, employer: Ghost Corp, amount: 10000, purpose: mystery
*   **Result**: 🛑 **ERROR (Handled)**.
*   **Talk Track**:
    > "Credit Bureau lookup failed (No Record). The agent handled it gracefully instead of hallucinating or crashing."

### 6. Policy Agility (Policy-as-Code)
*   **Persona**: Maria Rodriguez (Entrepreneur).
*   **Aims**: Dynamic Policy Updates (Hot-Swap).
*   **Action**: Rename/Swap Policy PDF (Simulated via prompt or file move).
*   **📋 Copy/Paste Prompt**:
    > process a new loan application for name: Maria Rodriguez, gov_id: 900-00-9012, income: 85000, employer: Marias Designs, amount: 20000, purpose: business
*   **Result**: ✅ **APPROVE** (Under Growth Policy).
*   **Talk Track**:
    > "We updated the policy live. The agent applied new 'Growth' rules without a single line of code change."

---

## ✅ Verification Results
- **Unit Tests**: Passed (Main suite).
- **Data Integrity**: All JSON files Validated (`900-00-xxxx`).
- **End-to-End**: Validated in both Streamlit and ADK Web.
