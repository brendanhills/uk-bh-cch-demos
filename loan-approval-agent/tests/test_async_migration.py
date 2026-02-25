
import pytest
import asyncio
import time
import sys
import os
from unittest.mock import patch, MagicMock

# Force local import
sys.path.insert(0, os.getcwd())

import importlib
from loan_approval_agent.tools import simulation_utils
from loan_approval_agent.tools import credit_bureau
from loan_approval_agent.tools import employment_service
from loan_approval_agent.tools import fraud_service

# Reload to ensure we get the latest code even if imported earlier
importlib.reload(simulation_utils)
importlib.reload(credit_bureau)
importlib.reload(employment_service)
importlib.reload(fraud_service)

print(f"DEBUG: credit_bureau file: {credit_bureau.__file__}")

@pytest.mark.asyncio
async def test_simulate_delay_async():
    """Verify simulate_delay_async is non-blocking and awaits."""
    start_time = time.time()
    # We mock get_latency to return a small non-zero value to prove it waits
    with patch("loan_approval_agent.tools.simulation_utils.get_latency", return_value=0.1):
        await simulation_utils.simulate_delay_async(0.1)
    duration = time.time() - start_time
    # It should take at least 0.1s
    assert duration >= 0.1

@pytest.mark.asyncio
async def test_get_credit_report_async_structure():
    """
    Verify that we can call get_credit_report asynchronously 
    ONCE we convert it. 
    This test serves as a target for our refactoring.
    """
    # Check if it is a coroutine function
    is_async = asyncio.iscoroutinefunction(credit_bureau.get_credit_report)
    
    if not is_async:
        pytest.fail(f"credit_bureau.get_credit_report is NOT async. Module file: {credit_bureau.__file__}")
        
    # If it is async, let's try calling it
    token_id = "TOKEN-123"
    with patch("loan_approval_agent.tools.token_vault.detokenize", return_value="900-00-1234"), \
         patch("loan_approval_agent.tools.credit_bureau.simulate_delay_async", new_callable=MagicMock) as mock_delay:
         
        # Make the mock awaitable by setting side_effect or return_value to be a coroutine?
        # Or just use an async function as side_effect
        async def async_mock(*args, **kwargs):
             pass
        mock_delay.side_effect = async_mock
         
        report = await credit_bureau.get_credit_report(token_id)
        assert "score" in report
        mock_delay.assert_called_once()

@pytest.mark.asyncio
async def test_verify_employment_async():
    if not asyncio.iscoroutinefunction(employment_service.verify_employment):
        pytest.skip("verify_employment not yet async")
        
    with patch("loan_approval_agent.tools.token_vault.detokenize", return_value="900-00-1234"), \
         patch("loan_approval_agent.tools.employment_service.simulate_delay_async", new_callable=MagicMock) as mock_delay:
         
        async def async_mock(*args, **kwargs):
             pass
        mock_delay.side_effect = async_mock

        result = await employment_service.verify_employment("TOKEN-123")
        if "error" in result:
             pytest.fail(f"verify_employment returned error: {result['error']}. DB Path: {employment_service.DATA_FILE}")
             
        assert "verified_annual_income" in result
        mock_delay.assert_called_once()

@pytest.mark.asyncio
async def test_check_fraud_risk_async():
    if not asyncio.iscoroutinefunction(fraud_service.check_fraud_risk):
        pytest.skip("check_fraud_risk not yet async")

    with patch("loan_approval_agent.tools.token_vault.detokenize", return_value="900-00-9999"), \
         patch("loan_approval_agent.tools.fraud_service.simulate_delay_async", new_callable=MagicMock) as mock_delay:
         
        async def async_mock(*args, **kwargs):
             pass
        mock_delay.side_effect = async_mock
         
        result = await fraud_service.check_fraud_risk("TOKEN-123")
        assert result["risk_level"] == "HIGH" 
        mock_delay.assert_called_once()
