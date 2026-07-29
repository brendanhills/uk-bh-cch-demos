# Specification: Full Dictionary Ingestion & Production Registry

## Overview
Perform a complete, exhaustive scrape of all alphabetical index listings (A-Z) from the HealthDirect directories. This task runs the self-healing robust pipeline end-to-end to import all clinical terms, pre-translate them, ground them using search context, and register the updated glossary in production. 

To make this intensive operation extremely robust, the pipeline will support **incremental execution** and **complete idempotency**. It will save all intermediate states, allowing a single full run to be split across multiple invocations without duplicating API costs or reprocessing crawled data. Once completed to 100% coverage, the final glossary is uploaded to GCS as the permanent download/sync source of truth.

## Functional Requirements
1. **Exhaustive Crawl with Checkpointing:** Crawl all 26 alphabetical sub-pages for Condition, Medicines, Symptoms, and Procedures directories on HealthDirect Australia. The crawl progress must be checkpointed locally (via `glossary/scrape_state.json`), enabling the scraper to resume from where it was interrupted.
2. **Idempotent Bulk Translation:** Translate newly scraped terms using Google Cloud Translation V3. Translation requests must be strictly idempotent: already translated terms present in the local database/glossary must be bypassed to avoid redundant API expenses.
3. **Idempotent Search Grounding:** Perform automated search grounding on terms missing grounding context using Gemini 3.5 and the Google Search Tool. Already grounded terms must be skipped.
4. **Data Synchronization & Backups:** Save progressive updates immediately to `glossary/glossary.json` and `glossary/glossary.csv` after each alphabetical page is processed, ensuring zero data loss on unexpected termination.
5. **GCS & GCP Registration:** Upon 100% completion of the index listings, upload the compiled multilingual glossary CSV and JSON files to GCS and recreate the immutable GCP Translation Glossary resource in production.
6. **GCS Sync/Download Support:** Maintain a `--download-gcs` option in the import script to pull the compiled dictionary from GCS into the local environment, ensuring that other developers can download the fully pre-compiled assets instantly.
7. **Synonym Parsing & Formal/Informal Nesting:** Detect parenthetical patterns like `primary_term (synonym)` in crawl results (e.g., `middle ear infection (otitis media)` or `amoxil (amoxicillin)`). Automatically split these into formal clinical keys and informal/colloquial aliases. During translation, translate both formal and informal components and structure them into nested `{ "formal": "...", "informal": [...] }` dictionaries under our standard translation schema.

## Acceptance Criteria
- No data loss occurred during the full migration (verified via progressive JSON/CSV commits).
- The pipeline is fully idempotent: running `import_glossary.py` repeatedly does not perform duplicate scrapes, translations, or search grounding requests.
- Scraped parenthetical terms are correctly parsed and split into formal and informal parts.
- The resulting `glossary.json` contains nested formal/informal dictionaries conforming to our strict translation schema.
- The exported CSV flattens the formal/informal nested dictionary keys into clear, readable text values (`formal: ... | informal: ...`).
- The GCP Translation V3 Glossary is successfully updated and available for active interpreter prompts.
- A developer can run `import_glossary.py --download-gcs` to successfully download the latest pre-compiled glossary from GCS, instantly populating the local workspace.
