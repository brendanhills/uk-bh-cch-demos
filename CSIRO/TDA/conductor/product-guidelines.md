# Product Guidelines: TDA Support & Data Generation

## Data Generation Standards
- **High Fidelity:** All synthetic PDFs must include structured content (tables, headings) that mimic real-world supplier documents.
- **Localization:** All data must be localized for Australia:
    - **Currency:** Use AUD.
    - **Addresses:** Use realistic Australian addresses for CSIRO and suppliers.
    - **Tax:** Include GST (10%) where applicable in financial documents.
- **Consistency:** Data across different CSVs and PDFs must be internally consistent to allow for cross-agent validation.
- **Variety:** Include edge cases and "counterfactual" data points to test agent robustness.

## Prompt Engineering Guidelines
- **System Instructions:** Prompts must clearly define the agent's role, its specific "Static Truth" (data sources), and the required output format (e.g., citations, rationale).
- **Security & Governance:** Prompts must enforce the "Agent Gateway" rules, requiring sign-off from relevant agents (like Security) for certain actions.
- **Tone & Style:** Recommended prompts should ensure agents maintain a professional, technical, and objective tone.

## Documentation Standards
- **Schema Mapping:** Document the structure of generated CSVs and PDFs so that prompts can be accurately mapped to data fields.
- **Version Control:** Track changes to prompts alongside changes to the data generator logic.