"""Unit tests for sub-agent delegation telemetry and latency measurement."""

import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

from google.adk.agents import Agent
from google.adk.tools import AgentTool
from cch_agent.tools.telemetry import TimedAgentTool
from cch_agent.agent import agent as router_agent


def test_timed_agent_tool_initialization():
    """Verify TimedAgentTool inherits name and description from wrapped Agent."""
    dummy_agent = Agent(name="dummy_sub_agent", model="gemini-2.5-flash", instruction="Test sub agent")
    timed_tool = TimedAgentTool(dummy_agent)
    assert timed_tool.name == "dummy_sub_agent"
    assert isinstance(timed_tool, AgentTool)


@pytest.mark.asyncio
async def test_timed_agent_tool_execution_logs_and_records_latency():
    """Verify TimedAgentTool measures duration_ms and logs start/end dispatch timestamps."""
    dummy_agent = Agent(name="dummy_sub_agent", model="gemini-2.5-flash", instruction="Test sub agent")
    timed_tool = TimedAgentTool(dummy_agent)

    # Mock tool context and super().run_async
    mock_context = MagicMock()
    mock_context.state = {}

    async def mock_run_async(*args, **kwargs):
        await asyncio.sleep(0.05) # simulate 50ms sub-agent execution
        return "Sub-agent result"

    import asyncio
    with patch.object(AgentTool, "run_async", side_effect=mock_run_async):
        start_time = time.perf_counter()
        result = await timed_tool.run_async(args={"request": "test"}, tool_context=mock_context)
        total_time = time.perf_counter() - start_time

        assert result == "Sub-agent result"
        assert total_time >= 0.04

        # Check telemetry recorded in session state
        telemetry = mock_context.state.get("temp:_sub_agent_telemetry")
        assert telemetry is not None
        assert len(telemetry) == 1
        assert telemetry[0]["sub_agent"] == "dummy_sub_agent"
        assert telemetry[0]["duration_ms"] >= 40.0


def test_router_agent_uses_timed_agent_tools():
    """Verify router agent sub-agent tools are configured with TimedAgentTool wrappers."""
    sub_agent_tools = [t for t in router_agent.tools if isinstance(t, AgentTool)]
    assert len(sub_agent_tools) == 4
    for tool in sub_agent_tools:
        assert isinstance(tool, TimedAgentTool), f"Tool {tool.name} is not wrapped in TimedAgentTool"
        assert tool.skip_summarization is True
