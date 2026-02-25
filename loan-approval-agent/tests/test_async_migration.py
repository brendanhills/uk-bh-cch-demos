import pytest
import asyncio
import time
import sys
import os
from unittest.mock import patch, MagicMock

# Force local import
sys.path.insert(0, os.getcwd())

import importlib
from external_services import simulation_utils
from loan_agent.tools import credit_bureau
from loan_agent.tools import employment_service
from loan_agent.tools import fraud_service

# Reload to ensure we get the latest code even if imported earlier
importlib.reload(simulation_utils)
importlib.reload(credit_bureau)
importlib.reload(employment_service)
importlib.reload(fraud_service)

@pytest.mark.asyncio
async def test_simulate_delay_async():
    """Verify simulate_delay_async is non-blocking and awaits."""
    start_time = time.time()
    # We mock get_latency to return a small non-zero value to prove it waits
    with patch("external_services.simulation_utils.get_latency", return_value=0.1):
        await simulation_utils.simulate_delay_async(0.1)
    duration = time.time() - start_time
    # It should take at least 0.1s
    assert duration >= 0.1

@pytest.mark.asyncio
async def test_get_credit_report_async_structure():
    """Verify that we can call get_credit_report asynchronously."""
    # Check if it is a coroutine function
    is_async = asyncio.iscoroutinefunction(credit_bureau.get_credit_report)
    assert is_async
        
    token_id = "TOKEN-123"
    # Note: call_tool is what actually does the work now
    with patch("loan_agent.utils.token_vault.detokenize", return_value="900-00-1234"), \
         patch("loan_agent.utils.tool_dispatcher.call_tool") as mock_call:
         
        async def async_mock(*args, **kwargs):
             return {"score": 750}
        mock_call.side_effect = async_mock
         
        report = await credit_bureau.get_credit_report(token_id)
        assert report["score"] == 750
        mock_call.assert_called_once()

@pytest.mark.asyncio
async def test_verify_employment_async():
    is_async = asyncio.iscoroutinefunction(employment_service.verify_employment)
    assert is_async
        
    with patch("loan_agent.utils.token_vault.detokenize", return_value="900-00-1234"), \
         patch("loan_agent.utils.tool_dispatcher.call_tool") as mock_call:
         
        async def async_mock(*args, **kwargs):
             return {"employer": "City Hospital", "verified_annual_income": 59758}
        mock_call.side_effect = async_mock

        result = await employment_service.verify_employment("TOKEN-123")
        assert result["employer"] == "City Hospital"
        mock_call.assert_called_once()

@pytest.mark.asyncio
async def test_check_fraud_risk_async():
    is_async = asyncio.iscoroutinefunction(fraud_service.check_fraud_risk)
    assert is_async

    with patch("loan_agent.utils.token_vault.detokenize", return_value="900-00-9999"), \
         patch("loan_agent.utils.tool_dispatcher.call_tool") as mock_call:
         
        async def async_mock(*args, **kwargs):
             return {"risk_level": "HIGH"}
        mock_call.side_effect = async_mock
         
        result = await fraud_service.check_fraud_risk("TOKEN-123")
        assert result["risk_level"] == "HIGH" 
        mock_call.assert_called_once()
