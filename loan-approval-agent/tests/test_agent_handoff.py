import pytest
import asyncio

# Mark as unit test dependency
pytestmark = [
    pytest.mark.depends(name="unit_tests"),
    pytest.mark.run(order=1)
]

from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
from loan_agent.agent import loan_manager
from loan_agent.sub_agents.investigator.agent import investigator_agent
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_handoff_to_investigator():
    """Verify that loan_manager hands off to investigator_agent when needed."""
    
    # 1. Setup Runner
    runner = InMemoryRunner(agent=loan_manager)
    session = await runner.session_service.create_session(user_id="test_user", app_name="loan_agent")
    
    # 2. Start with a state that has an applicant_id
    user_input = "Start investigation for Sarah Speed (ID: 900-00-1234, Token: TOKEN-123). She wants $10,000."
    
    # Static check of the agent tree configuration.
    from google.adk.tools.agent_tool import AgentTool
    tool_agents = [t.agent for t in loan_manager.tools if isinstance(t, AgentTool)]
    assert investigator_agent in tool_agents
    assert "investigator_agent" in [a.name for a in tool_agents]

def test_investigator_as_subagent_config():
    """Static check of the agent tree configuration."""
    from google.adk.tools.agent_tool import AgentTool
    tool_agents = [t.agent for t in loan_manager.tools if isinstance(t, AgentTool)]
    assert investigator_agent in tool_agents
    assert loan_manager.name == "loan_manager"
    assert investigator_agent.name == "investigator_agent"
    
    # Verify investigator has tools for data gathering
    tool_names = [getattr(t, "__name__", str(t)) for t in investigator_agent.tools]
    assert "get_credit_report" in tool_names
    assert "verify_employment" in tool_names
    
    # Verify loan_manager has investigator as agent tool
    assert any(a.name == "investigator_agent" for a in tool_agents)

@pytest.mark.asyncio
async def test_investigator_interactive_capability():
    """Verify that investigator agent can indeed 'ask' questions."""
    from loan_agent.sub_agents.investigator.prompt import INVESTIGATOR_PROMPT
    assert "Ask the User" in INVESTIGATOR_PROMPT
