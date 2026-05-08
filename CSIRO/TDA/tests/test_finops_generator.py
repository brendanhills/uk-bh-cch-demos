import pytest
import csv
from pathlib import Path
from scripts.finops_generator import generate_finops_csv

def test_generate_finops_csv_content(tmp_path):
    output_path = tmp_path / "finops_chargeback.csv"
    generate_finops_csv(output_path, 2026, 5)
    assert output_path.exists()
    
    with open(output_path, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
        assert len(rows) > 0
        header = reader.fieldnames
        expected_fields = ["Date", "Provider", "AccountID", "ServiceID", "ServiceName", "ResourceID", "Currency", "Cost"]
        for field in expected_fields:
            assert field in header
        
        # Check for presence of all 3 providers
        providers = set(row["Provider"] for row in rows)
        assert "AWS" in providers
        assert "Azure" in providers
        assert "GCP" in providers
        
        # Check currency is AUD
        currencies = set(row["Currency"] for row in rows)
        assert currencies == {"AUD"}
