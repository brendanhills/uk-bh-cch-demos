# Specification: Decision History Database

## Overview
Implement a Decision History system to capture and learn from the outcomes of daily loan applications. This system will utilize a dedicated Vector Database (Vertex AI Vector Search) hosted in the Google Cloud project to store sanitized application profiles. To ensure explainability, the detailed, DLP-scrubbed JSON decision reasoning will be attached as metadata to each vector. Data generation will follow an iterative scale-up strategy (100 -> 10,000 -> 100,000 records) to validate the pipeline before incurring larger infrastructure costs.

## Functional Requirements
1. **Dedicated Vector Database Storage:** Provision a Vertex AI Vector Search endpoint in the designated Google Cloud project to act as the persistent historical memory across demo runs.
2. **Explainable Metadata Payloads:** The raw decision output (JSON), including the risk score and the explicit reasoning chain, will be scrubbed of PII and stored directly as a metadata payload attached to its corresponding vector.
3. **Iterative Data Generator Script:** Create a Python script (`scripts/generate_history.py`) to procedurally generate realistic, sanitized historical loan decisions. The script must support parameter-driven sizing to facilitate a phased rollout:
   - *Phase 1 (Validation):* 100 records to test end-to-end vectorization and insertion.
   - *Phase 2 (Performance):* 10,000 records to test basic RAG retrieval speed.
   - *Phase 3 (Demo Scale):* 100,000 records for the final demo corpus.
4. **DLP Ingestion Pipeline:** Create an automated hook at the end of the live underwriting workflow. Every newly finalized decision must be strictly scrubbed using Google Cloud DLP to remove all PII before vectorization and live insertion into the database.
5. **Historical RAG Tooling:** Equip the Underwriter agent with a new tool (`query_decision_history`) to perform Semantic Search. It will vectorize the current applicant's profile, find the top $K$ most similar historical applications, and retrieve their JSON reasoning payloads to justify current decisions.

## Non-Functional Requirements
- **Cost Management:** The data generation strategy is explicitly tiered to minimize vector indexing and storage costs during initial development and debugging.
- **Explainability:** The system MUST surface the historical reasoning (from the metadata payload) alongside any statistical recommendations so human reviewers understand the precedent.
- **Compliance:** Strict adherence to the "no persisting credit data" constraint. The database will only hold mathematically irreversible vectors and DLP-scrubbed JSON outcome tags.
- **Performance:** Vector retrieval must add no more than 1-2 seconds to the overall 5-minute auto-approval SLA.

## Out of Scope
- Full continuous retraining of the separate "Custom ML Risk Model" (the focus here is agentic RAG lookup, not adjusting internal neural network weights).
- Migrating the existing 200+ page policy PDFs into this specific history database.
- Generating the full 18 million record dataset (5 years) until production scale testing is explicitly approved.
