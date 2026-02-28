# Loan Approval Agent Demo Script

This script guides you through demonstrating the **Loan Approval Agent** in **10 minutes**, focusing on high-impact ROI and the technical unblockers identified in the prompt.

---

## 🏗️ Technical Story: The "Unblocker"
*Before starting, explain the problem:*
> "Our customer had a 48-hour approval delay because underwriters had to manually search 300+ pages of PDF policies for every loan. We used Google Cloud's **Agent Development Kit (ADK)** to build a multi-agent system that parallelizes data gathering and uses **Gemini 3.1 Pro (Thinking: HIGH)** to reason through these policies in seconds, not hours."

---

## 🎯 Demo Walkthrough (10 Minutes)

### Setup
1.  **Launch**: `uv run streamlit run demo_frontend/app.py`
2.  **Verify**: Ensure the right-hand sidebar "Reasoning Trace" is visible.

### 1. The "Happy Path": Auto-Approval Speed
*   **Scenario**: Sarah Speed (nurse, good credit) needs $20,000 for debt consolidation.
*   **Actions**: 
    1.  Sidebar: Expand **Sarah Speed (Approve)**.
    2.  Sidebar: Copy the prompt text.
    3.  Main UI: Paste the prompt into the chat input and hit Enter.
*   **Talk Track**: 
    > "I'm starting the review. Look at the 'Reasoning Trace' on the right. You'll see the **Investigator** calling Credit, Employment, and Fraud APIs **in parallel**. Total execution time? Less than 15 seconds. We just automated 70% of the daily 10,000 applications."
*   **Result**: ✅ **APPROVE**.

### 2. The "Technical Unblocker": High-Value RAG
*   **Scenario**: Same Sarah, but now asking for **$50,000** (Home Improvement).
*   **Actions**: 
    1.  Sidebar: Expand **Sarah Speed (Decline)**.
    2.  Sidebar: Copy the prompt text.
    3.  Main UI: Paste into the chat input and hit Enter.
*   **Talk Track**: 
    > "Sarah is a great applicant, but high-value loans have stricter rules hidden deep in the 2026 Policy PDF. Normally, an underwriter would take 30 minutes to find this. Watch the **Policy Expert** navigate the 300+ pages, find Section 6, and apply the DTI cap."
*   **Result**: ⚠️ **ESCALATE** or ❌ **DENY**.
*   **Check**: Click "View Internal Data" in the trace to show the **Citation** (e.g., Section 6.1).

### 3. "Privacy by Design": Security & DLP
*   **Actions**:
    1.  Open the terminal (or the events.jsonl log).
*   **Talk Track**: 
    > "Compliance is non-negotiable. Notice that although I entered an SSN in the sidebar, our **DLP Guardian** masks this PII (`900-00-xxxx`) before it touches any logs or the agent's reasoning context. We are stateless and PCI-compliant."

---

## ✨ Key Differentiators (CE ROI)
1.  **Parallel Execution**: Investigator hits 3 APIs at once (ADK Tool Parallelism).
2.  **Policy Agility**: We updated the guidelines PDF this morning; the agent adapted *instantly* without a single line of code change.
3.  **Explainability**: Every decision includes a citation to the specific section of the PDF (Regulatory requirement).

---

## ✅ Final Verification
- **Speed**: 48 hours → ~10 seconds.
- **Accuracy**: 100% policy grounding (Zero hardcoded rules).
- **Scalability**: Stateless architecture handles 10k+ requests/day.
