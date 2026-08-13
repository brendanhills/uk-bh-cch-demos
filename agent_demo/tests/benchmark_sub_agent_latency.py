"""Benchmark script to measure sub-agent delegation latency overhead in ADK 2.0 system."""

import asyncio
import os
import time
from typing import Dict, Any

from google.adk.agents import Agent
from google.adk.tools import AgentTool
from google.adk.tools.tool_context import ToolContext
from cch_agent.tools.telemetry import TimedAgentTool
from cch_agent.sub_agents import (
    patient_verifier,
    document_scanner,
    visit_scheduler,
    soap_generator,
)


async def benchmark_sub_agent(sub_agent: Agent, sample_args: Dict[str, Any]) -> float:
    """Measures single execution latency of a TimedAgentTool delegation."""
    timed_tool = TimedAgentTool(sub_agent)
    
    class MockState(dict):
        def to_dict(self):
            return dict(self)

    mock_context = MagicMock()
    mock_context.state = MockState()
    mock_context._invocation_context = MagicMock()
    mock_context._invocation_context.app_name = "cch-demo"
    mock_context._invocation_context.user_id = "benchmark_user"
    mock_context._invocation_context.credential_service = None
    mock_context._invocation_context.plugin_manager = MagicMock()
    mock_context._invocation_context.plugin_manager.plugins = []

    start = time.perf_counter()
    try:
        result = await timed_tool.run_async(args=sample_args, tool_context=mock_context)
        duration = time.perf_counter() - start
        print(f"  • {sub_agent.name}: {duration*1000:.2f}ms ({(duration):.3f}s) | Result preview: {str(result)[:60]}")
        return duration
    except Exception as e:
        duration = time.perf_counter() - start
        print(f"  • {sub_agent.name}: {duration*1000:.2f}ms ({(duration):.3f}s) | Error: {e}")
        return duration


if __name__ == "__main__":
    from unittest.mock import MagicMock
    print("=" * 65)
    print("  ADK 2.0 Sub-Agent Delegation Latency Benchmark")
    print("=" * 65)
    
    sub_agents_to_test = [
        (patient_verifier, {"request": "Caller name Brendan, phone 0412 345 678, child Leo"}),
        (document_scanner, {"request": "Scan discharge summary for Leo"}),
        (visit_scheduler, {"request": "Schedule nurse visit for Leo on Monday 10am"}),
        (soap_generator, {"request": "Generate clinical SOAP note for Leo"}),
    ]

    for agent_obj, args in sub_agents_to_test:
        asyncio.run(benchmark_sub_agent(agent_obj, args))
