# Plan: Full Dictionary Ingestion & Production Registry

## Phase 1: Operational Ingestion & Registry Update
- [ ] Task: Execute full scraping, translation, and search-grounding run
    - [ ] Run `import_glossary.py` targeting all directories without max-letter limits
    - [ ] Verify that all terms are successfully merged into local database without loss
- [ ] Task: Complete GCS Upload & GCP Translation Glossary Recreation
    - [ ] Run CSV upload and GCP Translation V3 glossary recreation
    - [ ] Verify GCP Glossary is registered and active
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)
