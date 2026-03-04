# Implementation Plan: Decision History Database

## Phase 1: Infrastructure & Data Caching (Validation Scale)
- [ ] Task: Provision GCS Bucket to act as the development cache for generated historical data
- [ ] Task: Provision Vertex AI Vector Search Index and Endpoint
- [ ] Task: Write failing unit tests for `scripts/generate_history.py`
- [ ] Task: Implement `scripts/generate_history.py` to generate sanitized records and upload them as JSONL to the GCS bucket
- [ ] Task: Implement `scripts/ingest_to_vector_store.py` to pull the cached JSONL from GCS and populate the Vector Search Index
- [ ] Task: Conductor - User Manual Verification 'Infrastructure & Data Caching' (Protocol in workflow.md)

## Phase 2: Agent Tooling (RAG Retrieval)
- [ ] Task: Write failing unit tests for `loan_agent/tools/decision_history.py`
- [ ] Task: Implement `query_decision_history` tool using `google-cloud-aiplatform` to search the index and fetch metadata
- [ ] Task: Update Underwriter Agent prompt in `loan_agent/sub_agents/underwriter/agent.py` to utilize historical RAG for explainability
- [ ] Task: Verify tool execution and reasoning chain in `tests/test_history_tool.py`
- [ ] Task: Conductor - User Manual Verification 'Agent Tooling' (Protocol in workflow.md)

## Phase 3: Live Ingestion Pipeline & DLP
- [ ] Task: Write failing integration tests for the live decision-to-history pipeline
- [ ] Task: Implement live ingestion hook in `loan_agent/agent.py` (Underwriter completion -> DLP -> Vector Store)
- [ ] Task: Verify PII redaction in historical records using `tests/test_history_pii.py`
- [ ] Task: Conductor - User Manual Verification 'Live Ingestion Pipeline & DLP' (Protocol in workflow.md)

## Phase 4: Scaling & Performance
- [ ] Task: Execute `scripts/generate_history.py` to scale the GCS cache to 10,000 and then 100,000 records
- [ ] Task: Re-run `scripts/ingest_to_vector_store.py` to update the Vector Search index with the scaled data
- [ ] Task: Perform load testing on retrieval latency and verify < 2s response time
- [ ] Task: Update `docs/PRESENTATION.md` to showcase the new "Historical Precedent" capability
- [ ] Task: Conductor - User Manual Verification 'Scaling & Performance' (Protocol in workflow.md)
