"""Domain function tools for Cymbal Children's Hospital ADK 2.0 Concierge."""

from cch_agent.tools.cost_calculator import (
    calculate_home_care_financials,
    get_home_care_cost_estimate,
    approve_funding_subsidy,
    apply_subsidy_to_support_plan,
)
from cch_agent.tools.scheduling import (
    get_available_support_times,
    schedule_home_care_visit,
    update_hospital_emr,
)
from cch_agent.tools.phone_validator import (
    validate_phone_number,
    validate_phone_number as validate_australian_phone_number,
)
from cch_agent.tools.identity import record_patient_identity
from cch_agent.tools.telemetry import TimedAgentTool, get_sub_agent_telemetry_summary
from cch_agent.tools.document_scanner_tools import request_document_scan
from cch_agent.tools.search_tools import google_search

__all__ = [
    "calculate_home_care_financials",
    "get_home_care_cost_estimate",
    "approve_funding_subsidy",
    "apply_subsidy_to_support_plan",
    "get_available_support_times",
    "schedule_home_care_visit",
    "update_hospital_emr",
    "validate_phone_number",
    "validate_australian_phone_number",
    "record_patient_identity",
    "TimedAgentTool",
    "get_sub_agent_telemetry_summary",
    "request_document_scan",
    "google_search",
]
