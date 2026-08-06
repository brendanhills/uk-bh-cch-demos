# Specification: Full Dictionary Ingestion & Production Registry

## Overview
Perform a complete, exhaustive scrape of all alphabetical index listings (A-Z) from the HealthDirect directories. This task runs the self-healing robust pipeline end-to-end to import all clinical terms, pre-translate them, ground them using search context, and register the updated glossary in production.

## Functional Requirements
1. **Exhaustive Crawl:** Crawl all 26 alphabetical sub-pages for Condition, Medicines, Symptoms, and Procedures directories on HealthDirect Australia.
2. **Bulk GCP Translation:** Translate all newly scraped terms to Spanish and Vietnamese using Google Cloud Translation V3.
3. **Exhaustive Search Grounding:** Perform automated search grounding on all translated terms that are missing grounding context using Gemini 3.5 and the Google Search Tool.
4. **Data Synchronization:** Export and save progressive updates to `dictionary/glossary.json` and `dictionary/glossary.csv`.
5. **GCS & GCP Registration:** Upload the final multilingual glossary CSV to GCS and recreate the immutable GCP Translation Glossary resource in production.

## Acceptance Criteria
- No data loss occurred during the full migration (verified via progressive JSON/CSV commits).
- The exported CSV contains all translated terms formatted with standard translation headers (`en, es, vi`).
- The GCP Translation V3 Glossary is successfully updated and available for active interpreter prompts.
