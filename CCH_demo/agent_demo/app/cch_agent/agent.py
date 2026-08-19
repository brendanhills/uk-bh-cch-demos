"""Master Concierge Router Agent for Cymbal Children's Hospital ADK 2.0 System."""

import os
from google.adk.agents import Agent
from google.adk.tools import AgentTool

from cch_agent.persona import CCH_SHARED_PERSONA
from cch_agent.tools import validate_phone_number, record_patient_identity, google_search
from cch_agent.tools.document_scanner_tools import request_document_scan
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
    2. **Warm Hospital Answering Script**: When the caller connects or greets you, deliver a warm, professional hospital greeting:
       "Hello, thank you for calling Cymbal Children's Hospital. My name is Jennie. How can I help you today?"
    3. **MANDATORY IDENTITY & PHONE VERIFICATION**:
       - Before processing discharge papers or scheduling visits, politely ask the caller for their name and best contact phone number so you can locate their child's file.
       - Reassure callers that Cymbal Children's Hospital accepts both Australian national numbers (`04xx`, `02/03/07/08`) and international numbers (`+1`, `+44`, `+971`, etc.) for international visitors and tourists in Australia.
       - Immediately execute `record_patient_identity` and `validate_phone_number` when details are provided.
    4. **STRICT CAMERA GUARDRAIL & AUTOMATIC CAMERA TRIGGER**:
       - When the caller asks to scan, inspect, or show a document, ALWAYS call `request_document_scan` to automatically open the camera viewfinder UI overlay on their screen!
       - NEVER claim or pretend that you can see a document UNLESS a document image attachment payload has actually been received.
       - If no image has arrived yet, execute `request_document_scan` and instruct the caller: "I'm opening the document scanner on your screen now. Please align your document in the viewfinder and snap a picture for me!"
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
# 2. WHY DIRECT ROUTER TOOLS (validate_phone_number, record_patient_identity, request_document_scan)?
#    - Fast-Path Execution (< 10ms): High-frequency actions executed directly in Python memory.
#    - Zero Extra LLM Latency: Bypasses sub-agent delegation turns for instant camera triggering & identity validation.
#
# 3. WHY SUB-AGENTS (patient_verifier, document_scanner, visit_scheduler, soap_generator)?
#    - Encapsulated Prompt Scope: Each sub-agent carries specialized instructions & context.
#    - Unstructured Reasoning: Sub-agents handle fuzzy tasks like extracting text from medical paper photos.
#    - Performance Optimized: Wrapped in TimedAgentTool(..., skip_summarization=True) for ≤0.5s turns.
# ==============================================================================

# Master Concierge Router Agent configured for Live API BIDI WebSocket Session
agent = Agent(
    name="cch_concierge_router",
    model=os.getenv("LIVE_MODEL_ID") or os.getenv("DEMO_AGENT_MODEL") or "gemini-live-2.5-flash-native-audio",
    tools=[
        validate_phone_number,    # Direct Fast-Path Tool (<10ms execution)
        record_patient_identity,  # Direct Fast-Path Tool (<10ms execution)
        request_document_scan,    # Direct Fast-Path Tool (<10ms camera trigger)
        google_search,            # Direct Search Grounding Tool
        TimedAgentTool(patient_verifier),   # Sub-Agent Delegated Tool (≤0.5s turn)
        TimedAgentTool(document_scanner),   # Sub-Agent Delegated Tool (Multimodal OCR)
        TimedAgentTool(visit_scheduler),    # Sub-Agent Delegated Tool (Scheduling Logic)
        TimedAgentTool(soap_generator),     # Sub-Agent Delegated Tool (Clinical Notes)
    ],
    instruction=ROUTER_INSTRUCTION,
)
