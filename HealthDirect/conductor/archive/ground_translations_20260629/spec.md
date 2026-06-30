# Specification: Translation Search-Grounding & Validation

## Overview
As clinical terms are scraped from HealthDirect and translated into Spanish and Vietnamese, validating these translations is difficult for non-native speakers. This track adds automated Google Search grounding to verify and provide context for every translated term, storing grounding URLs and search snippets in `dictionary/glossary.json`.

## Functional Requirements
1. **Search Grounding Execution**: Integrate search-grounding directly into `import_glossary.py` as an optional flag or automatic step in `--pipeline`.
2. **Medical Query Construction**: Construct search queries for each translated term using targeted search auxiliary keywords:
   - Spanish: `"<translated_term>" salud OR medicina`
   - Vietnamese: `"<translated_term>" sức khỏe OR y tế OR bệnh`
3. **Search Grounding Integration**: Use our `search_web` or lightweight web query wrapper to find high-quality educational pages.
4. **Metadata Augmentation**: For each term in `dictionary/glossary.json`, update the database schema to store:
   - `Spanish_grounding_url`: URL of the top relevant medical/educational web page found.
   - `Spanish_grounding_snippet`: A short context snippet from that page.
   - `Vietnamese_grounding_url`: URL of the top relevant medical/educational web page found.
   - `Vietnamese_grounding_snippet`: A short context snippet from that page.
5. **Robust Schema Compatibility**: Ensure existing translations, descriptions, and URLs are preserved. If a grounding search fails, fallback gracefully without corrupting the entry.

## Non-Functional Requirements
- **Throttling & API Safety**: Implement rate-limiting/throttling (e.g., small sleeps between queries) to avoid Google Search rate limits.
- **Graceful Error Handling**: Do not let network or search API failures crash the main crawl or pipeline.

## Acceptance Criteria
- Running `uv run import_glossary.py --pipeline` crawls, translates, and then grounds the new/updated translations.
- Grounded metadata is correctly populated in `dictionary/glossary.json`.
- Unit and integration tests cover the search wrapper and database updates.
- Code coverage remains above 80% for the dictionary package files.

## Out of Scope (For Now)
- Generating a side-by-side human-readable Markdown report (to be implemented in a subsequent phase).
