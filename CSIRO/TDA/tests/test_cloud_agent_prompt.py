import pytest
from pathlib import Path

def test_cloud_agent_modular_prompts_exist():
    base_path = Path("agents/cloud_agent")
    expected_files = [
        "cloud_root_agent.md",
        "billing_sub_agent.md",
        "contract_sub_agent.md",
        "finops_sub_agent.md",
        "data_science_sub_agent.md",
        "security_sub_agent.md"
    ]
    for filename in expected_files:
        path = base_path / filename
        assert path.exists(), f"Prompt file {filename} should exist"
    
    # Check schema mapping in synthetic_data
    schema_path = Path("synthetic_data/cloud_agent_schema.md")
    assert schema_path.exists(), "Schema mapping file should exist in synthetic_data"

def test_root_agent_instruction_content():
    path = Path("agents/cloud_agent/cloud_root_agent.md")
    content = path.read_text()
    assert "delegate" in content.lower()
    assert "Billing Sub-agent" in content
    assert "Contract Sub-agent" in content
    assert "FinOps Sub-agent" in content
    assert "Data Science Sub-agent" in content
