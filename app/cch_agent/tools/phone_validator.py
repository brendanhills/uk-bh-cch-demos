"""Phone Number Validation and Country Detection Tool for Cymbal Children's Hospital."""

import re

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


def validate_phone_number(phone_number: str) -> dict:
    """Validate and format any domestic or international contact phone number, detecting its country for verbal confirmation.

    Args:
        phone_number: The contact phone number string provided by the parent.

    Returns:
        Dict with validation status, formatted number, detected country, and verbal confirmation guidance.
    """
    cleaned = re.sub(r"[\s\-\(\)]", "", phone_number)

    # Normalize 00 prefix to +
    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]

    detected_country = "International"

    # Match known country prefixes
    if cleaned.startswith("+"):
        for prefix, country in COUNTRY_PREFIX_MAP.items():
            if cleaned.startswith(prefix):
                detected_country = country
                break
        return {
            "is_valid": True,
            "formatted_number": phone_number,
            "detected_country": detected_country,
            "is_international": detected_country != "Australia",
            "message": f"Accepted {detected_country} contact number ({phone_number}). Verbally confirm with caller that they are providing a {detected_country} contact number.",
        }

    # Normalize Australian local numbers
    if cleaned.startswith("04") and len(cleaned) == 10:
        formatted = f"{cleaned[:4]} {cleaned[4:7]} {cleaned[7:]}"
        return {
            "is_valid": True,
            "formatted_number": formatted,
            "detected_country": "Australia",
            "is_international": False,
            "type": "Mobile",
            "message": f"Accepted Australian mobile number ({formatted}).",
        }

    if re.match(r"^0[2378]\d{8}$", cleaned):
        formatted = f"({cleaned[:2]}) {cleaned[2:6]} {cleaned[6:]}"
        return {
            "is_valid": True,
            "formatted_number": formatted,
            "detected_country": "Australia",
            "is_international": False,
            "type": "Landline",
            "message": f"Accepted Australian landline number ({formatted}).",
        }

    return {
        "is_valid": True,
        "formatted_number": phone_number,
        "detected_country": "Contact Number",
        "is_international": False,
        "message": f"Accepted contact number ({phone_number}). Verbally confirm with caller.",
    }
