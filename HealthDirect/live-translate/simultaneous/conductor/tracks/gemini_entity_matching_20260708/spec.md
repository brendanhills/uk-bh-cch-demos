# Specification: Contextual Clinical Entity Highlighting with Gemini NLU

## Overview
This track replaces regular-expression-based clinical term matching and highlighting with a context-aware system powered natively by Gemini's Natural Language Understanding (NLU). By utilizing passive constraints in translation and transcription system instructions, the Live model will automatically annotate medical terms using HTML/XML-like tags in the streaming output, which the client parses and highlights in the UI.

## Scope & Requirements

### Functional Requirements
1. **System Instruction Injection**: Update the server to automatically append Clinical Term Annotation rules to the system instructions sent to the Gemini Live session.
2. **Clinical Concept Identification**: The prompt instructs Gemini to detect symptoms or conditions from the Australian Medical Glossary (including conjugated, plural, or contextually equivalent terms) and wrap them in `<clinical-term term="[English Canonical Name]">...</clinical-term>` tags.
3. **Contextual Disambiguation**: The model must only tag a term if it is contextually used as a clinical symptom/condition (e.g., tagging "cold" in "the child has a cold", but not in "it is cold outside").
4. **Client-Side Progressive Parsing**: Update `main.js` to parse these XML tags in incoming transcripts and replace them with standard interactive highlighted `<a>` and `<span>` elements, preserving all hover tooltip translations, medical references, and click triggers.
5. **Robust Error Handling**: If a tag is truncated or invalidly formatted due to network/model cutoffs, the parser must strip the raw tags gracefully and log the event.

### Non-Functional Requirements
- **Latency**: Zero additional network or inference latency. Highlights must render as part of the streaming transcript chunks.
- **Reliability**: No false-positive highlights on non-clinical usage of common terms.

## Acceptance Criteria
- [ ] System instructions are correctly compiled with the XML annotation rule and glossary references.
- [ ] Gemini output containing clinical terms returns formatted XML tags around those concepts.
- [ ] Client-Side parser parses `<clinical-term>` tags and maps them to interactive UI elements.
- [ ] Clicking on highlighted terms opens the corresponding Healthdirect reference in a new tab.
- [ ] Automated unit tests verify backend prompt compilation and frontend parsing.
