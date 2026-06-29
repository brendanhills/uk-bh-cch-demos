# Implementation Plan: Ingest & Import HealthDirect Medical Dictionaries

## Phase 1: Web Scraping & Local Dictionary Ingestion
- [ ] Task: Web Scraper and Page Parser
    - [ ] Write failing unit tests for scraping the HealthDirect Australia pages (Medicines, Conditions, Symptoms, Procedures) and verifying parsed structures.
    - [ ] Implement robust scraping/crawling logic in `import_glossary.py` to harvest terms and short descriptions from the index pages of the 4 directories.
    - [ ] Handle fetch rate-limiting, error handling, custom User-Agents, and timeouts elegantly.
- [ ] Task: Glossary Merging and De-duplication
    - [ ] Write failing unit tests verifying de-duplicated merging of scraped terms into `dictionary/glossary.json`.
    - [ ] Implement the merging utility that reads existing entries, merges newly crawled terms, keeps existing human translations, and populates new terms with English descriptions.
- [ ] Task: Pre-Translation Service for New Terms
    - [ ] Write tests verifying that newly found terms are translated using Google Cloud Translation API.
    - [ ] Implement bulk pre-translation (translating English terms to Spanish and Vietnamese) for newly added words in `import_glossary.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Ingestion & Local Dictionary' (Protocol in workflow.md)

## Phase 2: GCP Translation V3 Glossary Registry
- [ ] Task: CSV Export & GCS Upload
    - [ ] Write tests for converting `glossary.json` into Translation V3 equivalent multi-lingual CSV formats.
    - [ ] Implement a utility in `import_glossary.py` that formats and exports the local glossary json to a CSV file.
    - [ ] Write tests for uploading the exported CSV to the target GCS bucket at `gs://uk-bh-experiments-argolis-us/HealthDirect/glossaries/`.
    - [ ] Implement GCS upload logic using the GCP Storage Python client library.
- [ ] Task: Cloud Translation V3 Glossary Resource Registry
    - [ ] Write unit/integration tests to verify registration and recreation of GCP Translation V3 Glossary resources.
    - [ ] Implement Translation API V3 calls to create or update/re-create the multi-lingual glossary using `google-cloud-translate`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: GCP V3 Glossary Registry' (Protocol in workflow.md)

## Phase 3: Gemini Live Prompt Integration & End-to-End CLI Demo
- [ ] Task: Gemini Live Instruction Injection
    - [ ] Write tests confirming that terms from `dictionary/glossary.json` are properly formatted and injected as terminology mapping tables in Gemini's Live system instructions.
    - [ ] Ensure `get_system_instruction` or equivalent system prompt manager correctly formats and injects these mappings dynamically based on the active target language.
- [ ] Task: End-to-End CLI Scraper Demo & Verification
    - [ ] Run the complete pipeline command to crawl new terms, translate them, update `dictionary/glossary.json`, upload CSV to GCS, and register with the GCP translation service.
    - [ ] Complete automated tests under `tests/test_import_glossary.py` verifying crawler mock responses, CSV generation, and Google Translation client mocks to guarantee >80% overall test coverage.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Prompt Integration & CLI Demo' (Protocol in workflow.md)
