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
    # Test with a known valid ID (Sarah Jenkins)
    valid_id = "900-00-1234"
    report = inv_tools.get_credit_report(valid_id)
    
    # Check for expected keys or error structure
    if "error" in report:
        # If the file load fails in test env, this might happen, but we expect success
        pytest.fail(f"Credit report returned error: {report['error']}")
        
    assert report["applicant_id"] == valid_id
    assert "score" in report

def test_investigator_employment():
    valid_id = "900-00-1234"
    emp = inv_tools.verify_employment(valid_id)
    
    if "error" in emp:
         pytest.fail(f"Employment check returned error: {emp['error']}")
         
    assert "verified_annual_income" in emp
    assert "status" in emp

def test_investigator_fraud():
    valid_id = "900-00-1234"
    fraud = inv_tools.check_fraud_risk(valid_id)
    
    if "error" in fraud:
        pytest.fail(f"Fraud check returned error: {fraud['error']}")
        
    assert "risk_level" in fraud

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
