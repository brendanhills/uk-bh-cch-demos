import os
import pytest
import pandas as pd
from src.data_loader import (
    load_nominal_gdp,
    load_receipts_csv,
    load_receipts_percentages_csv,
    get_category_time_series
)

@pytest.fixture
def gdp_excel_path():
    path = "data/bp1_s2-data-nominal-GDP.xlsx"
    assert os.path.exists(path)
    return path

@pytest.fixture
def receipts_csv_path():
    path = "data/bp1_s5-online_t1.csv"
    assert os.path.exists(path)
    return path

@pytest.fixture
def percentages_csv_path():
    path = "data/bp1_s5-online_t2.csv"
    assert os.path.exists(path)
    return path

def test_load_nominal_gdp(gdp_excel_path):
    df = load_nominal_gdp(gdp_excel_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Year" in df.columns
    assert "2026-27 Budget" in df.columns
    assert "2025-26 MYEFO" in df.columns
    assert df["2026-27 Budget"].dtype in ["float64", "int64"]

def test_load_nominal_gdp_not_found():
    with pytest.raises(FileNotFoundError):
        load_nominal_gdp("non_existent_gdp.xlsx")

def test_load_receipts_csv(receipts_csv_path):
    df = load_receipts_csv(receipts_csv_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Category" in df.columns
    assert len(df.columns) > 5

def test_load_receipts_csv_not_found():
    with pytest.raises(FileNotFoundError):
        load_receipts_csv("non_existent_receipts.csv")

def test_load_receipts_percentages_csv(percentages_csv_path):
    df = load_receipts_percentages_csv(percentages_csv_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Year" in df.columns
    assert "Total receipts (%)" in df.columns

def test_load_receipts_percentages_csv_not_found():
    with pytest.raises(FileNotFoundError):
        load_receipts_percentages_csv("non_existent_pct.csv")

def test_get_category_time_series(receipts_csv_path):
    df = load_receipts_csv(receipts_csv_path)
    
    # Test with valid category
    series_df = get_category_time_series(df, "Company tax")
    assert isinstance(series_df, pd.DataFrame)
    assert not series_df.empty
    assert "Year" in series_df.columns
    assert "Value ($m)" in series_df.columns
    # Years should be like '2005-06', '2025-26'
    assert "2026-27" in series_df["Year"].tolist()
    
    # Test with invalid category
    invalid_df = get_category_time_series(df, "Non Existent Category")
    assert isinstance(invalid_df, pd.DataFrame)
    assert invalid_df.empty
