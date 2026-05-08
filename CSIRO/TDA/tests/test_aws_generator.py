import pytest
from pathlib import Path
from scripts.aws_generator import generate_aws_service_agreement, generate_aws_invoice, generate_aws_finops_report

@pytest.mark.parametrize("gen_func, filename", [
    (generate_aws_service_agreement, "aws_sa.pdf"),
    (generate_aws_invoice, "aws_inv.pdf"),
    (generate_aws_finops_report, "aws_report.pdf"),
])
def test_aws_generators_create_file(tmp_path, gen_func, filename):
    output_path = tmp_path / filename
    gen_func(output_path, "2026-05-05")
    assert output_path.exists()
    assert output_path.stat().st_size > 0
