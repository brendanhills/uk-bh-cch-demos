"""Unit tests for phone validator and country detection tool."""

import pytest
from app.cch_agent.tools.phone_validator import validate_phone_number


def test_validate_australian_mobile_success():
    """Verify valid Australian mobile numbers are accepted and formatted."""
    res = validate_phone_number("0458 477 029")
    assert res["is_valid"] is True
    assert res["formatted_number"] == "0458 477 029"
    assert res["detected_country"] == "Australia"


def test_validate_uk_number_acceptance_and_country_detection():
    """Verify UK international phone numbers (+44...) are accepted and detected as UK for verbal confirmation."""
    res = validate_phone_number("+447743414371")
    assert res["is_valid"] is True
    assert res["detected_country"] == "UK"
    assert "+44" in res["formatted_number"]
    assert "UK contact number" in res["message"]
