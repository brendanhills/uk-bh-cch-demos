# Initial Concept
I want to build an agent to help me to fill in the ratings and recommendations for a candidate that I have interviewed.

## Target Audience
The primary audience is **recruiters and hiring managers** who need structured, objective summaries of candidate performance to make informed hiring decisions.

## Primary Goals
- **Note Summarization & Structuring:** The core task is to process interview documents (questions, notes, follow-ups) into a structured format for external tools.
- **Evidence-Based Evaluation Support:** Recommend ratings for the candidate against specific rubrics and provide an overall hiring recommendation.
- **Evidence Mapping:** Explicitly link candidate responses and interviewer observations to specific rubrics, questions, and levels.

## Core Features
- **Interview Document Processing:** Analyze raw, unstructured notes, including interview questions, follow-ups, and "good response" benchmarks.
- **Evidence Extraction:** Extract key evidence from "sloppy" notes and map it to specific questions and rubrics.
- **Rubric Recommendation Engine:** Recommend ratings (Poor, Borderline, Solid, Outstanding) against six categories:
    1. Framing ML Problems
    2. Consultative Skills
    3. Cloud Foundations
    4. Building Production ML Pipelines
    5. Building AI-Driven Applications
    6. Architecting ML Solutions
- **Hiring Recommendation Engine:** Suggest an overall hiring decision (Strong Hire to Strong No Hire) with specific level recommendations (L3-L6) and supporting reasoning.
- **Structured Output Generation:** Prepare a four-part report optimized for copy-pasting into web applications.

## Output Format
The agent provides a four-part response:
1. **Question List:** A clean bulleted list of all questions asked.
2. **Recommended Rubric Ratings:** Suggested ratings for the 6 categories, intended as a guide for the interviewer.
3. **Evidence Mapping:** Detailed evidence from the notes, categorized by rubric and linked to the source questions.
4. **Hiring Recommendation:** 
    - **Primary Recommendation:** Decision (Strong Hire, Hire, Leaning Hire, Leaning No Hire, No Hire, Strong No Hire) at the interviewed level (L3-L6).
    - **Alternative Level Recommendations (Optional):** Suggestions for hiring at different levels.
    - **Reasoning:** A clear justification for the overall recommendation and level.
