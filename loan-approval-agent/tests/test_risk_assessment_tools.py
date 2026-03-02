import pytest
from loan_agent.tools.risk_assessment import get_ml_risk_score, lookup_historical_decisions

@pytest.mark.asyncio
async def test_get_ml_risk_score():
    """Verify ML risk score retrieval for a demo persona."""
    applicant_id = "user_01" # Sarah Speed
    result = await get_ml_risk_score(applicant_id)
    assert "risk_score" in result
    assert 0 <= result["risk_score"] <= 100
    assert "model_version" in result

@pytest.mark.asyncio
async def test_lookup_historical_decisions():
    """Verify historical decision lookup for a demo persona."""
    applicant_id = "user_01" # Sarah Speed
    result = await lookup_historical_decisions(applicant_id)
    assert "historical_decisions" in result
    assert isinstance(result["historical_decisions"], list)
    if len(result["historical_decisions"]) > 0:
        assert "outcome" in result["historical_decisions"][0]
        assert "date" in result["historical_decisions"][0]
