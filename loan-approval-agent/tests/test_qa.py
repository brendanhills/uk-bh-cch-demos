
import pytest
import os
import sys

# Mark as unit test dependency
pytestmark = [
    pytest.mark.depends(name="unit_tests"),
    pytest.mark.run(order=1)
]
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
from loan_agent.agent import loan_manager

@pytest.mark.asyncio
@pytest.mark.skip(reason="Interactive Validation deferred to Phase 4")
async def test_qa_missing_info():
    """
    Test that the agent asks a clarifying question when 'Employer' is Unknown.
    Uses mock applicant 12349.
    """
    from loan_agent.agent import app
    runner = InMemoryRunner(app=app)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_qa_user"
    )

    # Input for Jane Fraud (12349) with "Unknown" employer
    user_input = (
        "Begin review for applicant_id: 12349. "
        "Requested Loan Amount: $5,000. "
        "Loan Purpose: Personal."
    )
    content = UserContent(parts=[Part(text=user_input)])

    final_response = ""
    question_asked = False
    
    # Logging helper
    def log(msg):
        with open("qa_debug.log", "a") as f:
            f.write(msg + "\n")

    log("STARTING TEST")
    
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    log(f"AGENT: {part.text}")
                    final_response += part.text
                    if "Question:" in part.text:
                        question_asked = True

    # Check if a question was asked
    if not question_asked:
        log(f"FINAL RESPONSE (No Question): {final_response}")
        
    assert question_asked, f"Agent did not ask a question. Final response: {final_response}"
    assert "Final Decision:" not in final_response, "Agent made a final decision instead of asking a question."

    # Part 2: Answer the question
    log("PROVIDING ANSWER")
    answer = "My employer is Google DeepMind. My confirmed annual income is returned as 80000."
    answer_content = UserContent(parts=[Part(text=answer)])
    
    final_decision_made = False
    final_res_2 = ""
    
    try:
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=answer_content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        log(f"AGENT (Turn 2): {part.text}")
                        final_res_2 += part.text
                        if "Final Decision:" in part.text:
                            final_decision_made = True
            else:
                log(f"EVENT (Turn 2): {event}")

        if not final_decision_made:
            log(f"FINAL RESPONSE 2 (No Decision): {final_res_2}")
            
        assert final_decision_made, f"Agent did not make a final decision after answer. Response: {final_res_2}"
        assert "APPROVE" in final_res_2.upper() or "DENY" in final_res_2.upper(), "Decision format incorrect."
        log("TEST PASSED")

    except Exception as e:
        log(f"TEST FAILED: {e}")
        raise e
