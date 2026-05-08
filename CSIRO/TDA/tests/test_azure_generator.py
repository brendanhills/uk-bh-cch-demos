import pytest
from pathlib import Path
from scripts.azure_generator import generate_azure_service_agreement, generate_azure_invoice, generate_azure_finops_report

@pytest.mark.parametrize("gen_func, filename", [
    (generate_azure_service_agreement, "azure_sa.pdf"),
    (generate_azure_invoice, "azure_inv.pdf"),
    (generate_azure_finops_report, "azure_report.pdf"),
])
def test_azure_generators_create_file(tmp_path, gen_func, filename):
    output_path = tmp_path / filename
    gen_func(output_path, "2026-05-05")
    assert output_path.exists()
    assert output_path.stat().st_size > 0
