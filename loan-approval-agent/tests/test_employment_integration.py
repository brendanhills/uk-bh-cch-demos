import pytest
import os
import json
from loan_agent.tools.employment_service import verify_employment
from external_services.employment_registry import DATA_FILE

# Mark as unit test dependency
pytestmark = [
    pytest.mark.dependency(name="unit_employment"),
    pytest.mark.run(order=1)
]

@pytest.mark.asyncio
async def test_verify_employment_sarah():
    result = await verify_employment("900-00-1234")
    print(f"\nResult: {result}")
    assert "error" not in result
    assert result["employer"] == "City Hospital"
    assert result["verified_annual_income"] == 59758
