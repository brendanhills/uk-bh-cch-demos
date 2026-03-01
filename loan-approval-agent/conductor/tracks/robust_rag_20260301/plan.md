# Implementation Plan: Robust RAG Integration

## Phase 1: RAG Infrastructure Setup
- [ ] Task: Create a script to initialize the Vertex AI RAG corpus.
- [ ] Task: Implement file ingestion logic to upload 300+ pages of PDFs from `external_services/confluence/`.
- [ ] Task: Conductor - User Manual Verification 'RAG Infrastructure Setup' (Protocol in workflow.md)

## Phase 2: Agent Refactor
- [ ] Task: Refactor `loan_agent/sub_agents/policy_expert/tools.py` to use `vertexai.rag` for retrieval.
- [ ] Task: Update the `Policy Expert` agent prompt to optimize for vector search results.
- [ ] Task: Verify citation extraction from the RAG response.
- [ ] Task: Conductor - User Manual Verification 'Agent Refactor' (Protocol in workflow.md)

## Phase 3: Validation & Performance
- [ ] Task: Re-run `tests/test_scenario_agents.py` to ensure reasoning logic is maintained.
- [ ] Task: Benchmark retrieval time against the large document corpus.
- [ ] Task: Conductor - User Manual Verification 'Validation & Performance' (Protocol in workflow.md)
