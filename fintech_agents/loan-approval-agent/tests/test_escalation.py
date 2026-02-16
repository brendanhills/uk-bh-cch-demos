
import pytest
import os
import sys
import asyncio
from google.genai.types import Part, UserContent
from google.adk.runners import InMemoryRunner

# Add project root to path
sys.path.append(os.getcwd())

from loan_approval_agent import config
# Set latency to testing mode
config.LATENCY_MODE = "TESTING"

from loan_approval_agent.agent import loan_manager

@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires mocking of ADK runtime model")
async def test_escalation_borderline_credit():
    """Test that the agent escalates a borderline credit application."""
    
    # Applicant 12348 has Credit Score 620, which is in the Borderline range (600-640)
    user_input = (
        "Begin review for applicant_id: 12348. "
        "Requested Loan Amount: $50,000. "
        "Loan Purpose: Business."
    )
    
    runner = InMemoryRunner(agent=loan_manager)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )
    content = UserContent(parts=[Part(text=user_input)])
    
    final_response = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text
    
    # Assertions
    print(f"DEBUG: Final Response: {final_response}")
    
    # Logic: The Underwriter should set decision to ESCALATE
    assert "ESCALATE" in final_response.upper() or "ESCALATION" in final_response.upper()
    
    # Check Audit Log for escalation event
    log_file = "loan_approval_agent/data/audit_logs/audit_12348.json"
    assert os.path.exists(log_file)
    
    import json
    with open(log_file, "r") as f:
        log_data = json.load(f)
        
    escalation_events = [e for e in log_data["events"] if e["action"] == "escalation_complete"]
    assert len(escalation_events) > 0, "No escalation event found in audit log"
    assert escalation_events[0]["details"]["record"]["decision"] == "ESCALATE"
