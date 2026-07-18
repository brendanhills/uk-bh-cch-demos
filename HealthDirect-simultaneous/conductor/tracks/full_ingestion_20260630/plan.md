# Plan: Full Dictionary Ingestion & Production Registry

## Phase 1: GCS Sync Support Implementation

- [x] Task: Add GCS Download command support to import script
    - [x] Add the `--download-gcs` command-line argument to `import_glossary.py`.
    - [x] Implement a function to download `glossary.json` and `glossary.csv` from GCS (using `google-cloud-storage` client library) to local `glossary/` folder.
    - [x] Handle missing remote files or credentials gracefully with clear developer feedback.
- [x] Task: Write tests verifying GCS Sync behavior
    - [x] Add unit tests simulating/mocking GCS download and verifying that files are correctly saved to the local workspace.
- [x] Task: Conductor - User Manual Verification 'Phase 1: GCS Sync Support Implementation' (Protocol in workflow.md)

## Phase 2: Operational Ingestion, Idempotency & GCS Verification

- [x] Task: Implement/Verify incremental state checkpointing and idempotency
    - [x] Ensure that `scrape_state.json` is actively loaded, updated, and flushed after *each* successful alphabetical page scrape to track URL coverage.
    - [x] Add idempotency checks to translation and grounding routines to bypass already processed terms based on current `glossary.json` contents.
    - [x] Add tests verifying that interrupting and restarting `import_glossary.py` results in zero redundant network/API operations.
- [x] Task: Implement synonym auto-scraping and formal/informal nesting
    - [x] Implement parenthetical splitting in scraper/cleaner to capture both clinical/formal names and colloquial/informal synonyms (e.g., `ear infection (otitis media)`).
    - [x] Update translation and data saving routines to structure synonyms into nested `{ "formal": "...", "informal": [...] }` dictionaries under the standard translation schema.
    - [x] Write unit tests verifying that synonyms are correctly scraped, nested in JSON, and flattened in CSV output.
- [x] Task: Execute full scraping, translation, and search-grounding run (multi-invocation test)
    - [x] Run `import_glossary.py` targeting all sub-directories. 
    - [x] Interrupt the run intentionally, then restart it to verify seamless, idempotent pickup from the saved checkpoint state.
    - [x] Allow the run to complete to 100% directory coverage.
    - [x] Verify that all terms are successfully merged into the local database without loss.
- [x] Task: Complete GCS Upload & GCP Translation Glossary Recreation
    - [x] Run GCS upload for both local CSV and JSON glossary files.
    - [x] Recreate and register the GCP Translation V3 glossary in production.
    - [x] Verify that the GCP Glossary is fully active.
- [x] Task: Validate single-run resilience (Clean environment sync check)
    - [x] Back up and remove local `glossary/glossary.json` and `glossary/glossary.csv`.
    - [x] Run `import_glossary.py --download-gcs` to sync assets from GCS.
    - [x] Confirm local files are perfectly restored and identical to the backups.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Operational Ingestion, Idempotency & GCS Verification' (Protocol in workflow.md)
