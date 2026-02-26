import pytest
from unittest.mock import patch, MagicMock
from loan_agent.utils.model_client import Client, get_best_model_name

# Mark as unit test dependency
pytestmark = [
    pytest.mark.depends(name="unit_tests"),
    pytest.mark.run(order=1)
]

class TestModelFeatures:
    
    @patch("loan_agent.utils.model_client.Client")
    def test_get_best_model_name_success(self, mock_client_cls):
        """Verify that it returns the preferred model if API call succeeds."""
        # Setup mock
        mock_instance = MagicMock()
        mock_client_cls.return_value = mock_instance
        
        # Reset global state for test
        with patch("loan_agent.utils.model_client._BEST_MODEL_NAME", None):
            model_name = get_best_model_name()
            assert model_name == "gemini-3-flash-preview"

    @patch("loan_agent.utils.model_client.Client")
    def test_get_best_model_name_fallback(self, mock_client_cls):
        """Verify that it returns the fallback model if API call fails."""
        # Setup mock to raise exception
        mock_instance = MagicMock()
        mock_instance.models.generate_content.side_effect = Exception("403 Forbidden")
        mock_client_cls.return_value = mock_instance
        
        # Reset global state for test
        with patch("loan_agent.utils.model_client._BEST_MODEL_NAME", None):
            model_name = get_best_model_name()
            assert model_name == "gemini-2.5-flash"
