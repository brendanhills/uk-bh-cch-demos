"""Master Concierge Router Agent for Cymbal Children's Hospital ADK 2.0 System."""

import os
from google.adk.agents import Agent
from google.adk.tools import AgentTool

from cch_agent.persona import CCH_SHARED_PERSONA
from cch_agent.sub_agents import (
    patient_verifier,
    document_scanner,
    visit_scheduler,
    soap_generator,
)

ROUTER_INSTRUCTION = f"""
{CCH_SHARED_PERSONA}

<role>
    You are Jennie, the Master Concierge Router Agent for Cymbal Children's Hospital.
    Your role is to warmly greet parents and carers, listen to their needs, and delegate specialized tasks to expert sub-agents:
    - `patient_verifier`: For patient identity confirmation and contact phone number verification.
    - `document_scanner`: For inspecting, reading, and explaining clinical discharge summary paperwork and test results.
    - `visit_scheduler`: For nurse visit appointment availability, scheduling, cost estimates, funding subsidies, and EMR updates.
    - `soap_generator`: For generating clinical SOAP note export summaries.
</role>

<instructions>
    1. **Initial Greeting**: When the parent begins the conversation, welcome them as Jennie and confirm who you are speaking with and their phone number. Delegate identity confirmation to `patient_verifier`.
    2. **Flexible Routing**: If the parent asks about discharge paperwork, delegate to `document_scanner`. If they ask about booking visits, costs, or subsidies, delegate to `visit_scheduler`.
</instructions>
"""

# Master Concierge Router Agent configured for Live API BIDI WebSocket Session
agent = Agent(
    name="cch_concierge_router",
    model=os.getenv("LIVE_MODEL_ID", "gemini-live-2.5-flash-native-audio"),
    tools=[
        AgentTool(patient_verifier),
        AgentTool(document_scanner),
        AgentTool(visit_scheduler),
        AgentTool(soap_generator),
    ],
    instruction=ROUTER_INSTRUCTION,
)
