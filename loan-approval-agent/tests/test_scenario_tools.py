import pytest
import asyncio
from loan_agent.sub_agents.investigator import tools

# Mark as unit test dependency
pytestmark = [
    pytest.mark.depends(name="unit_tests"),
    pytest.mark.run(order=1)
]

@pytest.mark.asyncio
async def test_sarah_speed_tools():
    """Verify tool outputs for Sarah Speed (900-00-1234)."""
    applicant_id = "user_01" # Sarah's token
    
    # Test Credit Report
    credit = await tools.get_credit_report(applicant_id)
    assert credit["score"]["value"] == 725
    assert credit["summary"]["totalMonthlyPayment"] == 500
    
    # Test Employment
    employment = await tools.verify_employment(applicant_id)
    assert employment["employer"] == "City Hospital"
    assert employment["verified_annual_income"] == 59758
    
    # Test Fraud
    fraud = await tools.check_fraud_risk(applicant_id)
    assert fraud["risk_level"] == "LOW"
    
    # Test DTI Calculation
    dti = await tools.calculate_dti(applicant_id, loan_amount=20000)
    assert dti["dti_percentage"] > 18
    assert dti["dti_percentage"] < 19

@pytest.mark.asyncio
async def test_jane_fraud_tools():
    """Verify tool outputs for Jane Fraud (900-00-9999)."""
    applicant_id = "user_05" # Jane's token
    
    # Test Fraud
    fraud = await tools.check_fraud_risk(applicant_id)
    assert fraud["risk_level"] == "HIGH"
    assert fraud["risk_score"] == 95
    
    # Test Employment (Expected to be Not Found error)
    employment = await tools.verify_employment(applicant_id)
    assert "error" in employment
    assert "Not Found" in employment["error"]

@pytest.mark.asyncio
async def test_gary_escalate_tools():
    """Verify tool outputs for Gary Escalate (900-00-3456)."""
    applicant_id = "user_04" # Gary's token
    
    # Test Credit
    credit = await tools.get_credit_report(applicant_id)
    assert credit["score"]["value"] == 640
    
    # Test Fraud
    fraud = await tools.check_fraud_risk(applicant_id)
    assert fraud["risk_level"] == "MEDIUM"
