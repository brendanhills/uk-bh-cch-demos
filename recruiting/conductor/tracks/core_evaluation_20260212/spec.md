# Specification: Core Evaluation Logic

## Goal
Implement a Python-based agent logic that processes raw interview documents and rubrics to produce a structured, four-part evaluation report.

## Requirements
- **Input:** Raw interview notes (containing questions and responses), role/level rubrics.
- **Anonymization:** Automatically replace candidate names/info with "TC" and use "they/them" pronouns.
- **Extraction:** Identify all questions asked and extract literal evidence from notes.
- **Evaluation:** Map evidence to 6 rubrics and recommend ratings (Poor, Borderline, Solid, Outstanding).
- **Recommendation:** Provide a hiring recommendation (Strong Hire to Strong No Hire) with reasoning and level (L3-L6).
- **Format:** Output a bulleted list of questions, rubric ratings, evidence mapping, and the final recommendation.

## Technical Constraints
- Use `google-adk` for agent definition.
- Leverage `gemini-2.5-pro` for analysis and summarization.
- Ensure output is optimized for copy-pasting into external web apps.
