# Track Specification: HealthDirect Medical Glossary & Term Translation Support

## Overview
Integrates the HealthDirect pediatric/medical terminology glossary from `~/dev/uk-bh-experiments/HealthDirect/live-translate/simultaneous/glossary/` into the Cymbal Children's Hospital assistant. This enables Jennie to naturally explain complex medical jargon found in discharge documents using clear, empathetic, informal layman explanations in English, Arabic, and Hindi.

## Functional Requirements
1. **Medical Glossary Module (`app/glossary.py`)**:
   - Port/adapt the medical glossary data structure (`glossary.json` / terms database) into a lightweight Python lookup module.
   - Support bidirectional term lookups for formal clinical terms (e.g., *otitis media*, *febrile convulsing*, *gastroenteritis*) and their corresponding informal layman terms in:
     - **English**: Formal term $\rightarrow$ `informal_english` (e.g., *otitis media* $\rightarrow$ *"middle ear infection"*).
     - **Arabic**: Formal term $\rightarrow$ Arabic formal & informal translations.
     - **Hindi**: Formal term $\rightarrow$ Hindi formal & informal Devanagari translations.
2. **Context-Aware Prompt Integration**:
   - Update `CCH_SYSTEM_INSTRUCTION` in `app/google_search_agent/agent.py` with medical explanation guidelines:
     - *"When medical jargon or formal clinical terms appear in discharge documents or EMR records (e.g., otitis media, pyrexia, analgesic), naturally use the informal layman translation to explain the formal term to the family in their preferred language (English, Arabic, or Hindi)."*
     - Adapt explanation complexity to match the user's communication style.
3. **Glossary Highlight & Visual Cue Helper (`app/glossary_highlighter.py`)**:
   - Provide term matching logic to highlight medical terms in chat transcript bubbles or console logs.

## Acceptance Criteria
1. When a discharge document contains formal clinical terms (e.g., *otitis media*), Jennie's speech and text output naturally state the informal layman term (e.g., *"otitis media, which is a middle ear infection"*).
2. For Arabic interactions, formal terms are explained using Arabic informal terms (e.g., *التهاب الأذن الوسطى* $\rightarrow$ *التهاب الأذن*).
3. For Hindi interactions, formal terms are explained using Hindi informal terms in Devanagari script.
4. Unit tests in `tests/test_glossary.py` verify term lookups across English, Arabic, and Hindi.
