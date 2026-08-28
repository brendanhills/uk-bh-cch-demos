"""Clinical SOAP Note Generator Sub-Agent for Cymbal Children's Hospital."""

import os
from google.adk.agents import Agent
from cch_agent.persona import CCH_SHARED_PERSONA

SOAP_GENERATOR_INSTRUCTION = f"""
{CCH_SHARED_PERSONA}

<role>
    You are Jennie composing structured clinical SOAP notes for medical record exports at Cymbal Children's Hospital.
</role>

<instructions>
    1. **NO RE-GREETINGS OR RE-INTRODUCTIONS**: Never include conversational greetings or internal role titles in output summaries.
    2. **Subjective (S)**: Summarize parent/carer reported symptoms, concerns, and background history.
    3. **Objective (O)**: Document clinical observations extracted from discharge summary papers.
    4. **Assessment (A)**: State primary clinical diagnosis and home recovery status.
    5. **Plan (P)**: Detail home care nurse visit schedules, medication rules, follow-up dates, and applied funding subsidies.
</instructions>
"""

# ==============================================================================
# DEMO ARCHITECTURE RATIONALE: Why a Sub-Agent (soap_generator)?
#
# WHY A SUB-AGENT HERE?
# 1. Specialized Text Synthesis Prompt: Carries clinical record formatting rules
#    (Subjective, Objective, Assessment, Plan) without polluting general voice instructions.
# 2. Dual Re-use (Live API & REST API): Invoked both by the multi-agent router during live
#    calls AND by the FastAPI endpoint (@app.post("/api/session/soap_note")) for medical exports.
# ==============================================================================

soap_generator = Agent(
    name="soap_generator",
    model=os.getenv("SUB_AGENT_MODEL") or "gemini-2.5-flash-native-audio",
    instruction=SOAP_GENERATOR_INSTRUCTION,
)
