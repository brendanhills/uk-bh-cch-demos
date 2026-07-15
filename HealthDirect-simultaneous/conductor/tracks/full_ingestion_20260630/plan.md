# Plan: Full Dictionary Ingestion & Production Registry

## Phase 1: GCS Sync Support Implementation

- [ ] Task: Add GCS Download command support to import script
    - [ ] Add the `--download-gcs` command-line argument to `import_glossary.py`.
    - [ ] Implement a function to download `glossary.json` and `glossary.csv` from GCS (using `google-cloud-storage` client library) to local `glossary/` folder.
    - [ ] Handle missing remote files or credentials gracefully with clear developer feedback.
- [ ] Task: Write tests verifying GCS Sync behavior
    - [ ] Add unit tests simulating/mocking GCS download and verifying that files are correctly saved to the local workspace.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: GCS Sync Support Implementation' (Protocol in workflow.md)

## Phase 2: Operational Ingestion, Idempotency & GCS Verification

- [ ] Task: Implement/Verify incremental state checkpointing and idempotency
    - [ ] Ensure that `scrape_state.json` is actively loaded, updated, and flushed after *each* successful alphabetical page scrape to track URL coverage.
    - [ ] Add idempotency checks to translation and grounding routines to bypass already processed terms based on current `glossary.json` contents.
    - [ ] Add tests verifying that interrupting and restarting `import_glossary.py` results in zero redundant network/API operations.
- [ ] Task: Execute full scraping, translation, and search-grounding run (multi-invocation test)
    - [ ] Run `import_glossary.py` targeting all sub-directories. 
    - [ ] Interrupt the run intentionally, then restart it to verify seamless, idempotent pickup from the saved checkpoint state.
    - [ ] Allow the run to complete to 100% directory coverage.
    - [ ] Verify that all terms are successfully merged into the local database without loss.
- [ ] Task: Complete GCS Upload & GCP Translation Glossary Recreation
    - [ ] Run GCS upload for both local CSV and JSON glossary files.
    - [ ] Recreate and register the GCP Translation V3 glossary in production.
    - [ ] Verify that the GCP Glossary is fully active.
- [ ] Task: Validate single-run resilience (Clean environment sync check)
    - [ ] Back up and remove local `glossary/glossary.json` and `glossary/glossary.csv`.
    - [ ] Run `import_glossary.py --download-gcs` to sync assets from GCS.
    - [ ] Confirm local files are perfectly restored and identical to the backups.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Operational Ingestion, Idempotency & GCS Verification' (Protocol in workflow.md)
