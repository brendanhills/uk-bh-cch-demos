"""Integration Test for 'Sarah Speed' (Auto-Approve) scenario."""
import pytest
import asyncio
from unittest.mock import patch
from google.genai.types import Part, UserContent
from google.adk.runners import InMemoryRunner

@pytest.mark.asyncio
async def test_sarah_speed_auto_approve():
    """Verify that Sarah Speed is automatically approved by the agent team."""
    
    # 1. Setup Runner
    # We move imports here to ensure patches apply if logic runs on import
    from loan_agent.agent import loan_manager
    from loan_agent import config

    # Ensure we use testing mode for speed
    config.LATENCY_MODE = "TESTING"

    # Initialize Runner
    runner = InMemoryRunner(agent=loan_manager)
    session = await runner.session_service.create_session(user_id="test_user", app_name="loan_agent")
    
    # 2. Start Conversation
    # Conversation Input
    app_input = (
        "Please process a loan application for Sarah Speed (ID: 900-00-1234). "
        "She wants $20,000 for Debt Consolidation. She earns $59,758 at City Hospital. "
        "Her monthly current debt payment is $500."
    )
    
    user_content = UserContent(parts=[Part(text=app_input)])
    
    full_text = ""
    # Capture events to verify tool calls
    tool_calls = []
    
    async for event in runner.run_async(
        user_id="test_user",
        session_id=session.id,
        new_message=user_content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    full_text += part.text + "\n"
        
        # Track tool calls if visible in events (Depends on ADK version/event schema)
        if hasattr(event, "tool_calls") and event.tool_calls:
            tool_calls.extend([tc.name for tc in event.tool_calls])

    print(f"\n[Sarah Speed Test] Final Output:\n{full_text}")

    # 3. Decision Assertion
    assert "APPROVE" in full_text.upper() or "APPROVED" in full_text.upper() or "SUCCESS" in full_text.upper()
