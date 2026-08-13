"""Master Concierge Router Agent for Cymbal Children's Hospital ADK 2.0 System."""

import os
from google.adk.agents import Agent
from google.adk.tools import AgentTool

from cch_agent.persona import CCH_SHARED_PERSONA
from cch_agent.tools import validate_phone_number, record_patient_identity, google_search
from cch_agent.tools.telemetry import TimedAgentTool
from cch_agent.sub_agents import (
    patient_verifier,
    document_scanner,
    visit_scheduler,
    soap_generator,
)

ROUTER_INSTRUCTION = f"""
{CCH_SHARED_PERSONA}

<role>
    You are Jennie, the Healthcare Coordinator for Cymbal Children's Hospital.
    Your role is to warmly answer calls from parents and carers, welcome them to Cymbal Children's Hospital, and assist them with identity verification, discharge paperwork, home care nurse visit bookings, funding subsidies, and hospital record updates.
</role>

<instructions>
    1. **STRICT SINGLE AGENT PERSONA**: To the user, there is ONLY ONE agent speaking: Jennie. NEVER mention sub-agents, internal roles, transfers, or delegation.
    2. **Warm Hospital Answering Script**: When the caller first speaks or says "Hi", answer with a warm, professional hospital greeting:
       "Hello, thank you for calling Cymbal Children's Hospital. My name is Jennie. How can I help you today?"
    3. **Natural Identity Verification**: Once the parent explains what they need or greets you back, politely ask for their name and best contact phone number so you can locate their child's file.
    4. **STRICT CAMERA GUARDRAIL (NO HALLUCINATED VISION)**:
       - NEVER claim, pretend, or hallucinate that you can see a document, discharge paper, or medical note UNLESS a document image attachment payload has actually been received!
       - If the caller says "let me show you", "here it is", or "I have the papers", but NO document image has been received yet, DO NOT say "I can see the discharge summary now"!
       - Instead, instruct the caller: "Please click the Camera button at the bottom and align your document in the viewfinder to snap a picture for me!"
    5. **No Filler Platitudes**: Never use random filler phrases like "No worries at all" or "To start..." when answering a greeting.
    6. **Seamless Handoffs**: Delegate specialized tasks to expert tools (`patient_verifier`, `document_scanner`, `visit_scheduler`, `soap_generator`) behind the scenes so the parent experiences a smooth, continuous conversation with Jennie.
</instructions>
"""

# ==============================================================================
# DEMO ARCHITECTURE RATIONALE: Router Agent vs. Tools & Sub-Agents
# 
# 1. WHY AN AGENT (cch_concierge_router)?
#    - Maintains real-time conversational state over Gemini Live WebSocket sessions.
#    - Enforces hospital persona ("Jennie"), system prompt guardrails, and conversational flow.
#    - Dynamically evaluates user turn intent to choose between fast-path tools or sub-agent delegation.
#
# 2. WHY DIRECT ROUTER TOOLS (validate_phone_number, record_patient_identity)?
#    - Fast-Path Execution (< 10ms): High-frequency actions executed directly in Python memory.
#    - Zero Extra LLM Latency: Bypasses sub-agent delegation turns for instant identity validation.
#
# 3. WHY SUB-AGENTS (patient_verifier, document_scanner, visit_scheduler, soap_generator)?
#    - Encapsulated Prompt Scope: Each sub-agent carries specialized instructions & context.
#    - Unstructured Reasoning: Sub-agents handle fuzzy tasks like extracting text from medical paper photos.
#    - Performance Optimized: Wrapped in TimedAgentTool(..., skip_summarization=True) for ≤0.5s turns.
# ==============================================================================

# Master Concierge Router Agent configured for Live API BIDI WebSocket Session
agent = Agent(
    name="cch_concierge_router",
    model=os.getenv("LIVE_MODEL_ID", "gemini-live-2.5-flash-native-audio"),
    tools=[
        validate_phone_number,    # Direct Fast-Path Tool (<10ms execution)
        record_patient_identity,  # Direct Fast-Path Tool (<10ms execution)
        google_search,            # Direct Search Grounding Tool
        TimedAgentTool(patient_verifier),   # Sub-Agent Delegated Tool (≤0.5s turn)
        TimedAgentTool(document_scanner),   # Sub-Agent Delegated Tool (Multimodal OCR)
        TimedAgentTool(visit_scheduler),    # Sub-Agent Delegated Tool (Scheduling Logic)
        TimedAgentTool(soap_generator),     # Sub-Agent Delegated Tool (Clinical Notes)
    ],
    instruction=ROUTER_INSTRUCTION,
)
