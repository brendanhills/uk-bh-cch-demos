import time
import asyncio
import sys
import os

# Fix path to include project root
sys.path.append(os.getcwd())

from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent, GenerateContentResponse, Candidate, Content, FunctionCall

# Mock tools
def tool_a():
    """Tool A sleeps 1s"""
    print("Start A")
    time.sleep(1)
    print("End A")
    return "A done"

def tool_b():
    """Tool B sleeps 1s"""
    print("Start B")
    time.sleep(1)
    print("End B")
    return "B done"

class MockModel:
    def __init__(self):
        self.turn = 0
        
    def query(self, *args, **kwargs):
        # Return tool calls on first turn
        if self.turn == 0:
            self.turn += 1
            return GenerateContentResponse(
                candidates=[
                    Candidate(
                        content=Content(
                            parts=[
                                Part(function_call=FunctionCall(name="tool_a", args={})),
                                Part(function_call=FunctionCall(name="tool_b", args={}))
                            ],
                            role="model"
                        )
                    )
                ]
            )
        else:
            return GenerateContentResponse(
                candidates=[
                    Candidate(
                        content=Content(parts=[Part(text="Done")], role="model")
                    )
                ]
            )

async def probe():
    print("Probing Parallel Execution...")
    
    # Create Agent
    agent = Agent(
        model="mock-model",
        tools=[tool_a, tool_b]
    )
    
    # Patch the model client used by the agent
    # ADK Agents might use `self._model_client` or verify how they call it.
    # Usually `runner` calls `agent`, and `agent` calls `model`.
    
    # Let's inspect how to inject a mock model.
    # If not easy, we just rely on inspection of library code.
    pass

if __name__ == "__main__":
    # We will trust the library inspection for now as it's more reliable than guessing the mocking API
    print("Probe script placeholder - verifying via library inspection instead.")
