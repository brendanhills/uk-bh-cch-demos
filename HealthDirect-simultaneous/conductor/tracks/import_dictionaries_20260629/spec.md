# Specification: Ingest & Import HealthDirect Medical Dictionaries

## 1. Overview
This track introduces an automated ingestion and import pipeline to harvest medical and clinical terms from HealthDirect Australia's reference website and integrate them into our dual-layer translation glossary ecosystem. The harvested terms will populate both the **Google Cloud Translation V3 Glossaries** and the **Gemini Live System Prompt Context**.

## 2. Source Material
The pipeline will crawl and scrape the following HealthDirect directories:
- **Medicines**: [https://www.healthdirect.gov.au/medicines](https://www.healthdirect.gov.au/medicines)
- **Conditions**: [https://www.healthdirect.gov.au/health-topics/conditions](https://www.healthdirect.gov.au/health-topics/conditions)
- **Symptoms**: [https://www.healthdirect.gov.au/health-topics/symptoms](https://www.healthdirect.gov.au/health-topics/symptoms)
- **Procedures**: [https://www.healthdirect.gov.au/health-topics/procedures](https://www.healthdirect.gov.au/health-topics/procedures)

## 3. Functional Requirements

### 3.1 Web Harvesting & Extraction Engine
- Implement a scraper to fetch the index pages of the 4 directories.
- Parse the terms (A-Z indexes, links, and term names) from the HTML content.
- Support deep crawling of term definitions (short summaries/descriptions) where possible, ensuring raw content is clean and structured.
- Handle fetch rate-limiting, timeouts, and user-agent configurations robustly.

### 3.2 Glossary Generation & Merging
- Merge newly extracted terms into the local schema `HealthDirect/dictionary/glossary.json`.
- Prevent duplicate entries while preserving any existing translations (Spanish, Vietnamese, etc.) and adding short English descriptions.
- Support translation pre-population using Google Cloud Translation API for Spanish and Vietnamese where terms do not have translations yet.

### 3.3 Google Cloud Translation V3 Glossary Service
- Build a utility to convert `dictionary/glossary.json` into GCS-compatible CSV glossary formats.
- Upload CSV glossary file to standard GCP bucket path (`gs://uk-bh-experiments-argolis-us/HealthDirect/glossaries/`).
- Connect to and update/re-create the V3 Glossary Resource using standard GCP Client libraries (incorporating dual Spanish/Vietnamese glossary formats).

### 3.4 Gemini Live Prompts System Instruction Integration
- Ensure dynamic injection of dictionary mappings directly into the **Gemini Live System Instructions** template.
- Inject terms when starting a session, mapping English terms to Spanish and Vietnamese equivalents.

### 3.5 Automated Testing
- Deliver unit/integration tests with >80% coverage under `tests/test_import_glossary.py` for crawler, CSV generator, and Translation API interactions.
