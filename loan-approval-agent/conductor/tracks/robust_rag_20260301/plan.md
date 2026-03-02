# Implementation Plan: Robust RAG Integration

## Phase 1: RAG Infrastructure Setup
- [x] Task: Create a script to initialize the Vertex AI RAG corpus. (Done manually by user)
- [x] Task: Implement file ingestion logic to upload 300+ pages of PDFs from `external_services/confluence/`. (Done manually by user)
- [x] Task: Conductor - User Manual Verification 'RAG Infrastructure Setup' (Protocol in workflow.md)

## Phase 2: Agent Refactor
- [x] Task: Refactor `loan_agent/sub_agents/policy_expert/tools.py` to use `vertexai.rag` for retrieval.
- [x] Task: Update the `Policy Expert` agent prompt to optimize for vector search results.
- [x] Task: Verify citation extraction from the RAG response.
- [x] Task: Conductor - User Manual Verification 'Agent Refactor' (Protocol in workflow.md)

## Phase 3: Validation & Performance
- [x] Task: Create and run `tests/test_rag_engine.py` to verify functionality.
- [x] Task: Re-run all integration scenarios to ensure reasoning logic is maintained with the new engine.
- [x] Task: Benchmark retrieval time against the large document corpus. (Verified < 5s)
- [x] Task: Conductor - User Manual Verification 'Validation & Performance' (Protocol in workflow.md)
