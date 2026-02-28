# User Acceptance Testing (UAT) Checklist

This checklist maps the requirements from `demo_task.txt` to the verification steps for the Loan Agent Refactor.

## 1. Core Workflow
- [ ] **Intake**: User can submit a loan application via Streamlit.
- [ ] **Identity Verification**: System accepts valid Gov IDs and rejects invalid ones.
    - [ ] Case: "900-00-1234" (Sarah Speed) -> Success
    - [ ] Case: "Invalid-ID" -> Rejection/Error
- [ ] **Data Gathering**: Agent successfully calls:
    - [ ] Credit Bureau (Simulated)
    - [ ] Employment Registry (Simulated)
    - [ ] Fraud Check (Simulated)
- [ ] **Policy Review**: Agent consults "Lending_Policy_2025.pdf" for rules.
- [ ] **Decision**: Agent outputs a clear Approve/Deny/Escalate decision.

## 2. Advanced Features (Refactor Goals)
- [ ] **Real ID Architecture**: Verify `token_vault` generates tokens and `credit_bureau` detokenizes them.
- [ ] **Multimodal Paystub**: Upload a paystub image and verify `DocAnalyzer` extracts income.
    - [ ] Case: Paystub matches stated income -> Consistency Pass.
    - [ ] Case: Paystub differs -> Consistency Warning.
- [ ] **Privacy (DLP)**: Check `audit_logs/events.jsonl` to ensure NO raw SSNs are visible (only Tokens or Redacted).
- [ ] **Resilience**:
    - [ ] **Latency**: Set `LATENCY_MODE=TESTING` and verify near-instant response.
    - [ ] **High Reasoning**: Verify complex cases (e.g. Sarah $50k) use **Gemini 3.1 Pro (Thinking: HIGH)** for deep policy alignment.
    - [ ] **Service Failure**: Set `simulate_failure=True` in Credit Bureau tool (manual code tweak or flag) and see if Agent handles it gracefully (Escalates or Retries).

## 3. Demo Experience
- [ ] **UI Feedback**: Streamlit shows "Processing..." steps clearly.
- [ ] **Audit Trail**: The final Decision PDF contains the "Audit Trail" section with logs.
- [ ] **Speed**: End-to-end flow is under 30 seconds in `REALISTIC` mode (excluding massive sleep).

## 4. Manual Verification Steps
1. Run `uv run streamlit run demo_frontend/app.py`.
2. Fill form as "Sarah Speed".
3. Upload `tests/data/paystubs/sarah_stub.png` (Need to create this mock later).
4. Submit.
5. Check `data/decisions/*.pdf`.
6. `cat loan_agent/data/audit_logs/events.jsonl` and `grep` for SSN.
