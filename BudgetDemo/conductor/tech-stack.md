# Technology Stack

This document defines the technology stack for the Australian Budget Analysis Dashboard and Data Extraction Tool.

## 1. Core Platform & Frameworks
* **Programming Language:** Python 3.10+
* **Application Framework:** Streamlit (v1.30+) — Provides a fast, interactive web interface for python data apps.

## 2. Data Processing & Visualization
* **Data Processing:**
  * `pandas` — For reading, cleaning, and manipulating budget CSV/Excel tables.
  * `openpyxl` — Excel file reader engine for parsing the nominal GDP spreadsheet (`.xlsx`).
* **Data Visualization:**
  * `plotly` or `altair` — For rich, interactive financial charts (GDP growth trends, nominal GDP comparisons) with hover states.

## 3. PDF Data Extraction & Parsing
* **Text & Table Extraction:**
  * `pdfplumber` — Highly precise tool for extracting structured tables and text from budget PDF documents.
  * `pypdf` — Light and fast library for general PDF metadata and text reading.

## 4. AI & Natural Language Processing
* **LLM & Embedding API:**
  * `google-genai` or `google-cloud-aiplatform` — Official SDKs to access Google's Gemini models (e.g., `gemini-2.5-flash` or `gemini-2.5-pro`) for high-accuracy text embeddings and semantic Q&A.
* **Vector Indexing & Search:**
  * In-memory semantic search (using cosine similarity on Gemini embeddings) or a lightweight local database like `faiss-cpu` / `chromadb`.

## 5. Development & Deployment Tools
* **Package Management:** `pip` with `requirements.txt`
* **Version Control:** `git`
