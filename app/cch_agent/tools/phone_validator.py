"""Australian Phone Number Validation Tool for Cymbal Children's Hospital."""

import re


def validate_australian_phone_number(phone_number: str) -> dict:
    """Validate whether a contact phone number is a valid Australian mobile or landline number.

    Args:
        phone_number: The contact phone number string provided by the parent.

    Returns:
        Dict with validation status, detected country code, and user guidance.
    """
    cleaned = re.sub(r"[\s\-\(\)]", "", phone_number)

    # Check for international country codes
    if cleaned.startswith("+44") or cleaned.startswith("0044"):
        return {
            "is_valid_australian": False,
            "detected_country": "United Kingdom (+44)",
            "message": "Provided number is a UK international number (+44). Cymbal Children's Hospital is based in Australia and requires an Australian contact number (mobile 04xx xxx xxx or landline 02/03/07/08).",
        }

    if cleaned.startswith("+") and not cleaned.startswith("+61"):
        return {
            "is_valid_australian": False,
            "detected_country": "International",
            "message": "Provided number is an international non-Australian number. Please request an Australian mobile (04xx xxx xxx) or landline contact number.",
        }

    # Normalize +614xxx to 04xxx
    if cleaned.startswith("+61"):
        cleaned = "0" + cleaned[3:]

    # Australian mobile pattern: 04xx xxx xxx (10 digits starting with 04)
    if re.match(r"^04\d{8}$", cleaned):
        formatted = f"{cleaned[:4]} {cleaned[4:7]} {cleaned[7:]}"
        return {
            "is_valid_australian": True,
            "formatted_number": formatted,
            "detected_country": "Australia",
            "type": "Mobile",
            "message": f"Valid Australian mobile number ({formatted}).",
        }

    # Australian landline pattern: 02, 03, 07, 08 (10 digits)
    if re.match(r"^0[2378]\d{8}$", cleaned):
        formatted = f"({cleaned[:2]}) {cleaned[2:6]} {cleaned[6:]}"
        return {
            "is_valid_australian": True,
            "formatted_number": formatted,
            "detected_country": "Australia",
            "type": "Landline",
            "message": f"Valid Australian landline number ({formatted}).",
        }

    return {
        "is_valid_australian": False,
        "detected_country": "Unknown",
        "message": "Number does not match Australian phone formatting (04xx xxx xxx for mobile or 02/03/07/08 for landline). Please confirm an Australian contact number.",
    }
