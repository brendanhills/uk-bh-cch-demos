import os
import pytest
import pandas as pd
from src.pdf_parser import (
    extract_text_from_pdf,
    extract_tables_from_pdf,
    parse_budget_table
)

@pytest.fixture
def sample_pdf_path():
    # Use bp1_bs-1.pdf as a sample for our tests
    path = "data/bp1_bs-1.pdf"
    assert os.path.exists(path), f"Sample PDF not found at {path}"
    return path

def test_extract_text_from_pdf(sample_pdf_path):
    text = extract_text_from_pdf(sample_pdf_path)
    assert isinstance(text, str)
    assert len(text) > 0
    # Confirm it contains typical text
    assert "Budget Paper No. 1" in text or "Statement 1" in text

def test_extract_tables_from_pdf(sample_pdf_path):
    # page 7 (index 6) has Table 1 with 8 rows, 7 columns
    tables = extract_tables_from_pdf(sample_pdf_path, page_num=7)
    assert isinstance(tables, list)
    assert len(tables) > 0
    table = tables[0]
    assert len(table) == 8  # 8 rows
    assert len(table[0]) == 7  # 7 columns
    # First row headers or outcomes
    assert "Outcome" in [str(cell) for cell in table[0] if cell]

def test_parse_budget_table(sample_pdf_path):
    # parse Table 1 on page 7
    df = parse_budget_table(sample_pdf_path, page_num=7)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    # Columns should be standard: Item/Category and years
    assert "Category" in df.columns or "Item" in df.columns
    assert "2025-26" in df.columns
    assert "2026-27" in df.columns
    # Check some content
    categories = df.iloc[:, 0].tolist()
    assert any("Real GDP" in str(cat) for cat in categories)
