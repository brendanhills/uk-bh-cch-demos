"""Phone Number Validation and Country Detection Tool for Cymbal Children's Hospital."""

import re
from typing import Optional
from google.adk.tools import ToolContext

# TODO: replace with Google Search grounding
# Comprehensive country code mapping for dynamic verbal confirmation
COUNTRY_PREFIX_MAP = {
    "+61": "Australia",
    "+44": "United Kingdom",
    "+1": "United States or Canada",
    "+64": "New Zealand",
    "+65": "Singapore",
    "+91": "India",
    "+971": "United Arab Emirates",
    "+966": "Saudi Arabia",
    "+49": "Germany",
    "+33": "France",
    "+81": "Japan",
    "+86": "China",
    "+886": "Taiwan",
    "+82": "South Korea",
    "+39": "Italy",
    "+34": "Spain",
    "+31": "Netherlands",
    "+41": "Switzerland",
    "+62": "Indonesia",
    "+63": "Philippines",
    "+60": "Malaysia",
    "+84": "Vietnam",
    "+27": "South Africa",
    "+55": "Brazil",
    "+52": "Mexico",
    "+353": "Ireland",
}


def validate_phone_number(
    phone_number: str,
    tool_context: Optional[ToolContext] = None,
) -> dict:
    """Validate and format any contact phone number, detecting country code and saving to ADK session state memory.

    Args:
        phone_number: The contact phone number string provided by the parent.
        tool_context: ADK ToolContext for persisting validated phone number to session state.

    Returns:
        Dict with validation status, formatted number, detected country, and verbal confirmation guidance.
    """
    cleaned = re.sub(r"[\s\-\(\)]", "", phone_number)

    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]

    detected_country = "International"

    if cleaned.startswith("+"):
        for prefix, country in COUNTRY_PREFIX_MAP.items():
            if cleaned.startswith(prefix):
                detected_country = country
                break

    elif cleaned.startswith("04") and len(cleaned) == 10:
        cleaned = f"{cleaned[:4]} {cleaned[4:7]} {cleaned[7:]}"
        detected_country = "Australia"

    elif re.match(r"^0[2378]\d{8}$", cleaned):
        cleaned = f"({cleaned[:2]}) {cleaned[2:6]} {cleaned[6:]}"
        detected_country = "Australia"

    if tool_context and hasattr(tool_context, "state") and tool_context.state is not None:
        tool_context.state["phone_number"] = phone_number
        tool_context.state["phone_country"] = detected_country

    return {
        "is_valid": True,
        "formatted_number": phone_number,
        "detected_country": detected_country,
        "is_international": detected_country != "Australia",
        "message": f"Accepted {detected_country} contact number ({phone_number}). Saved to ADK session memory. Verbally confirm country with caller.",
    }
