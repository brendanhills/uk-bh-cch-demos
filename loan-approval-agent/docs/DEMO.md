# 💰 Loan Approval Agent: 10-Minute Demo Script

This script is optimized for your CE interview. It focuses on the **technical unblockers** (Scaling, RAG Accuracy, Security) and **ROI** (48h to 10s).

---

## 🏗️ The Pitch (Before you click anything)
> "Our customer's bottleneck was a **48-hour manual review cycle**. Underwriters had to manually search 341 pages of PDF policies for every high-value loan. We used the **Google Cloud Agent Development Kit (ADK)** and **Gemini 3.1** to build a multi-agent system that parallelizes investigation and uses **Vertex AI RAG Engine** to automate compliance in seconds."

---

## 🚀 Scenario 1: High-Speed Auto-Approval (Sarah Speed)
**Goal**: Demonstrate parallel tool execution and rapid decision-making.

1.  **Sidebar**: Click `🔄 Start New Scenario`.
2.  **Sidebar**: Expand `👤 Sarah: Debt Consolidation`.
3.  **Action**: Copy the text and paste it into the **FastLoan Portal**.
4.  **Point to UI**:
    - **Audit Trace**: "Watch the **Investigator** calling Credit, Employment, and Fraud services **simultaneously**. ADK handles this orchestration automatically."
    - **Timestamps**: "Note the rounded 0.1s timestamps. Total processing time: under 10 seconds."
5.  **Result**: ✅ **APPROVE**.

---

## 🚨 Scenario 2: API Resiliency (The Outage)
**Goal**: Demonstrate autonomous recovery from system failures.

1.  **Sidebar**: Click `🔄 Start New Scenario`.
2.  **Sidebar**: Toggle **"🚨 Simulate Credit Bureau Downtime"** to **ON**.
3.  **Sidebar**: Click `👤 Sarah: Debt Consolidation` again.
4.  **Action**: Paste into the portal.
5.  **Point to UI**:
    - **Audit Trace**: Show the `CREDIT_CHECK_RETRYING` events. "The agent doesn't crash; it follows an autonomous exponential backoff retry policy."
    - **Live Recovery**: Toggle the downtime **OFF** while the agent is retrying.
    - **Success**: "The moment the dependency restores, the agent picks up and completes the task."
6.  **Result**: ✅ **APPROVE** (after automated recovery).

---

## 📜 Scenario 3: The "RAG" Unblocker (David: Yacht)
**Goal**: Prove the agent is grounded in 300+ pages of PDF, not hardcoded prompts.

1.  **Sidebar**: Click `🔄 Start New Scenario`.
2.  **Sidebar**: Click `👤 David: Yacht Purchase`.
3.  **Action**: Paste into the portal.
4.  **Point to UI**:
    - **Audit Trace**: Look for `📜 consult_policy_docs_complete`.
    - **JSON Payload**: "The **Policy Expert** just reviewed 341 pages. It found **Section 1: High-Value Mandates** which applies to this $100k loan."
5.  **Result**: ✅ **APPROVE** (with detailed policy citations).

---

## 🤝 Scenario 4: Human-in-the-Loop (Gary Escalate)
**Goal**: Show how agents handle borderline cases gracefully.

1.  **Sidebar**: Click `🔄 Start New Scenario`.
2.  **Sidebar**: Click `👤 Gary: Borderline Credit`.
3.  **Action**: Paste into the portal.
4.  **Point to UI**:
    - **Audit Trace**: "Gary has a 640 score. The **Policy Expert** found that this requires 'Manual Review'. The **Underwriter** is now escalating to a human."
5.  **Result**: ⚠️ **ESCALATE** (Generate Decision PDF).

---

## 🔍 Scenario 5: Multimodal Document Analysis (Maria)
**Goal**: Show the agent "reading" real evidence to handle self-employment.

1.  **Sidebar**: Click `🔄 Start New Scenario`.
2.  **Sidebar**: Click `👤 Maria: Business Expansion`.
3.  **Action**: Paste into the portal.
4.  **Agent will identify**: "Self-Employed" status and request a bank statement.
5.  **Action**: Expand **"📤 Upload Documents"** and upload `bank_statement_maria_agility.pdf`.
6.  **Point to UI**: "The **Investigator** uses multimodal Gemini 1.5 to 'read' the PDF, verify business cash flow, and update the DTI calculation live."
7.  **Result**: ✅ **APPROVE**.

---

## 🛠️ Technical Deep Dive: Tool Definitions (JSON)
The ADK autonomously generates these schemas from our Python functions. This is how the LLM "sees" our banking tools:

### DTI Calculation Tool
```json
{
  "name": "calculate_dti",
  "description": "Calculates the Debt-To-Income (DTI) ratio.",
  "parameters": {
    "type": "object",
    "properties": {
      "applicant_id": {"type": "string", "description": "The Token ID of the applicant."},
      "loan_amount": {"type": "integer", "description": "Requested loan amount."},
      "loan_term_months": {"type": "integer", "default": 60}
    },
    "required": ["applicant_id", "loan_amount"]
  }
}
```

### Multimodal Document Tool
```json
{
  "name": "analyze_document",
  "description": "Analyzes an uploaded document (PDF/Image) retrieved from the secure landing zone.",
  "parameters": {
    "type": "object",
    "properties": {
      "file_path": {"type": "string", "description": "The filename of the document to analyze."},
      "query": {"type": "string", "description": "Specific question or data to extract."}
    },
    "required": ["file_path", "query"]
  }
}
```

---

## 📈 Closing ROI Summary
- **Efficiency**: Reduced approval turnaround from **48 hours to 10 seconds**.
- **Accuracy**: 100% grounded in policy (Vertex RAG Engine).
- **Compliance**: PII is masked at the edge (Google Cloud DLP).
- **Scale**: Multi-agent architecture handles 10k daily loans effortlessly.
