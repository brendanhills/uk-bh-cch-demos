import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from external_services.credit_bureau import get_credit_report as service_get_credit
from loan_agent.tools.credit_bureau import get_credit_report as tool_get_credit
from external_services.simulation_utils import set_service_failure

@pytest.mark.asyncio
async def test_service_level_failure():
    """Verify the underlying service respects the external failure flag."""
    gov_id = "900-00-1234"
    set_service_failure("credit_bureau", True)
    try:
        result = await service_get_credit(gov_id)
        assert "error" in result
        assert "External Downtime" in result["error"]
    finally:
        set_service_failure("credit_bureau", False)

@pytest.mark.asyncio
async def test_agent_tool_level_failure_propagation():
    """Verify the agent-facing tool correctly propagates simulated failure."""
    applicant_id = "user_01" # Sarah Speed
    set_service_failure("credit_bureau", True)
    try:
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await tool_get_credit(applicant_id)
            assert "error" in result
            assert "External Downtime" in result["error"]
    finally:
        set_service_failure("credit_bureau", False)

@pytest.mark.asyncio
async def test_outage_retry_exhaustion():
    """
    Test that the tool retries the specified number of times and eventually fails
    when the API outage persists.
    """
    # Mock call_tool to always return a 503 error
    mock_response = {"error": "Credit Bureau API is currently unavailable (External Downtime)."}
    
    with patch("loan_agent.tools.credit_bureau.call_tool", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_response
        
        # Mock asyncio.sleep to avoid waiting 31 seconds
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            result = await tool_get_credit("900-00-1234")
            
            # Verify call_tool was called 5 times (max_retries in the tool)
            assert mock_call.call_count == 5
            
            # Verify asyncio.sleep was called 5 times (the tool sleeps after EVERY failing attempt)
            assert mock_sleep.call_count == 5
            
            # Verify the final result is the last service error
            assert "error" in result
            assert "External Downtime" in result["error"]

@pytest.mark.asyncio
async def test_transient_outage_recovery():
    """
    Test that the tool recovers if the API outage is transient (fails once, then succeeds).
    """
    success_response = {"score": 750, "summary": "Strong credit profile"}
    error_response = {"error": "Credit Bureau API is currently unavailable (External Downtime)."}
    
    with patch("loan_agent.tools.credit_bureau.call_tool", new_callable=AsyncMock) as mock_call:
        # First call fails, second call succeeds
        mock_call.side_effect = [error_response, success_response]
        
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            result = await tool_get_credit("900-00-1234")
            
            # Verify call_tool was called 2 times
            assert mock_call.call_count == 2
            
            # Verify the result is successful
            assert result["score"] == 750
            assert "error" not in result

@pytest.mark.asyncio
async def test_no_retry_on_not_found():
    """
    Test that the tool does NOT retry for errors like "Applicant not found".
    """
    not_found_response = {"error": "Applicant not found in Credit Bureau"}
    
    with patch("loan_agent.tools.credit_bureau.call_tool", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = not_found_response
        
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            result = await tool_get_credit("900-00-1234")
            
            # Verify call_tool was called only 1 time
            assert mock_call.call_count == 1
            
            # Verify asyncio.sleep was never called
            assert mock_sleep.call_count == 0
            
            # Verify the result is the not_found error
            assert result == not_found_response
