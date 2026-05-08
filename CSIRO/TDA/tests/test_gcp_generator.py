import pytest
from pathlib import Path
from scripts.gcp_generator import generate_gcp_service_agreement, generate_gcp_invoice, generate_gcp_finops_report

@pytest.mark.parametrize("gen_func, filename", [
    (generate_gcp_service_agreement, "gcp_sa.pdf"),
    (generate_gcp_invoice, "gcp_inv.pdf"),
    (generate_gcp_finops_report, "gcp_report.pdf"),
])
def test_gcp_generators_create_file(tmp_path, gen_func, filename):
    output_path = tmp_path / filename
    gen_func(output_path, "2026-05-05")
    assert output_path.exists()
    assert output_path.stat().st_size > 0
