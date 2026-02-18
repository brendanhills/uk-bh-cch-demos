# Loan Approval Agent Demo Script

This script guides you through demonstrating the **Loan Approval Agent**, ensuring you hit all requirements (NFRs, X-Factors) in **10 minutes**.

---

## 🏗️ Architecture: "Real ID"
- **Primary Key**: Government ID (SSN format, e.g., `900-00-1234`).
- **Behavior**: Strict lookup. Invalid IDs return "Not Found" errors (Resilience).
- **Data**: All JSON files migrated to use these IDs.

---

## 🎯 P0: The Core Value (Must Show)
**Time**: 5 Minutes
**Focus**: Speed, Business Rules, Human-in-the-Loop.
**Run**: `uv run streamlit run demo_app.py`
**URL**: `http://localhost:8501`

### 1. Auto-Approval (`sarah_speed`)
*   **Persona**: Sarah Speed (Nurse, $60k, 787 Score).
*   **Aims**: Parallel Orchestration, Auto-Approval (<5 mins).
*   **Action**: Select **"Scenario 1: Sarah (Debt Consolidation)"**. Click **Start**.
*   **📋 Copy/Paste Prompt (Optional)**:
    > process a new loan application for name: Sarah Speed, gov_id: 900-00-1234, income: 59758, employer: City Hospital, amount: 20000, purpose: Debt Consolidation, monthly_payment: 300
*   **Result**: ✅ **APPROVE**.
*   **Talk Track**:
    > "The agent parallelized 3 external API calls (Credit, Employment, Fraud) **and analyzed her uploaded Bank Statements**."
    > "Approved in seconds."

### 2. Explainable Decline (`sarah_decline`)
*   **Persona**: Sarah Speed (Same applicant, higher loan).
*   **Aims**: Business Rules, Explainability.
*   **Action**: Select **"Scenario 1b: Sarah (Home Improvement)"**. Click **Start**.
*   **📋 Copy/Paste Prompt (Optional)**:
    > process a new loan application for name: Sarah Speed, gov_id: 900-00-1234, income: 59758, employer: City Hospital, amount: 50000, purpose: Home Improvement, monthly_payment: 1200, Loan-to-Value: 90%, tenure: 5 years
*   **Result**: ❌ **DENY** (DTI > 43%).
*   **Talk Track**:
    > "Same person, different loan. The Risk Engine flagged DTI > 43% per the 'Responsible Lending' policy."

### 3. Seamless Handoff (`gary_escalate`)
*   **Persona**: Gary Escalate (Borderline Score, High DTI).
*   **Aims**: Human Escalation.
*   **Action**: Select **"Scenario 4: Gary (Borderline)"**. Click **Start**.
*   **📋 Copy/Paste Prompt (Optional)**:
    > process a new loan application for name: Gary Escalate, gov_id: 900-00-3456, income: 60000, employer: Medianville Manufacturing, amount: 25000, purpose: Business, monthly_payment: 300
*   **Result**: ⚠️ **ESCALATE**.
*   **Talk Track**:
    > "Borderline case routed to underwriter. Case file pre-populated. No data re-entry."

---

## 🚀 P1: The "X-Factors" (Key Differentiators)
**Time**: 4 Minutes
**Focus**: Resilience, Data Consistency.
**URL**: `http://localhost:8503` (ADK Web) or use Streamlit if preferred.

### 4. Resilience (`alex_resilience`)
*   **Persona**: **Alex Resilience** (Invalid ID).
*   **Aims**: Graceful API Failure Handling.
*   **Action**: Paste the prompt below.
*   **📋 Copy/Paste Prompt**:
    > process a new loan application for name: Alex Resilience, gov_id: 000-00-0000, income: 50000, employer: Tech Corp, amount: 10000, purpose: personal
*   **Result**: 🛑 **ERROR (Handled)**.
*   **Talk Track**:
    > "Credit Bureau lookup failed (No Record). The agent handled it gracefully."
    > "This pattern also handles **Rate Limits**—if the API throttles us, we queue or fail safely without data loss."

### 5. Data Consistency (`jane_fraud`)
*   **Persona**: Jane Fraud (Fraudster).
*   **Aims**: LLM Cross-Check ("Stated Income $0" vs "No Tax Record").
*   **Action**: Paste the prompt below.
*   **📋 Copy/Paste Prompt**:
    > process a new loan application for name: Jane Fraud, gov_id: 900-00-9999, income: 0, employer: none, amount: 5000, purpose: personal
*   **Result**: 🚩 **FLAGGED**.
*   **Talk Track**:
    > "The LLM detected 'Stated Income $0' contradicts 'No Tax Record'. It blocked the fraud at the gate."

---

## 🌟 P2: If Time Permits (Nice to Have)
**Time**: 3 Minutes
**Focus**: Policy Agility, Security.

### 6. Policy Agility (`maria_agility`)
*   **Persona**: Maria Agility (Entrepreneur).
*   **Aims**: Dynamic Policy Updates (Hot-Swap).
*   **Action**: Rename/Swap Policy PDF (Simulated via prompt or file move).
*   **📋 Copy/Paste Prompt**:
    > process a new loan application for name: Maria Agility, gov_id: 900-00-9012, income: 85000, employer: Marias Designs, amount: 20000, purpose: business, monthly_payment: 500
*   **Result**: ✅ **APPROVE** (Under Growth Policy).
*   **Talk Track**:
    > "We updated the policy live. The agent applied new 'Growth' rules without a single line of code change."

### 7. Security & PII (Stateless Architecture)
*   **Focus**: PII Compliance, PCI-DSS.
*   **Action**: Show code `loan_approval_agent/tools/investigator.py` or `token_vault.py`.
*   **Talk Track**:
    > "To meet **PCI-DSS** and **PII** constraints, the agent is stateless. It only sees Token IDs (`900-00...`) and Risk Signals ('DTI > 40%'). Raw data never leaves the secure vault."

---

## ✅ Verification Results
- **Unit Tests**: Passed (Main suite).
- **Data Integrity**: All JSON files Validated (`900-00-xxxx`).
- **End-to-End**: Validated in both Streamlit and ADK Web.
