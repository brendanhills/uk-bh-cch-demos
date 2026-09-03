"""End-to-end simulation tests verifying the complete demo pipeline and tool execution."""

import pytest
from app.cch_agent.tools import (
    validate_phone_number,
    record_patient_identity,
    calculate_home_care_financials,
    approve_funding_subsidy,
    get_available_support_times,
    schedule_home_care_visit,
    update_hospital_emr,
)


def test_e2e_demo_flow():
    """Verify end-to-end demo flow tools execute correctly in sequence."""
    
    # Step 1: Phone & Identity Verification
    phone_res = validate_phone_number("0458477029")
    assert phone_res["is_valid"] is True
    assert phone_res["formatted_number"] == "0458 477 029"

    identity_res = record_patient_identity(caller_name="Brendan", phone_number="0458477029")
    assert identity_res["status"] == "Saved to Global Session Memory"
    assert identity_res["phone_number"] == "0458477029"

    # Step 2: Financial Calculation & Rebate
    medicare_res = calculate_home_care_financials(number_of_visits=1, subsidy_type="Medicare")
    assert medicare_res["total_base_cost"] == 150.00
    assert medicare_res["subsidy_rate"] == 0.15
    assert medicare_res["subsidy_discount"] == 22.50
    assert medicare_res["net_out_of_pocket"] == 127.50

    ndis_res = calculate_home_care_financials(number_of_visits=2, subsidy_type="NDIS")
    assert ndis_res["total_base_cost"] == 300.00
    assert ndis_res["subsidy_rate"] == 0.20
    assert ndis_res["subsidy_discount"] == 60.00
    assert ndis_res["net_out_of_pocket"] == 240.00

    # Step 3: Nurse Availability & Booking
    slots = get_available_support_times()
    assert isinstance(slots, dict)
    assert "available_slots" in slots

    booking = schedule_home_care_visit(
        date="2026-09-03",
        time="10:00 AM",
        child_name="Leo Marlow",
        parent_name="Brendan",
    )
    assert booking["booking_status"] == "Confirmed"
    assert booking["booking_id"] == "BK-CCH-2026-881"

    # Step 4: Hospital EMR Update
    emr_res = update_hospital_emr(child_name="Leo Marlow", clinical_notes="Home care nurse visit booked and verified.")
    assert emr_res["emr_update_status"] == "Success"
