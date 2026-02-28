import pytest
import asyncio
from google.adk.runners import InMemoryRunner
from google.adk.apps import App
from google.genai.types import UserContent, Part
from loan_agent.sub_agents.investigator.agent import investigator_agent
from loan_agent.sub_agents.policy_expert.agent import policy_expert_agent
from loan_agent.sub_agents.underwriter.agent import underwriter_agent

# Mark as unit test dependency
pytestmark = [
    pytest.mark.depends(name="unit_tests"),
    pytest.mark.run(order=1)
]

@pytest.mark.asyncio
async def test_investigator_agent_sarah():
    """Verify investigator_agent correctly gathers data for Sarah Speed."""
    test_app = App(name="loan_agent", root_agent=investigator_agent)
    runner = InMemoryRunner(app=test_app)
    session = await runner.session_service.create_session(user_id="test_sarah", app_name="loan_agent")
    
    # Sarah Speed's token is user_01
    user_input = "Gather all data for applicant user_01. Loan amount is $20,000."
    
    final_response = ""
    async for event in runner.run_async(
        session_id=session.id,
        user_id="test_sarah",
        new_message=UserContent(parts=[Part.from_text(text=user_input)])
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text

    assert "725" in final_response or "credit" in final_response.lower()
    assert "City Hospital" in final_response or "employer" in final_response.lower()
    assert "low" in final_response.upper() or "fraud" in final_response.lower()

@pytest.mark.asyncio
async def test_policy_expert_agent_sarah():
    """Verify policy_expert_agent reasoning given a mock report."""
    test_app = App(name="loan_agent", root_agent=policy_expert_agent)
    runner = InMemoryRunner(app=test_app)
    session = await runner.session_service.create_session(user_id="test_policy", app_name="loan_agent")
    
    mock_report = {
        "credit_score": 725,
        "employer": "City Hospital",
        "income": 59758,
        "dti": 18.57,
        "fraud_risk": "LOW"
    }
    
    user_input = f"Evaluate this investigation report against lending policy: {mock_report}. Applicant is user_01, loan is $20,000."
    
    final_response = ""
    async for event in runner.run_async(
        session_id=session.id,
        user_id="test_policy",
        new_message=UserContent(parts=[Part.from_text(text=user_input)])
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text

    assert "eligible" in final_response.lower() or "approve" in final_response.lower()

@pytest.mark.asyncio
async def test_underwriter_agent_sarah():
    """Verify underwriter_agent reasoning given a mock policy assessment."""
    test_app = App(name="loan_agent", root_agent=underwriter_agent)
    runner = InMemoryRunner(app=test_app)
    session = await runner.session_service.create_session(user_id="test_underwriter", app_name="loan_agent")
    
    mock_assessment = {
        "eligible": True,
        "reasoning": ["Strong credit", "Low DTI", "Verified income"],
        "recommended_rate": 6.5
    }
    
    user_input = f"Make a final decision for application APP-123 based on this assessment: {mock_assessment}. Applicant is user_01."
    
    final_response = ""
    async for event in runner.run_async(
        session_id=session.id,
        user_id="test_underwriter",
        new_message=UserContent(parts=[Part.from_text(text=user_input)])
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text

    assert "APPROVE" in final_response.upper()

@pytest.mark.asyncio
async def test_policy_expert_agent_gary_escalate():
    """Verify Gary Escalate triggers a manual review recommendation due to borderline credit."""
    test_app = App(name="loan_agent", root_agent=policy_expert_agent)
    runner = InMemoryRunner(app=test_app)
    session = await runner.session_service.create_session(user_id="test_gary", app_name="loan_agent")
    
    mock_report = {
        "credit_score": 640, # Sub-Prime Tier 3
        "employer": "Medianville Manufacturing",
        "income": 60000,
        "dti": 35.0,
        "fraud_risk": "MEDIUM"
    }
    
    user_input = f"Evaluate this investigation report: {mock_report}. Loan is $15,000. Applicant is user_04."
    
    final_response = ""
    async for event in runner.run_async(
        session_id=session.id,
        user_id="test_gary",
        new_message=UserContent(parts=[Part.from_text(text=user_input)])
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text

    # Policy for Tier 3 (> $10k) is MANUAL_REVIEW or ESCALATE
    assert "REVIEW" in final_response.upper() or "ESCALATE" in final_response.upper() or "MANUAL" in final_response.upper()

@pytest.mark.asyncio
async def test_underwriter_agent_jane_fraud():
    """Verify Jane Fraud is denied due to high risk."""
    test_app = App(name="loan_agent", root_agent=underwriter_agent)
    runner = InMemoryRunner(app=test_app)
    session = await runner.session_service.create_session(user_id="test_jane", app_name="loan_agent")
    
    mock_assessment = {
        "eligible": False,
        "reasoning": ["HIGH FRAUD RISK", "Identity flags triggered"],
        "recommended_action": "DENY"
    }
    
    user_input = f"Make a final decision for application APP-999 based on this assessment: {mock_assessment}. Applicant is user_05."
    
    final_response = ""
    async for event in runner.run_async(
        session_id=session.id,
        user_id="test_jane",
        new_message=UserContent(parts=[Part.from_text(text=user_input)])
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text

    assert "DENY" in final_response.upper() or "DENIED" in final_response.upper()
