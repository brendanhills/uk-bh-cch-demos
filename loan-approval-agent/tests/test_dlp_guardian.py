import pytest
import os
from unittest.mock import MagicMock, patch
from loan_agent.utils.dlp_guardian import DLPGuardian, guardian

# Mark as unit test dependency
pytestmark = [
    pytest.mark.dependency(name="unit_dlp"),
    pytest.mark.run(order=1)
]

class TestDLPGuardian:
    @pytest.fixture(autouse=True)
    def reset_guardian(self):
        from loan_agent.utils.dlp_guardian import guardian
        guardian.reset()
        yield
        guardian.reset()
    
    def test_regex_fallback_masking(self):
        """Verify that Regex fallback works when Cloud DLP is disabled/fails."""
        # Force a guardian instance with no project ID to trigger fallback
        with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": ""}, clear=True):
            local_guardian = DLPGuardian()
            # It might try to use google.auth.default(), so we should patch that too if needed
            # But simpler: ensure client is None
            local_guardian._use_cloud_dlp_checked = True 
            local_guardian._client = None
            
            text = "My SSN is 123-45-6789 and email is test@example.com"
            masked = local_guardian.inspect_and_mask(text)
            
            assert "[REDACTED_SSN]" in masked
            assert "[REDACTED_EMAIL]" in masked
            assert "123-45-6789" not in masked
            assert "test@example.com" not in masked

    def test_cloud_dlp_call(self):
        """Verify that Cloud DLP is called when client is available."""
        # Create a mock client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.item.value = "Masked by Cloud"
        mock_client.deidentify_content.return_value = mock_response

        # Init guardian (mode doesn't matter since we inject client)
        cloud_guardian = DLPGuardian()
        
        # Manually inject the mock client
        cloud_guardian._client = mock_client
        cloud_guardian._use_cloud_dlp_checked = True # Prevent auto-init
        cloud_guardian._parent = "projects/test-project/locations/global"

        # Execute
        result = cloud_guardian.inspect_and_mask("sensitive data")
        
        # Verify
        assert result == "Masked by Cloud"
        mock_client.deidentify_content.assert_called_once()

    def test_singleton_exists(self):
        assert guardian is not None
        assert isinstance(guardian, DLPGuardian)
