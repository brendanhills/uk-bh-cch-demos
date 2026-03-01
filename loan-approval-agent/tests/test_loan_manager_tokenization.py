import pytest
import asyncio
import json
import os
from unittest.mock import patch, MagicMock
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
from loan_agent.agent import loan_manager
from loan_agent.utils.audit_logger import LOG_FILE
from loan_agent import config

# Mark as unit test dependency
pytestmark = [
    pytest.mark.depends(name="unit_tests"),
    pytest.mark.run(order=1)
]

@pytest.mark.asyncio
async def test_loan_manager_tokenization_flow():
    """Verify that the Loan Manager correctly tokenizes Gov ID before tools see it."""
    
    # Force TESTING latency for speed
    config.LATENCY_MODE = "TESTING"
    
    # 1. Setup Runner
    runner = InMemoryRunner(agent=loan_manager, app_name="loan_agent")
    session = await runner.session_service.create_session(app_name="loan_agent", user_id="test_user")
    
    # 2. User Input with PII (SSN)
    raw_ssn = "900-00-3456"
    user_input = (
        f"Process a new loan application for name: Gary Escalate, "
        f"gov_id: {raw_ssn}, income: 60000, employer: Medianville Manufacturing, "
        f"amount: 15000, purpose: Business, monthly_payment: 300"
    )
    
    # Clear logs before test
    if os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w').close()

    # We only run until the registration event is found to save time
    async for _ in runner.run_async(
        session_id=session.id,
        user_id="test_user",
        new_message=UserContent(parts=[Part(text=user_input)])
    ):
        # Break early if we see the tool call in the logs
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                if "Application_Registered" in f.read():
                    break

    # 3. Verify Tokenization via Logs
    assert os.path.exists(LOG_FILE)
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
        
    found_token = False
    for line in lines:
        entry = json.loads(line)
        if entry.get("applicant_id") == "user_04":
            found_token = True
        
        log_str = json.dumps(entry)
        assert raw_ssn not in log_str, f"Found raw SSN in logs! {log_str}"

    assert found_token, "Did not find the tokenized ID (user_04) in any log entry."
