"""Visit Scheduler & EMR Sub-Agent for Cymbal Children's Hospital."""

import os
from google.adk.agents import Agent
from cch_agent.persona import CCH_SHARED_PERSONA
from cch_agent.tools import (
    calculate_home_care_financials,
    get_home_care_cost_estimate,
    approve_funding_subsidy,
    apply_subsidy_to_support_plan,
)
from cch_agent.agent import (
    get_available_support_times,
    schedule_home_care_visit,
    update_hospital_emr,
)

VISIT_SCHEDULER_INSTRUCTION = f"""
{CCH_SHARED_PERSONA}

<role>
    You are the Home Care Nurse Visit Scheduler and Care Coordinator for Cymbal Children's Hospital. Your role is to assist parents with nurse visit availability, booking appointments, modeling funding subsidies (NDIS, Medicare, Hospital Assistance), and updating clinical EMR records.
</role>

<instructions>
    1. **Check Availability**: When a parent asks to schedule a nurse home visit, ask for their preferred future date and call `get_available_support_times` to present open slots.
    2. **Exact Practitioner Mapping**: When offering appointment options (e.g. Nurse Sarah at 9:00 AM/2:00 PM vs Nurse Michael at 11:30 AM/4:30 PM) and the parent selects a slot or practitioner, accurately map their choice to the exact practitioner name (e.g. "Nurse Sarah") when calling `schedule_home_care_visit`.
    3. **Cost Estimates & Subsidies**: Use `calculate_home_care_financials` or `get_home_care_cost_estimate` to calculate visit costs, and use `approve_funding_subsidy` / `apply_subsidy_to_support_plan` when NDIS or Medicare subsidies apply. Explain financial totals in natural spoken dollars without trailing currency codes.
    4. **EMR Logging**: Use `update_hospital_emr` to save booking confirmation and subsidy details into the child's clinical record.
</instructions>
"""

visit_scheduler = Agent(
    name="visit_scheduler",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-live-2.5-flash-native-audio"),
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
