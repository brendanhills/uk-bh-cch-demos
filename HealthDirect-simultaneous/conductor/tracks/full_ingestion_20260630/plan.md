# Plan: Full Dictionary Ingestion & Production Registry

## Phase 1: GCS Sync Support Implementation

- [ ] Task: Add GCS Download command support to import script
    - [ ] Add the `--download-gcs` command-line argument to `import_glossary.py`.
    - [ ] Implement a function to download `glossary.json` and `glossary.csv` from GCS (using `google-cloud-storage` client library) to local `glossary/` folder.
    - [ ] Handle missing remote files or credentials gracefully with clear developer feedback.
- [ ] Task: Write tests verifying GCS Sync behavior
    - [ ] Add unit tests simulating/mocking GCS download and verifying that files are correctly saved to the local workspace.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: GCS Sync Support Implementation' (Protocol in workflow.md)

## Phase 2: Operational Ingestion, Registration & GCS Verification

- [ ] Task: Execute full scraping, translation, and search-grounding run
    - [ ] Run `import_glossary.py` targeting all sub-directories without alphabetical or quantity limits.
    - [ ] Verify that all terms are successfully merged into the local database without loss.
- [ ] Task: Complete GCS Upload & GCP Translation Glossary Recreation
    - [ ] Run GCS upload for both local CSV and JSON glossary files.
    - [ ] Recreate and register the GCP Translation V3 glossary in production.
    - [ ] Verify that the GCP Glossary is fully active.
- [ ] Task: Validate single-run resilience (Clean environment sync check)
    - [ ] Back up and remove local `glossary/glossary.json` and `glossary/glossary.csv`.
    - [ ] Run `import_glossary.py --download-gcs` to sync assets from GCS.
    - [ ] Confirm local files are perfectly restored and identical to the backups.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Operational Ingestion, Registration & GCS Verification' (Protocol in workflow.md)
