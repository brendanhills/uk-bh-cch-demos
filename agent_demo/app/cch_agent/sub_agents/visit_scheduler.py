"""Visit Scheduler & EMR Sub-Agent for Cymbal Children's Hospital."""

import os
from google.adk.agents import Agent
from cch_agent.persona import CCH_SHARED_PERSONA
from cch_agent.tools import (
    calculate_home_care_financials,
    get_home_care_cost_estimate,
    approve_funding_subsidy,
    apply_subsidy_to_support_plan,
    get_available_support_times,
    schedule_home_care_visit,
    update_hospital_emr,
)

VISIT_SCHEDULER_INSTRUCTION = f"""
{CCH_SHARED_PERSONA}

<role>
    You are Jennie assisting a parent or carer with nurse visit scheduling, cost estimates, funding subsidies, and EMR updates for Cymbal Children's Hospital.
</role>

<instructions>
    1. **NO RE-GREETINGS OR RE-INTRODUCTIONS**: Never say "Hello", "G'day", "My name is Jennie", or "You've reached Cymbal Children's Hospital". Respond directly to the scheduling or financial request.
    2. **NO INTERNAL ROLE TITLES**: Never mention internal titles or sub-agent names.
    3. **Check Availability**: Call `get_available_support_times` when the parent requests appointment slots.
    4. **Exact Practitioner Mapping**: Map practitioner choices accurately (e.g. "Nurse Sarah") when calling `schedule_home_care_visit`.
    5. **Cost Estimates & Subsidies**: Use `calculate_home_care_financials` or `get_home_care_cost_estimate` to calculate visit costs and explain figures in natural spoken dollars.
    6. **EMR Logging**: Use `update_hospital_emr` to persist booking details into the child's clinical record.
</instructions>
"""

# ==============================================================================
# DEMO ARCHITECTURE RATIONALE: Why a Sub-Agent (visit_scheduler)?
#
# WHY A SUB-AGENT HERE?
# 1. Multi-Step Tool Orchestration: Coordinates complex multi-tool workflows:
#    Checking nurse slot availability -> Calculating Medicare/NDIS subsidies ->
#    Scheduling appointment -> Updating hospital EMR database records.
# 2. Domain Tool Isolation: Isolates financial calculation & appointment calendar tools away
#    from the primary conversation router to avoid tool registration clutter on the Live API model.
# ==============================================================================

visit_scheduler = Agent(
    name="visit_scheduler",
    model=os.getenv("SUB_AGENT_MODEL", "gemini-3.5-flash"),
    tools=[
        calculate_home_care_financials,
        get_home_care_cost_estimate,
        approve_funding_subsidy,
        apply_subsidy_to_support_plan,
        get_available_support_times,
        schedule_home_care_visit,
        update_hospital_emr,
    ],
    instruction=VISIT_SCHEDULER_INSTRUCTION,
)
