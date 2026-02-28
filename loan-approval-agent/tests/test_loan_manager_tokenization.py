import pytest
import asyncio
from unittest.mock import MagicMock, patch
from google.genai.types import (
    UserContent, Part, GenerateContentResponse, Candidate, Content, FunctionCall, FinishReason
)
from google.adk.runners import InMemoryRunner

# Mark as unit test dependency
pytestmark = [
    pytest.mark.depends(name="unit_tests"),
    pytest.mark.run(order=1)
]
from google.adk.models.base_llm import BaseLlm
from google.adk.models.registry import LLMRegistry
from loan_agent.agent import loan_manager
from loan_agent import config
from typing import ClassVar, List, Any

# Use TESTING latency
config.LATENCY_MODE = "TESTING"

# Subclass to add missing attributes for ADK runner
class MockGenerateContentResponse(GenerateContentResponse):
    model_config = {"extra": "allow"}
    
    def __init__(self, **data):
        super().__init__(**data)
        # ADK runner needs these attributes which might be missing in some versions of the type
        self.partial = False
        self.finish_reason = FinishReason.STOP
        if self.candidates:
             self.content = self.candidates[0].content
        else:
             self.content = None

    def model_dump(self, **kwargs):
        # Event model is strict and doesn't accept 'candidates'.
        # We must return a dict compatible with Event.model_validate.
        data = super().model_dump(**kwargs)
        if "candidates" in data:
            del data["candidates"]
        # Ensure content is present
        if self.content:
            data["content"] = self.content.model_dump(**kwargs) if hasattr(self.content, 'model_dump') else self.content
        data["partial"] = self.partial
        data["finish_reason"] = self.finish_reason
        return data

def create_mock_response(text=None, function_calls=None):
    parts = []
    if text:
        parts.append(Part(text=text))
    if function_calls:
        for fc in function_calls:
            parts.append(Part(function_call=fc))
            
    candidate = Candidate(
        content=Content(parts=parts, role="model"),
        finish_reason=FinishReason.STOP
    )
    
    return MockGenerateContentResponse(
        candidates=[candidate]
    )

class MockStreamingLlm(BaseLlm):
    next_responses: ClassVar[List[Any]] = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    @classmethod
    def supported_models(cls):
        return [r"^mock-model-.*"]
        
    async def generate_content_async(self, contents, **kwargs):
        if MockStreamingLlm.next_responses:
            response = MockStreamingLlm.next_responses.pop(0)
            yield response
        else:
            yield create_mock_response(text="No more responses")

# Register the mock model
LLMRegistry.register(MockStreamingLlm)

@pytest.mark.asyncio
async def test_loan_manager_tokenization_flow():
    # 1. Setup Mock Responses
    MockStreamingLlm.next_responses = [
        # Turn 1: Call register_application
        create_mock_response(
            function_calls=[
                FunctionCall(
                    name="register_application",
                    args={
                        "name": "Gary Escalate",
                        "income": 60000,
                        "employer": "Medianville Manufacturing",
                        "amount": 25000,
                        "purpose": "Business",
                        "gov_id": "900-00-3456"
                    }
                )
            ]
        ),
        # Turn 2: Call investigator with TOKEN
        create_mock_response(
            function_calls=[
                FunctionCall(
                    name="investigator_agent",
                    args={
                        "request": "Investigate loan for Applicant ID: token_900-00-3456. Amount: 25000. Purpose: Business."
                    }
                )
            ]
        )
    ]
    
    # 2. Configure Agent
    loan_manager.model = "mock-model-tokenization"
    
    # 3. Initialize Runner
    from loan_agent.agent import app
    runner = InMemoryRunner(app=app)
    session = await runner.session_service.create_session(app_name=runner.app_name, user_id="test_user")
    
    # 4. User Input
    user_input = (
        "Process a new loan application for name: Gary Escalate, "
        "gov_id: 900-00-3456, income: 60000, employer: Medianville Manufacturing, "
        "amount: 25000, purpose: Business"
    )
    user_msg = UserContent(parts=[Part(text=user_input)])
    
    print("\n--- Starting Tokenization Flow Test ---")
    step = 0
    register_called = False
    investigator_called = False
    
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=user_msg,
    ):
        step += 1
        print(f"DEBUG STEP {step}: Event type: {type(event)}")
                # basic inspection
        function_calls = []
        if hasattr(event, 'get_function_calls'):
            function_calls = event.get_function_calls()
        elif hasattr(event, 'tool_calls') and event.tool_calls:
             # Fallback/Old way
             for tc in event.tool_calls:
                 function_calls.extend(tc.function_calls)
        
        if function_calls:
            print(f"  Function Calls: {function_calls}")
            for fc in function_calls:
                print(f"STEP {step} TOOL: {fc.name} args={fc.args}")

                if fc.name == "register_application":
                    # Verify args (handling both dict and object access just in case)
                    gov_id = fc.args.get("gov_id") if isinstance(fc.args, dict) else getattr(fc.args, "gov_id", None)
                    if gov_id == "900-00-3456":
                            register_called = True

                if fc.name == "investigator_agent":
                    investigator_called = True
        else:
            print(f"  Event dir: {dir(event)}")
        
        if step >= 3:
            break
            
    assert register_called
    assert investigator_called
