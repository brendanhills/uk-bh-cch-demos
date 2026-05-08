# Product Guide: Technical Design Authority (TDA) Agent MVP Support

## Vision
To support the development of CSIRO's TDA Agent MVP (built in Gemini Enterprise Agent Designer) by providing a robust environment for generating realistic synthetic data and developing high-quality prompt recommendations for the SME agents.

## Target Audience
- **Developers and Prompt Engineers:** Using this project to generate test data and refine agent instructions.
- **Stakeholders:** Reviewing the synthetic data and recommended prompts as part of the POC.

## Core Goals
- **Synthetic Data Generation:** Create a realistic and consistent set of PDFs and CSVs for 6 SME agents, localized for CSIRO Australia (AUD currency, Australian addresses, GST).
- **Prompt Recommendation:** Develop and document optimized system prompts for each agent to be used in the Gemini Enterprise Agent Designer.

## Key Features & Roadmap
- **Data Generators:** Python-based scripts to generate domain-specific documents based on sample patterns.
- **Prompt Library:** A collection of recommended system instructions for each of the 6 agents, ensuring consistency and adherence to the TDA requirements.

## Complexity Requirements
- **Data Realism:** Generated data must be high-fidelity to ensure agents can provide accurate citations and grounded recommendations.
- **Prompt Precision:** Prompts must explicitly instruct agents on traceability, governance, and inter-agent collaboration.gent collaboration.