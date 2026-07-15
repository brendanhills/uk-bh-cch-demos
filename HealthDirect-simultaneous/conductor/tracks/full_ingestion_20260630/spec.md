# Specification: Full Dictionary Ingestion & Production Registry

## Overview
Perform a complete, exhaustive scrape of all alphabetical index listings (A-Z) from the HealthDirect directories. This task runs the self-healing robust pipeline end-to-end to import all clinical terms, pre-translate them, ground them using search context, and register the updated glossary in production. 

To ensure the crawl only needs to run **once**, GCS will serve as the absolute source of truth. The local workspace will support downloading and synchronizing the pre-computed glossary directly from GCS to bypass re-scraping and re-translating.

## Functional Requirements
1. **Exhaustive Crawl:** Crawl all 26 alphabetical sub-pages for Condition, Medicines, Symptoms, and Procedures directories on HealthDirect Australia.
2. **Bulk GCP Translation:** Translate all newly scraped terms to Spanish and Vietnamese using Google Cloud Translation V3.
3. **Exhaustive Search Grounding:** Perform automated search grounding on all translated terms that are missing grounding context using Gemini 3.5 and the Google Search Tool.
4. **Data Synchronization & Backups:** Export and save progressive updates locally to `glossary/glossary.json` and `glossary/glossary.csv`.
5. **GCS & GCP Registration:** Upload the final multilingual glossary CSV and JSON files to GCS so they can be retrieved instantly. Recreate the immutable GCP Translation Glossary resource in production.
6. **GCS Sync/Download Support:** Add an argument (e.g. `--download-gcs`) to the import script to seamlessly pull the compiled dictionary from GCS into the local environment, ensuring that the scraping and translation pipeline never has to be rerun by downstream developers or systems.

## Acceptance Criteria
- No data loss occurred during the full migration (verified via progressive JSON/CSV commits).
- The exported CSV contains all translated terms formatted with standard translation headers (`en, es, vi`).
- The GCP Translation V3 Glossary is successfully updated and available for active interpreter prompts.
- A developer can run `import_glossary.py --download-gcs` to successfully download the latest pre-compiled glossary from GCS, instantly populating the local workspace.
