"""Unit tests for Australian phone validator tool."""

import pytest
from app.cch_agent.tools.phone_validator import validate_australian_phone_number


def test_validate_australian_mobile_success():
    """Verify valid Australian mobile numbers are accepted and formatted."""
    res = validate_australian_phone_number("0458 477 029")
    assert res["is_valid_australian"] is True
    assert res["formatted_number"] == "0458 477 029"
    assert res["detected_country"] == "Australia"


def test_validate_australian_mobile_intl_prefix():
    """Verify Australian mobile numbers with +61 prefix are normalized and accepted."""
    res = validate_australian_phone_number("+61 458 477 029")
    assert res["is_valid_australian"] is True
    assert res["formatted_number"] == "0458 477 029"


def test_validate_uk_number_rejection():
    """Verify UK international phone numbers (+44...) are identified and rejected with Australian requirement guidance."""
    res = validate_australian_phone_number("+447743414371")
    assert res["is_valid_australian"] is False
    assert res["detected_country"] == "United Kingdom (+44)"
    assert "Australia" in res["message"]
