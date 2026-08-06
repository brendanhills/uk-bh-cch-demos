# Specification: Implement core data extraction and parsing for budget PDFs and spreadsheets

## 1. Overview
The goal of this track is to build python modules that parse, extract, and clean budget data from raw source files located in the `data/` directory. The extracted data will form the backend database/structures for the interactive Streamlit budget dashboard.

All modules must follow strict Test-Driven Development (TDD): unit tests must be written first to verify parsing behavior, and then the parsing code will be implemented.

## 2. Input Data Files (located in `data/`)
- **PDF Files**:
  - `data/bp1_2026-27.pdf`: Contains budget proposal tables and summaries.
  - `data/bp1_bs-*.pdf` (e.g. `bp1_bs-1.pdf` through `bp1_bs-11.pdf`): Specific budget sheets or reports.
  - `data/bp1_notes.pdf`: Explanatory notes.
- **Excel Spreadsheet**:
  - `data/bp1_s2-data-nominal-GDP.xlsx`: Contains nominal GDP data.
- **CSV Spreadsheets**:
  - `data/bp1_s5-online_t1.csv`, `bp1_s5-online_t2.csv`, `bp1_s5-online_t3.csv`: Tables of transactions or metrics.

## 3. Scope of Implementation

### 3.1 PDF Parser (`src/pdf_parser.py`)
- Extract tabular structures from the budget PDFs using `pdfplumber`.
- Identify key budget line items: Department name, planned spend, variance, etc.
- Verify correctness by checking if extracted line items sum to the reported total budget.

### 3.2 Spreadsheet Reader (`src/spreadsheet_reader.py`)
- Parse the nominal GDP data from `data/bp1_s2-data-nominal-GDP.xlsx`.
- Load and combine transactions/tables from the CSV files (`data/bp1_s5-online_t*.csv`).
- Output cleaned Pandas DataFrames with standardized column names and data types (e.g. Year as integer, Spending/GDP as float).

### 3.3 Unified Data Layer (`src/data_layer.py`)
- Integrate data from PDFs, Excel, and CSV sources.
- Provide a caching wrapper (using Streamlit's `@st.cache_data`) to prevent redundant file parsing on dashboard refreshes.

## 4. Verification Plan
- **Unit Tests**:
  - `tests/test_pdf_parser.py`: Verify PDF text/table extraction with expected structures.
  - `tests/test_spreadsheet_reader.py`: Verify GDP sheet reading and CSV merging.
  - `tests/test_data_layer.py`: Verify data consolidation and caching.
- **Coverage**: Minimum of >80% code coverage.
