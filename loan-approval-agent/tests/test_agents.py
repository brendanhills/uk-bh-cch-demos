import pytest
import os
import sys
from unittest.mock import MagicMock, patch

# Mark as unit test dependency
pytestmark = [
    pytest.mark.depends(name="unit_agents"),
    pytest.mark.run(order=1)
]

# Add project root to path
sys.path.append(os.getcwd())

from loan_agent import config
# Set latency to testing mode for speed
config.LATENCY_MODE = "TESTING"

from loan_agent.sub_agents.investigator import tools as inv_tools
from loan_agent.sub_agents.policy_expert import tools as pol_tools
from loan_agent.sub_agents.underwriter import tools as und_tools

from loan_agent.utils import token_vault

@pytest.mark.asyncio
async def test_investigator_credit_report():
    # Test with a known valid ID (Sarah Speed)
    raw_id = "900-00-1234"
    # Tokenize first (simulating Intake)
    token_id = token_vault.tokenize(raw_id)
    
    report = await inv_tools.get_credit_report(token_id)
    
    # Check for expected keys or error structure
    if "error" in report:
        # If the file load fails in test env, this might happen, but we expect success
        pytest.fail(f"Credit report returned error: {report['error']}")
        
    # The report uses the ID it found in the DB (which matches raw_id in the mock data usually)
    # verify_employment returns "applicant_id": "900-00-1234"
    assert "score" in report

@pytest.mark.asyncio
async def test_investigator_employment():
    raw_id = "900-00-1234"
    token_id = token_vault.tokenize(raw_id)
    emp = await inv_tools.verify_employment(token_id)
    
    if "error" in emp:
         pytest.fail(f"Employment check returned error: {emp['error']}")
         
    assert "verified_annual_income" in emp
    assert "status" in emp

@pytest.mark.asyncio
async def test_investigator_fraud():
    raw_id = "900-00-1234"
    token_id = token_vault.tokenize(raw_id)
    fraud = await inv_tools.check_fraud_risk(token_id)
    
    if "error" in fraud:
        pytest.fail(f"Fraud check returned error: {fraud['error']}")
        
    assert "risk_level" in fraud

def test_policy_expert_pdf_reading():
    # Test the actual tool
    from loan_agent.sub_agents.policy_expert.tools import consult_policy_docs
    
    # Empty query should return top chunks
    result = consult_policy_docs("", applicant_id="TEST_UNIT")
    
    # Check for expected content or error
    if "Error:" in result:
        pytest.fail(f"consult_policy_docs returned error: {result}")
        
    assert "Policy Search Results" in result
    assert "Source:" in result

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
