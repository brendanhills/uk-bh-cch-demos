"""Unit tests for phone validator and global country detection tool."""

import pytest
from app.cch_agent.tools.phone_validator import validate_phone_number


def test_validate_australian_mobile_success():
    """Verify valid Australian mobile numbers are accepted and formatted."""
    res = validate_phone_number("0458 477 029")
    assert res["is_valid"] is True
    assert res["formatted_number"] == "0458 477 029"
    assert res["detected_country"] == "Australia"
    assert res["is_international"] is False


def test_validate_global_international_numbers():
    """Verify ANY global international phone number (+44 UK, +1 US, +64 NZ, +65 SG) is accepted and detected for verbal country confirmation."""
    test_cases = [
        ("+447743414371", "United Kingdom"),
        ("+12025550143", "United States or Canada"),
        ("+6421345678", "New Zealand"),
        ("+6591234567", "Singapore"),
    ]

    for num, expected_country in test_cases:
        res = validate_phone_number(num)
        assert res["is_valid"] is True
        assert res["detected_country"] == expected_country
        assert res["is_international"] is True
        assert expected_country in res["message"]
