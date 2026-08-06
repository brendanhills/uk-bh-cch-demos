"""Phone Number Validation and Country Detection Tool for Cymbal Children's Hospital."""

import re


def validate_phone_number(phone_number: str) -> dict:
    """Validate and format a contact phone number, detecting its country for verbal confirmation.

    Args:
        phone_number: The contact phone number string provided by the parent.

    Returns:
        Dict with validation status, formatted number, detected country, and verbal confirmation guidance.
    """
    cleaned = re.sub(r"[\s\-\(\)]", "", phone_number)

    # UK international number (+44)
    if cleaned.startswith("+44") or cleaned.startswith("0044"):
        digits = cleaned[3:] if cleaned.startswith("+44") else cleaned[4:]
        formatted = f"+44 {digits[:4]} {digits[4:7]} {digits[7:]}" if len(digits) >= 10 else phone_number
        return {
            "is_valid": True,
            "formatted_number": formatted,
            "detected_country": "UK",
            "message": f"Accepted UK contact number ({formatted}). Verbally confirm with caller that they are providing a UK contact number.",
        }

    # US/Canada international number (+1)
    if cleaned.startswith("+1") or cleaned.startswith("001"):
        return {
            "is_valid": True,
            "formatted_number": phone_number,
            "detected_country": "US/Canada",
            "message": f"Accepted US/Canada contact number ({phone_number}). Verbally confirm country with caller.",
        }

    # Other international numbers starting with +
    if cleaned.startswith("+"):
        return {
            "is_valid": True,
            "formatted_number": phone_number,
            "detected_country": "International",
            "message": f"Accepted international contact number ({phone_number}). Verbally confirm country with caller.",
        }

    # Normalize +614xxx to 04xxx
    if cleaned.startswith("+61"):
        cleaned = "0" + cleaned[3:]

    # Australian mobile pattern: 04xx xxx xxx
    if re.match(r"^04\d{8}$", cleaned):
        formatted = f"{cleaned[:4]} {cleaned[4:7]} {cleaned[7:]}"
        return {
            "is_valid": True,
            "formatted_number": formatted,
            "detected_country": "Australia",
            "type": "Mobile",
            "message": f"Accepted Australian mobile number ({formatted}).",
        }

    # Australian landline pattern: 02, 03, 07, 08
    if re.match(r"^0[2378]\d{8}$", cleaned):
        formatted = f"({cleaned[:2]}) {cleaned[2:6]} {cleaned[6:]}"
        return {
            "is_valid": True,
            "formatted_number": formatted,
            "detected_country": "Australia",
            "type": "Landline",
            "message": f"Accepted Australian landline number ({formatted}).",
        }

    return {
        "is_valid": True,
        "formatted_number": phone_number,
        "detected_country": "Contact Number",
        "message": f"Accepted contact number ({phone_number}). Verbally confirm with caller.",
    }
