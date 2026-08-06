# Plan: Implement core data extraction and parsing for budget PDFs and spreadsheets

This plan implements TDD workflow. Each task requires writing tests before writing the corresponding implementation.

## Phase 1: Environment and PDF Parsing Foundation

- [x] Task: Project initialization and pytest configuration (2385fc5)
    - [x] Create `pyproject.toml` or `requirements.in` configuration specifying dependencies (`streamlit`, `pdfplumber`, `openpyxl`, `pandas`, `pytest`, `pytest-cov`)
    - [x] Install dependencies using `uv`
    - [x] Create a placeholder unit test `tests/test_placeholder.py` and run `pytest` to confirm test suite works
- [x] Task: Extract tables and text from budget PDFs (38b7536)
    - [x] Write unit tests in `tests/test_pdf_parser.py` using sample/actual budget PDF structures to define expected extraction fields and outputs
    - [x] Implement `src/pdf_parser.py` using `pdfplumber` to extract tables and text from PDFs in `data/` directory
    - [x] Verify unit tests pass and code coverage meets targets
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Environment and PDF Parsing Foundation' (Protocol in workflow.md)

## Phase 2: Spreadsheet (Excel/CSV) Parsing

- [ ] Task: Parse Nominal GDP from Excel spreadsheet
    - [ ] Write unit tests in `tests/test_spreadsheet_reader.py` for reading the Nominal GDP data structure from the Excel spreadsheet
    - [ ] Implement nominal GDP extraction logic in `src/spreadsheet_reader.py` using `pandas` / `openpyxl`
    - [ ] Run test suite and verify tests pass
- [ ] Task: Parse and aggregate CSV files
    - [ ] Write unit tests in `tests/test_spreadsheet_reader.py` for reading and merging CSV sheets (`bp1_s5-online_t*.csv`)
    - [ ] Implement CSV loading and merging logic in `src/spreadsheet_reader.py`
    - [ ] Run test suite and verify tests pass
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Spreadsheet (Excel/CSV) Parsing' (Protocol in workflow.md)

## Phase 3: Unified Data Layer & Caching

- [ ] Task: Integrate all sources into a consolidated data interface
    - [ ] Write unit tests in `tests/test_data_layer.py` for the unified data retrieval interface and caching logic
    - [ ] Implement the integration layer in `src/data_layer.py` with Streamlit cache decorators (`st.cache_data`)
    - [ ] Verify test suite and code coverage targets (>80%)
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Unified Data Layer & Caching' (Protocol in workflow.md)
