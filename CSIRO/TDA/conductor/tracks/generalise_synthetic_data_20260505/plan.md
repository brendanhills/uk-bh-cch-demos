# Implementation Plan: Generalise Synthetic Data Generation

## Phase 1: Core Engine Refactoring

- [ ] Task: Design and implement the `BaseDocumentTemplate`
    - [ ] Abstract header/footer/page numbering logic
    - [ ] Create a unified `StyleManager` for easy branding swaps
- [ ] Task: Implement `SchemaDrivenCSVGenerator`
    - [ ] Allow CSV structure and provider data to be defined in JSON
- [ ] Task: Refactor existing generators (AWS, Azure, GCP) to use the new engine
    - [ ] Verify no regression in output quality for CSIRO

## Phase 2: Metadata & Prompt Integration

- [ ] Task: Create a `CustomerProfile` schema
    - [ ] Include fields for Name, Location, Currency, Addresses, and Industry Vertical
- [ ] Task: Implement `PromptToDocument` bridge
    - [ ] Use LLM calls to generate realistic "Legal T&C" and "Insight" text based on the Customer Profile
- [ ] Task: Demonstrate "One-Click" generation for a new customer
    - [ ] Generate a full set of docs for a fictitious "Global Retail Corp" in the UK

## Phase 3: Validation & Quality Gates

- [ ] Task: Implement generic test suite
    - [ ] Tests that validate output against the provided schema
- [ ] Task: Conductor - User Manual Verification 'Generalisation Framework' (Protocol in workflow.md)
