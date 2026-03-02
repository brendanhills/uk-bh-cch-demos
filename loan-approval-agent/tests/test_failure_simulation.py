import pytest
from external_services.credit_bureau import get_credit_report as service_get_credit
from loan_agent.tools.credit_bureau import get_credit_report as tool_get_credit

@pytest.mark.asyncio
async def test_service_level_failure():
    """Verify the underlying service respects the simulate_failure flag."""
    gov_id = "900-00-1234"
    result = await service_get_credit(gov_id, simulate_failure=True)
    assert "error" in result
    assert "unavailable" in result["error"].lower()

@pytest.mark.asyncio
async def test_agent_tool_level_failure():
    """Verify the agent-facing tool correctly propagates simulated failure."""
    applicant_id = "user_01" # Sarah Speed
    result = await tool_get_credit(applicant_id, simulate_failure=True)
    assert "error" in result
    assert "simulated" in result["error"].lower()
