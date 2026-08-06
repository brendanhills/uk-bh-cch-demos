"""Master Concierge Router Agent for Cymbal Children's Hospital ADK 2.0 System."""

import os
from typing import Any, Dict, List

from google.adk.agents import Agent
from google.adk.tools import AgentTool

# =====================================================================
# Specialized CCH Clinical & Scheduling Tools
# =====================================================================

def get_available_support_times(
    requested_date: str, service_type: str = "Pediatric Nurse Visit"
) -> Dict[str, Any]:
    """Look up available clinical home care appointment slots for a specified future date.

    Args:
        requested_date: The requested appointment date (e.g. 'tomorrow', 'Friday', '2026-07-22').
        service_type: Type of home care service. Defaults to 'Pediatric Nurse Visit'.
    """
    return {
        "requested_date": requested_date,
        "service_type": service_type,
        "available_slots": [
            {
                "time": "09:00 AM",
                "practitioner": "Nurse Sarah",
                "status": "Available",
            },
            {
                "time": "11:30 AM",
                "practitioner": "Nurse Michael",
                "status": "Available",
            },
            {
                "time": "02:00 PM",
                "practitioner": "Nurse Sarah",
                "status": "Available",
            },
            {
                "time": "04:30 PM",
                "practitioner": "Nurse Michael",
                "status": "Available",
            },
        ],
        "notes": "All appointments include pediatric vital signs assessment and medication review.",
    }


def schedule_home_care_visit(
    date: str,
    time: str,
    child_name: str,
    parent_name: str,
    service_type: str = "Pediatric Nurse Visit",
    practitioner: str = None,
) -> Dict[str, Any]:
    """Schedule and confirm a specialized pediatric nurse home visit.

    Args:
        date: The confirmed date for the visit.
        time: The confirmed time for the visit (e.g. '09:00 AM', '2:00 PM').
        child_name: Name of the child/patient receiving care.
        parent_name: Name of the parent/carer confirming the booking.
        service_type: Type of home care service. Defaults to 'Pediatric Nurse Visit'.
        practitioner: Optional specific nurse requested (e.g. 'Nurse Sarah').
    """
    assigned_nurse = practitioner if practitioner else "Nurse Sarah"
    return {
        "booking_status": "Confirmed",
        "booking_id": "BK-CCH-2026-881",
        "child_name": child_name,
        "parent_name": parent_name,
        "service_type": service_type,
        "date": date,
        "time": time,
        "assigned_practitioner": assigned_nurse,
        "confirmation_message": f"Successfully booked {service_type} with {assigned_nurse} for {child_name} on {date} at {time}.",
    }


def update_hospital_emr(
    child_name: str,
    booked_visits: List[str] = None,
    approved_subsidies: List[str] = None,
    clinical_notes: str = None,
) -> Dict[str, Any]:
    """Update and persist clinical records, booked visits, and approved subsidies into the Hospital EMR system.

    Args:
        child_name: Name of the child patient.
        booked_visits: List of confirmed home care visits.
        approved_subsidies: List of approved funding subsidies.
        clinical_notes: Summary of clinical assessment notes.
    """
    return {
        "emr_update_status": "Success",
        "child_name": child_name,
        "patient_id": "P-CCH-883012",
        "vitals_logged": True,
        "booked_visits": booked_visits,
        "approved_subsidies": approved_subsidies,
        "clinical_notes_saved": clinical_notes,
        "timestamp": "2026-07-21T12:45:13Z",
    }


# =====================================================================
# Master Concierge Router Configuration
# =====================================================================

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

<persona>
    Maintain a warm, empathetic, professional Australian pediatric healthcare tone. Speak naturally and listen attentively without using canned or patronizing scripts.
</persona>

<instructions>
    1. **Initial Greeting**: When the parent begins the conversation, welcome them as Jennie and confirm who you are speaking with and their phone number. Delegate identity confirmation to `patient_verifier`.
    2. **Flexible Routing**: If the parent asks about discharge paperwork, delegate to `document_scanner`. If they ask about booking visits, costs, or subsidies, delegate to `visit_scheduler`.
</instructions>
"""

# Master Concierge Router Agent
agent = Agent(
    name="cch_concierge_router",
    model=os.getenv(
        "DEMO_AGENT_MODEL", "gemini-live-2.5-flash-native-audio"
    ),
    tools=[
        AgentTool(patient_verifier),
        AgentTool(document_scanner),
        AgentTool(visit_scheduler),
        AgentTool(soap_generator),
    ],
    instruction=ROUTER_INSTRUCTION,
)
