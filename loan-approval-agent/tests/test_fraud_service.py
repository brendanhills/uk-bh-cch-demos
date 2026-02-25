import pytest
import asyncio
from unittest.mock import patch, MagicMock
from external_services.fraud_service import check_fraud_risk

# Mark as unit test dependency
pytestmark = [
    pytest.mark.depends(name="unit_fraud"),
    pytest.mark.run(order=1)
]

class TestFraudService:
    
    @pytest.mark.asyncio
    async def test_high_risk_profile(self):
        """Verify that known fraudster ID returns HIGH risk."""
        # Mock simulation_utils to avoid sleep delay
        with patch("external_services.fraud_service.simulate_delay_async", new_callable=MagicMock) as mock_delay:
            # Make mock awaitable
            async def async_mock(*args, **kwargs): pass
            mock_delay.side_effect = async_mock
            
            result = await check_fraud_risk("900-00-9999") 
            assert result["risk_level"] == "HIGH"
            assert "IDENTITY_VELOCITY_CHECK" in result["flags"]

    @pytest.mark.asyncio
    async def test_low_risk_profile(self):
        """Verify that a safe ID returns LOW/MEDIUM risk."""
        with patch("external_services.fraud_service.simulate_delay_async", new_callable=MagicMock) as mock_delay:
            async def async_mock(*args, **kwargs): pass
            mock_delay.side_effect = async_mock
            
            result = await check_fraud_risk("900-00-1234") # Sarah Speed
            # In my JSON update, Sarah Speed (900-00-1234) is LOW
            assert result["risk_level"] in ["LOW", "MEDIUM"]
