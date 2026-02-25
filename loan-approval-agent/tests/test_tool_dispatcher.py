import pytest
from unittest.mock import patch, MagicMock
from loan_agent.utils.tool_dispatcher import call_tool, list_tools, TOOL_REGISTRY

# Mark as unit test dependency
pytestmark = [
    pytest.mark.dependency(name="unit_dispatcher"),
    pytest.mark.run(order=1)
]

class TestToolDispatcher:
    
    @pytest.mark.asyncio
    async def test_call_tool_success(self):
        """Verify successful tool dispatch."""
        # Mock the importlib to return a mock module
        mock_module = MagicMock()
        
        # If the dispatcher checks for coroutine, we need to mock it as such
        async def mock_coro(*args, **kwargs):
            return {"score": 750}
        
        mock_module.get_credit_report = mock_coro
        
        with patch("loan_agent.utils.tool_dispatcher.importlib.import_module", return_value=mock_module):
            # We use an existing key from registry, e.g., get_credit_report
            result = await call_tool("get_credit_report", {"gov_id": "123"})
            
            assert result == {"score": 750}

    @pytest.mark.asyncio
    async def test_call_nonexistent_tool(self):
        """Verify handling of unknown tools."""
        result = await call_tool("non_existent_tool", {})
        assert "error" in result
        assert "not found" in result["error"]

    def test_registry_structure(self):
        """Verify registry maps to valid module paths."""
        assert "get_credit_report" in TOOL_REGISTRY
        module, func = TOOL_REGISTRY["get_credit_report"]
        assert isinstance(module, str)
        assert isinstance(func, str)
