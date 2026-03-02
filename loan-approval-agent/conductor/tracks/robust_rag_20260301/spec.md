# Specification: Robust RAG Integration

## Overview
Implement a robust RAG (Retrieval-Augmented Generation) system for the Policy Expert agent using Vertex AI RAG Engine. This replaces the current manual PDF parsing and keyword search with a scalable, high-performance vector-based retrieval system capable of reviewing 300+ pages of policy documents in seconds.

## Functional Requirements
1.  **Vertex AI RAG Engine Integration**:
    *   Create a RAG corpus in Vertex AI.
    *   Ingest all PDF files from `external_services/confluence/` into the corpus.
    *   Implement asynchronous retrieval from the corpus.
2.  **Accuracy & Performance**:
    *   Replace the current page-by-page keyword search with vector similarity search.
    *   Ensure retrieval is fast enough for a 10-minute live demo.
    *   Support complex queries against large documents (OCC Handbook, Master Policy).
3.  **Explainability**:
    *   Maintain the ability to provide citations (Source, Page/Section) for every retrieved policy.

## Non-Functional Requirements
*   **Scalability**: The system must handle hundreds of pages without performance degradation.
*   **Security**: Ensure the RAG corpus is restricted to the project environment.

## Acceptance Criteria
*   The Policy Expert agent successfully retrieves relevant policy sections from 300+ pages of PDFs.
*   Total retrieval time is less than 5 seconds per query.
*   The system uses Vertex AI RAG Engine as the primary retrieval source.

## Out of Scope
*   Replacing other agent tools (Credit, Fraud, etc.).
*   Major UI redesign beyond the Reasoning Trace labels.
