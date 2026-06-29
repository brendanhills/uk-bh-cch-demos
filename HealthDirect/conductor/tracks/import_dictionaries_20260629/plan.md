# Implementation Plan: Ingest & Import HealthDirect Medical Dictionaries

## Phase 1: Web Scraping & Local Dictionary Ingestion
- [x] Task: Web Scraper and Page Parser (84cc7bb)
    - [x] Write failing unit tests for scraping the HealthDirect Australia pages (Medicines, Conditions, Symptoms, Procedures) and verifying parsed structures.
    - [x] Implement robust scraping/crawling logic in `import_glossary.py` to harvest terms and short descriptions from the index pages of the 4 directories.
    - [x] Handle fetch rate-limiting, error handling, custom User-Agents, and timeouts elegantly.
- [x] Task: Glossary Merging and De-duplication (84cc7bb)
    - [x] Write failing unit tests verifying de-duplicated merging of scraped terms into `dictionary/glossary.json`.
    - [x] Implement the merging utility that reads existing entries, merges newly crawled terms, keeps existing human translations, and populates new terms with English descriptions.
- [x] Task: Pre-Translation Service for New Terms (84cc7bb)
    - [x] Write tests verifying that newly found terms are translated using Google Cloud Translation API.
    - [x] Implement bulk pre-translation (translating English terms to Spanish and Vietnamese) for newly added words in `import_glossary.py`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Ingestion & Local Dictionary' (Protocol in workflow.md)

## Phase 2: GCP Translation V3 Glossary Registry
- [x] Task: CSV Export & GCS Upload
    - [x] Write tests for converting `glossary.json` into Translation V3 equivalent multi-lingual CSV formats.
    - [x] Implement a utility in `import_glossary.py` that formats and exports the local glossary json to a CSV file.
    - [x] Write tests for uploading the exported CSV to the target GCS bucket at `gs://uk-bh-experiments-argolis-us/HealthDirect/glossaries/`.
    - [x] Implement GCS upload logic using the GCP Storage Python client library.
- [x] Task: Cloud Translation V3 Glossary Resource Registry
    - [x] Write unit/integration tests to verify registration and recreation of GCP Translation V3 Glossary resources.
    - [x] Implement Translation API V3 calls to create or update/re-create the multi-lingual glossary using `google-cloud-translate`.
- [x] Task: Conductor - User Manual Verification 'Phase 2: GCP V3 Glossary Registry' (Protocol in workflow.md)

## Phase 3: Gemini Live Prompt Integration & End-to-End CLI Demo
- [x] Task: Gemini Live Instruction Injection
    - [x] Write tests confirming that terms from `dictionary/glossary.json` are properly formatted and injected as terminology mapping tables in Gemini's Live system instructions.
    - [x] Ensure `get_system_instruction` or equivalent system prompt manager correctly formats and injects these mappings dynamically based on the active target language.
- [x] Task: End-to-End CLI Scraper Demo & Verification
    - [x] Run the complete pipeline command to crawl new terms, translate them, update `dictionary/glossary.json`, upload CSV to GCS, and register with the GCP translation service.
    - [x] Complete automated tests under `tests/test_import_glossary.py` verifying crawler mock responses, CSV generation, and Google Translation client mocks to guarantee >80% overall test coverage.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Prompt Integration & CLI Demo' (Protocol in workflow.md)
