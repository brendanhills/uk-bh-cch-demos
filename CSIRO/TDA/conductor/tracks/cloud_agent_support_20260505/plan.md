# Implementation Plan: Cloud Agent Support

## Phase 1: Data Generation Infrastructure [checkpoint: fe44a91]

- [x] Task: Implement AWS Service Agreement PDF generator 39f56dc
    - [x] Write unit tests for AWS PDF structure and content 39f56dc
    - [x] Implement PDF generation using `reportlab` with realistic template 39f56dc
    - [x] Verify >80% code coverage 39f56dc
- [x] Task: Implement Azure Service Agreement PDF generator b4371d3
    - [x] Write unit tests for Azure PDF structure and content b4371d3
    - [x] Implement PDF generation using `reportlab` with realistic template b4371d3
    - [x] Verify >80% code coverage b4371d3
- [x] Task: Implement GCP Service Agreement PDF generator 33e0005
    - [x] Write unit tests for GCP PDF structure and content 33e0005
    - [x] Implement PDF generation using `reportlab` with realistic template 33e0005
    - [x] Verify >80% code coverage 33e0005
- [x] Task: Implement Unified FinOps Chargeback CSV generator f62a94d
    - [x] Write unit tests for CSV schema and data consistency (AWS, Azure, GCP) f62a94d
    - [x] Implement CSV generation with realistic billing categories and costs f62a94d
    - [x] Verify >80% code coverage f62a94d
- [x] Task: Implement high-fidelity Invoice PDF generators (AWS, Azure, GCP) 1182167
    - [x] Design realistic invoice templates with tables and GST breakdown 1182167
    - [x] Update generators to support 'Invoice' document type 1182167
    - [x] Verify >80% code coverage 1182167
- [x] Task: Overhaul Service Agreements and Enhance FinOps Reports 049e763
    - [x] Update `pdf_utils.py` to support multi-page flowables for legal documents 049e763
    - [x] Implement 5+ page legal T&C templates for Service Agreements (AWS, Azure, GCP) 049e763
    - [x] Add more granular detail and service-level trends to FinOps Reports 049e763
    - [x] Verify >80% code coverage 049e763
- [x] Task: Implement Security Agent and Standards Data 2b883af
    - [x] Create `scripts/security_generator.py` for high-fidelity Security Standards PDF 2b883af
    - [x] Draft `security_sub_agent.md` prompt 2b883af
    - [x] Update orchestrator and orchestration script to include security 2b883af
    - [x] Verify >80% code coverage 2b883af
- [x] Task: Create data orchestration script 5a4f323
    - [x] Implement script to generate 3-year history using new high-fidelity generators 5a4f323
    - [x] Ensure consistent data between PDFs and CSVs 5a4f323
- [x] Task: Conductor - User Manual Verification 'Data Generation Infrastructure' (Protocol in workflow.md) fe44a91

## Phase 2: Prompt Recommendation [checkpoint: 5627cf3]

- [x] Task: Draft Cloud Agent System Prompt 2167ac0
    - [x] Define role and SME domain expertise 2167ac0
    - [x] Include explicit instructions for traceability and citations 2167ac0
    - [x] Define requirements for Security Agent sign-off (Agent Gateway) 2167ac0
- [x] Task: Create Data Schema Mapping for Prompts 71c124a
    - [x] Document the structure of generated CSVs and PDFs for agent instruction 71c124a
    - [x] Provide examples of how agents should cite specific data points 71c124a
- [x] Task: Conductor - User Manual Verification 'Prompt Recommendation' (Protocol in workflow.md) 5627cf3
