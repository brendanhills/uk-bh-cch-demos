import os
from typing import List, Optional
import re
import httpx
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.adk import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner

app = FastAPI(title="Enterprise Agent Portal")

# --- Model Armor Component ---
class ModelArmor:
    """Simulates blocking and redacting of unapproved content."""
    def __init__(self, blocked_keywords: List[str]):
        self.blocked_pattern = re.compile(
            r'\b(' + '|'.join(map(re.escape, blocked_keywords)) + r')\b', 
            re.IGNORECASE
        )

    def redact(self, text: str) -> str:
        return self.blocked_pattern.sub("[REDACTED BY MODEL ARMOR]", text)

    def has_blocked_content(self, text: str) -> bool:
        return bool(self.blocked_pattern.search(text))

armor = ModelArmor(blocked_keywords=["SECRET_PROJECT_X", "INTERNAL_ONLY", "CREDENTIALS"])

# --- Sub-Agent Communication Tools ---
async def call_security_agent(query: str) -> str:
    """Calls the specialized Security Agent to analyze commits or security policies."""
    async with httpx.AsyncClient() as client:
        try:
            # ADK /run endpoint expects { "message": "...", "app_name": "..." }
            response = await client.post(
                "http://127.0.0.1:8081/run",
                json={"message": query, "app_name": "security_analyst"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json().get("text", "Error: No response text from Security Agent.")
        except Exception as e:
            return f"Security Agent Error: {str(e)}"

async def call_geo_agent(query: str) -> str:
    """Calls the specialized Geopolitical Agent for regional insights."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://127.0.0.1:8082/run",
                json={"message": query, "app_name": "geo_researcher"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json().get("text", "Error: No response text from Geo Agent.")
        except Exception as e:
            return f"Geo Agent Error: {str(e)}"

security_tool = FunctionTool(func=call_security_agent)
geo_tool = FunctionTool(func=call_geo_agent)

# --- Enterprise Portal Agent ---
portal_agent = Agent(
    name="enterprise_portal",
    model="gemini-2.0-flash-001",
    instruction="""You are the CSIRO Enterprise Agent Portal. 
    Your job is to assist users by coordinating between specialized agents.
    - For security, GitHub commit analysis, or policy checks, use 'call_security_agent'.
    - For geopolitical insights, regional trade, or stability queries, use 'call_geo_agent'.
    Always apply security best practices. If you suspect sensitive data is being requested, be cautious.""",
    tools=[security_tool, geo_tool]
)

# Initialize the Runner for the portal agent
portal_runner = InMemoryRunner(agent=portal_agent)

# --- API Models ---
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    armor_applied: bool

# --- Routes ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. Input Filtering (Model Armor)
    redacted_input = armor.redact(request.message)
    input_armor_triggered = armor.has_blocked_content(request.message)

    # 2. Agent Processing
    try:
        # Use run_debug for simple one-off interaction in the MVP
        events = await portal_runner.run_debug(redacted_input, session_id=request.session_id)
        
        # Extract text from events. ADK 2.0 events have a .text property if they are model responses.
        response_text = ""
        for event in events:
            if hasattr(event, "text") and event.text:
                response_text = event.text # Take the last one or accumulate
        
        if not response_text:
            response_text = "I processed your request but have no text response."
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portal Agent Error: {str(e)}")

    # 3. Output Filtering (Model Armor)
    final_response = armor.redact(response_text)
    output_armor_triggered = armor.has_blocked_content(response_text)

    return ChatResponse(
        response=final_response,
        armor_applied=input_armor_triggered or output_armor_triggered
    )

@app.get("/")
def read_root():
    return {"status": "Enterprise Portal is running with distributed agent support"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
