"""Global Patient & Caller Identity State Management Tool for Cymbal Children's Hospital."""

from typing import Optional
from google.adk.tools import ToolContext


def record_patient_identity(
    caller_name: Optional[str] = None,
    patient_name: Optional[str] = None,
    phone_number: Optional[str] = None,
    tool_context: Optional[ToolContext] = None,
) -> dict:
    """Global tool to save structured patient and caller identity facts into ADK short-term session state memory.

    Args:
        caller_name: Name of the parent/carer caller (e.g., "Brendan").
        patient_name: Name of the pediatric patient child (e.g., "Leo").
        phone_number: Contact phone number string provided by caller.
        tool_context: ADK ToolContext instance for persisting session state across all agents.

    Returns:
        Dict confirming saved identity facts in ADK session memory.
    """
    saved_state = {}

    if tool_context and hasattr(tool_context, "state") and tool_context.state is not None:
        if caller_name:
            tool_context.state["caller_name"] = caller_name
            saved_state["caller_name"] = caller_name
        if patient_name:
            tool_context.state["patient_name"] = patient_name
            saved_state["patient_name"] = patient_name
        if phone_number:
            tool_context.state["phone_number"] = phone_number
            saved_state["phone_number"] = phone_number

    return {
        "status": "Saved to Global Session Memory",
        "caller_name": caller_name,
        "patient_name": patient_name,
        "phone_number": phone_number,
        "message": f"Recorded identity facts in ADK Session Memory: Caller='{caller_name}', Patient='{patient_name}', Phone='{phone_number}'. All sub-agents now have global access to these facts.",
    }
