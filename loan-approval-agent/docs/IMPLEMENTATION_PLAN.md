# Loan Agent Resilience & Fixes Plan

## Goal
Improve robustness and fix test failures while maintaining realistic behavior (no hallucinated credit scores).

## User Review Required
> [!IMPORTANT]
> **Change of Strategy**: I will **REVERT** the synthetic data generation in `credit_bureau.py` and `employment_service.py`. A real credit bureau does not invent scores.
>
> **Resilience approach**:
> 1. **Data Consistency**: REVERT synthetic data in `credit_bureau.py` and `employment_service.py`.
> 2. **Real ID Architecture**: Transition `applicant_id` to be a **Government ID** (e.g., SSN like `US-SSN-12345`).
>    - **Intake**: Update `demo_app.py` and `intake.py` to REQUIRE the user to provide their Gov ID. The application cannot proceed without it.
>    - **Services**: `credit_bureau.py`, `employment_service.py`, etc., will now lookup records by this Gov ID.
>    - **Validation**: If no record is found for the provided Gov ID, return a **realistic error** (e.g., "Credit Report Not Found"), halting the automated approval. This is the correct "happy path" for invalid data.

## Proposed Changes

### 1. Data Model Migration (Real IDs)
Update all JSON data files to use Gov IDs (SSN format) as primary keys.

#### [MODIFY] [applicants.json](file:///usr/local/google/home/brendanhills/dev/uk-bh-experiments/loan-approval-agent/loan_approval_agent/data/demo_data/applicants.json)
- **Change**: Replace internal IDs (e.g., "12345") with realistic Gov IDs (e.g., `900-00-1234`).
- **Map**:
  - Sarah Speed -> `900-00-1234`
  - David Leverage -> `900-00-5678`
  - Jane Fraud -> `900-00-9999` (Invalid/No Record)

#### [MODIFY] [credit_score.json](file:///usr/local/google/home/brendanhills/dev/uk-bh-experiments/loan-approval-agent/loan_approval_agent/data/external_data/credit_score.json)
- **Change**: Update keys to match new Gov IDs.

### 2. Intake & Agent Logic
Enforce Gov ID collection at the start of the flow.

#### [MODIFY] [demo_app.py](file:///usr/local/google/home/brendanhills/dev/uk-bh-experiments/loan-approval-agent/demo_app.py)
- **Change**: Update `sys_prompt` to explicit instructions: "You MUST collect the applicant's Government ID (SSN) before submitting."
- **Change**: Update `register_application` to accept `gov_id` argument.
- **UI**: Update "Quick Fill" button to populate the Gov ID for the selected scenario.

#### [MODIFY] [intake.py](file:///usr/local/google/home/brendanhills/dev/uk-bh-experiments/loan-approval-agent/loan_approval_agent/tools/intake.py)
- **Change**: Update signature to `register_application(name, income, ..., gov_id)`.
- **Logic**: Use `gov_id` as the primary key.

### 3. Service Updates
Ensure strict lookup by Gov ID.

#### [MODIFY] [credit_bureau.py](file:///usr/local/google/home/brendanhills/dev/uk-bh-experiments/loan-approval-agent/loan_approval_agent/tools/credit_bureau.py)
- **Action**: Ensure it returns `{ "error": "Credit Report Not Found" }` if ID lookup fails. No synthetic data.

#### [MODIFY] [employment_service.py](file:///usr/local/google/home/brendanhills/dev/uk-bh-experiments/loan-approval-agent/loan_approval_agent/tools/employment_service.py)
- **Action**: Ensure it returns `{ "error": "Employment Record Not Found" }`.

### 4. Demo Structure & Requirements Mapping
Align `DEMO.md` with `interview_task.txt`, splitting into Operations (UI) and Technical/Resilience (Backend).

#### [MODIFY] [DEMO.md](file:///usr/local/google/home/brendanhills/dev/uk-bh-experiments/loan-approval-agent/DEMO.md)
- **Part 1: Streamlit (Operations/Speed)**
  - **Scenario 1 (Sarah Speed - Approve)**
    - **Req 1 (Parallel Orchestration)**: "The agent checked Credit, Employment, and Risk in parallel."
    - **Req 4 (Auto-Approve < 5 mins)**: "Auto-approved in seconds, not days."
    - **NFR (Audit Trail)**: Show live audit log in sidebar.
  - **Scenario 2 (Sarah - High DTI Decline)**
    - **Req 2 (Business Rules)**: "Risk Engine flagged DTI > 43%."
    - **Req 3 (Reasoning/Explainability)**: "Decline reason is precise."
  - **Scenario 4 (Gary Escalate - Escalate)**
    - **Req 5 (Seamless Handoff)**: "Generates Case File... human starts at 90% done."

- **Part 2: ADK Web (Technical/X-Factors)**
  - **Scenario 5 (Jane Fraud - Fraud)**
    - **X-Factor (Data Consistency)**: "Stated income ($0) contradicts tax record... proactively blocked."
    - **Req 1 (Fraud API)**: Demonstrates integration.
  - **Scenario 6 (Invalid ID - Resilience)**
    - **Req (Graceful Failure)**: "returned a clear 'Record Not Found' error, halting the process safely."
    - **NFR (Isolation)**: Each session is independent.
  - **Scenario 3 (Maria - Policy Agility)**
    - **X-Factor (Policy-as-Code)**: "Swapped policy doc... agent applies new rules."
    - **Req 2 (Policy Updates)**: "Policy documents change weekly."

## Verification Plan

### Automated Tests
1. Run `uv run pytest` to ensure all tests pass.

### Manual Verification
1. Run `uv run streamlit run demo_app.py` -> Execute Scenarios 1, 2, 4.
2. Run `uv run adk web .` -> Execute Scenarios 5, 6, 3 (via prompt).
