import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.getcwd())

from loan_approval_agent import config
# Set latency to testing mode for speed
config.LATENCY_MODE = "TESTING"

from loan_approval_agent.sub_agents.investigator import tools as inv_tools
from loan_approval_agent.sub_agents.policy_expert import tools as pol_tools
from loan_approval_agent.sub_agents.underwriter import tools as und_tools

def test_investigator_credit_report():
    # Test with a known ID from mock DB (assuming mock DB mock is loaded or we mock get)
    # Actually, let's check one of the generated IDs if possible, or just check the structure
    # of the fallback/error if not found, OR rely on the fact that tools.py loads the JSON on import.
    
    # We can list keys from the loaded DB if we want to be sure
    valid_ids = list(inv_tools.APPLICANTS_DB.keys())
    if valid_ids:
        report = inv_tools.get_credit_report(valid_ids[0])
        assert "credit_score" in report or "error" in report
        assert report["applicant_id"] == valid_ids[0]

def test_investigator_employment():
    valid_ids = list(inv_tools.APPLICANTS_DB.keys())
    if valid_ids:
        emp = inv_tools.verify_employment(valid_ids[0])
        assert "verified_annual_income" in emp
        assert "status" in emp

def test_investigator_fraud():
    valid_ids = list(inv_tools.APPLICANTS_DB.keys())
    if valid_ids:
        fraud = inv_tools.check_fraud_risk(valid_ids[0])
        assert "fraud_score" in fraud

def test_policy_expert_pdf_reading():
    # Check if the Master Policy exists and is readable
    policy_path = "loan_approval_agent/data/policy_docs/Master_Lending_Policy_v2024.pdf"
    assert os.path.exists(policy_path), "Master Policy PDF not found"
    
    # Test the tool
    # Note: consult_policy_docs calls the LLM, which we might want to mock for a unit test
    # BUT, we can test the helper function `_read_policy_docs` if it exists, or just mock the dependencies.
    # For now, let's just verify the file exists and is a valid PDF using pypdf directly
    import pypdf
    try:
        reader = pypdf.PdfReader(policy_path)
        assert len(reader.pages) > 0
        text = reader.pages[0].extract_text()
        assert len(text) > 0
    except Exception as e:
        pytest.fail(f"Failed to read Master Policy PDF: {e}")

def test_underwriter_decision_record():
    result = und_tools.record_decision(
        applicant_id="TEST_123",
        decision="APPROVE",
        reason="Unit Test Approval",
        interest_rate=5.5
    )
    assert result["status"] == "success"
    assert "pdf_path" in result
    assert result["record"]["applicant_id"] == "TEST_123"
    assert os.path.exists(result["pdf_path"])
    
    # Cleanup
    if os.path.exists(result["pdf_path"]):
        os.remove(result["pdf_path"])
