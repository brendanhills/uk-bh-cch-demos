import pytest
from unittest.mock import MagicMock, patch
from loan_agent.utils import dlp_guardian

# Mark as unit test dependency
pytestmark = [
    pytest.mark.depends(name="unit_tests"),
    pytest.mark.run(order=1)
]

class TestDLPGuardian:
    @pytest.fixture(autouse=True)
    def reset_dlp(self):
        dlp_guardian.reset_dlp()
        yield
        dlp_guardian.reset_dlp()
    
    def test_live_dlp_availability(self):
        """
        Verify that the live Cloud DLP service is available and functional.
        """
        # Using a standard format that DLP is likely to recognize
        text = "My name is Sarah Speed and my SSN is 411-55-6789."
        try:
            masked = dlp_guardian.inspect_and_mask(text)
            
            # Check that it masked SOMETHING (either name or SSN)
            assert "[" in masked and "]" in masked
            assert "Sarah Speed" not in masked or "411-55-6789" not in masked
            
            print(f"\n[DLP Live Test] Masked output: {masked}")
            
        except Exception as e:
            pytest.fail(f"Cloud DLP service is NOT available or failed: {e}")

    def test_cloud_dlp_mock_call(self):
        """Verify the internal logic of calling the client when available."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.item.value = "Masked by Cloud"
        mock_client.deidentify_content.return_value = mock_response

        # Use patch to inject our mock client
        with patch("loan_agent.utils.dlp_guardian._get_client", return_value=(mock_client, "projects/test/locations/global")):
            result = dlp_guardian.inspect_and_mask("sensitive data")
            assert result == "Masked by Cloud"
            mock_client.deidentify_content.assert_called_once()
