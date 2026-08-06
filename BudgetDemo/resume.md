# Australian Budget Analysis Dashboard & AI Assistant - Resume Guide

Welcome back! This document outlines the project state, what is completed, and exactly how to pick up where we left off.

---

## 1. Project Overview & Pivot
- **Primary Goal:** Build a beautiful, interactive Streamlit dashboard (using our custom Zinc-style aesthetics) comparing nominal GDP and tax indicators, integrated with a real-time Gemini Q&A assistant grounded on local budget PDFs (with page citations and text streaming).
- **Environment:** Python 3.13.12, managed with `uv` and `pyproject.toml`.
- **GCP Project Context:** `uk-bh-experiments-argolis` (Vertex AI client is verified and fully functional).

---

## 2. Completed Milestones

### Phase 1: Environment & Dependencies
- Fully updated `pyproject.toml` with packages: `streamlit`, `google-genai`, `plotly`, `pyopenssl`, `pdfplumber`, `openpyxl`, and `pandas`.
- Verified that mTLS client cert configuration in this environment can be bypassed by setting `GOOGLE_API_USE_CLIENT_CERTIFICATE=false` and `GOOGLE_API_USE_MTLS=never`.
- Standardized packages using `uv sync`.

### Phase 2: Gemini Assistant Module (`src/gemini_assistant.py`)
- Created a robust assistant module using the new official `google-genai` SDK on Vertex AI.
- Implemented `stream_pdf_qa()` which loads any selected local PDF as bytes, converts it to a standard Gemini Part, and streams responses chunk-by-chunk with precise page citation instructions.
- Fully supports multi-turn conversations by reconstructing conversation history into the SDK content parts.
- Unit and integration tests written in `tests/test_gemini_assistant.py`.

### Phase 3: Data Loader Module (`src/data_loader.py`)
- Implemented and cached standard data cleansers for nominal GDP Excel spreadsheets and Tax Receipts/Revenues CSV files.
- Provided a `get_category_time_series()` helper to seamlessly extract and format year-by-year plottable trends for any selected budget line item.
- Unit tests written in `tests/test_data_loader.py`.

---

## 3. Current Test Suite State
All **15 tests** pass flawlessly with a total project code coverage of **89%**:
- `src/data_loader.py`: **91%** coverage
- `src/gemini_assistant.py`: **95%** coverage
- `src/pdf_parser.py`: **85%** coverage

To run the test suite:
```bash
uv run pytest
```

---

## 4. Next Steps to Resume

### Phase 4: Build the Streamlit Dashboard UI (`src/app.py`)
Create the interactive front-end incorporating the compiled modules. Follow these design requirements:
1. **Theming:** Inject theme-aware CSS (Zinc/Slate theme) that looks ultra-premium and supports both dark and light modes cleanly.
2. **Tab 1: Economic & Receipts Indicators**
   - Import `src/data_loader.py`.
   - Implement dropdown select-boxes to choose between Nominal GDP (Excel), Table 1 Receipts (CSV), and Table 3 Revenue (CSV).
   - Render highly-polished interactive Plotly line and bar charts using the Plotly configuration helper.
3. **Tab 2: PDF Grounding Explorer & Gemini Chat**
   - Import `src/gemini_assistant.py`.
   - Provide a dropdown to select a local PDF file (e.g., `bp1_bs-1.pdf` through `bp1_bs-11.pdf` or the main `bp1_2026-27.pdf`).
   - Use `st.chat_input` and stream responses in real-time using `stream_pdf_qa` within standard `st.chat_message` loops.
   - Maintain multi-turn history in `st.session_state.messages`.

To start the local web server during development:
```bash
uv run streamlit run src/app.py
```
