# Specification: Cloud Agent Support

## Objective
The objective of this track is to support the "Cloud Agent" SME (Subject Matter Expert) within the CSIRO TDA Agent MVP. This involves two primary workstreams:
1. **Synthetic Data Generation:** Creating high-fidelity, realistic cloud provider service agreements (PDF) and FinOps chargeback data (CSV) for AWS, Azure, and GCP.
2. **Prompt Recommendation:** Developing and documenting optimized system prompts for the Cloud Agent to be used in Gemini Enterprise Agent Designer.

## Scope
- **Providers:** AWS, Azure, GCP.
- **Documents:**
  - Service Agreements (PDF): High-fidelity documents with realistic legal/technical language, structured with headings and tables.
  - Invoices (PDF): High-fidelity financial documents with itemized charges, GST, and billing details.
  - FinOps Reports (PDF): High-fidelity executive summaries of cloud spend and usage trends.
  - Security Standards (PDF): High-fidelity documents outlining CSIRO's multi-cloud security and data residency policies.
  - FinOps Chargeback Data (CSV): Monthly cost and usage data, including resource IDs, account names, services, and costs.
- **Prompts:** Recommended system instructions for the Cloud Agent, emphasizing traceability, citations, and the Security Agent sign-off (Agent Gateway).

## Requirements
- **Data Realism:** Generated documents must mimic real-world samples provided by the customer.
- **Traceability:** Agents must be able to cite specific pages/rows in the generated data.
- **Integration:** Data and prompts must be compatible with Gemini Enterprise Agent Designer and NotebookLM.

## Acceptance Criteria
- [ ] Data generators for AWS, Azure, and GCP service agreements are functional and produce high-quality PDFs.
- [ ] FinOps chargeback CSV generator produces consistent and realistic cost data across all three providers.
- [ ] A comprehensive set of recommended system prompts for the Cloud Agent is documented.
- [ ] All code for data generation meets the project's quality gates (>80% coverage, linted, TDD).