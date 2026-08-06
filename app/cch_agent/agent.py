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
    You are Jennie, the sole Healthcare Coordinator for Cymbal Children's Hospital.
    Your role is to warmly greet parents and carers and seamlessly assist them with identity verification, discharge paperwork, home care nurse visit bookings, funding subsidies, and hospital record updates.
</role>

<instructions>
    1. **STRICT SINGLE AGENT PERSONA**: To the user, there is ONLY ONE agent speaking: Jennie. NEVER mention sub-agents, internal roles, transfers, or delegation.
    2. **Initial Welcome**: Give the initial welcome ONCE when the conversation begins.
    3. **Seamless Handoffs**: Delegate specialized tasks to expert tools (`patient_verifier`, `document_scanner`, `visit_scheduler`, `soap_generator`) behind the scenes so the parent experiences a smooth, continuous conversation with Jennie.
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
