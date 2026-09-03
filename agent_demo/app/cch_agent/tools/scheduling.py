"""Domain scheduling and EMR tools for Cymbal Children's Hospital."""

from typing import Any, Dict, List


from datetime import datetime, timedelta


def get_available_support_times(
    requested_date: str = None, service_type: str = "Pediatric Nurse Visit"
) -> Dict[str, Any]:
    """Look up available clinical home care appointment slots for a specified future date.

    Args:
        requested_date: The requested appointment date (must be at least 1 day after today, e.g. 'tomorrow', 'Friday', '2026-09-03').
        service_type: Type of home care service. Defaults to 'Pediatric Nurse Visit'.
    """
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%A, %d %B %Y")
    day_after = datetime.now() + timedelta(days=2)
    day_after_str = day_after.strftime("%A, %d %B %Y")

    date_to_use = requested_date if requested_date and requested_date.strip() else f"Tomorrow ({tomorrow_str})"

    return {
        "requested_date": date_to_use,
        "earliest_allowed_date": tomorrow_str,
        "suggested_dates": [tomorrow_str, day_after_str],
        "service_type": service_type,
        "available_slots": [
            {
                "time": "09:00 AM",
                "practitioner": "Nurse Sarah",
                "status": "Available",
            },
            {
                "time": "11:30 AM",
                "practitioner": "Nurse Michael",
                "status": "Available",
            },
            {
                "time": "02:00 PM",
                "practitioner": "Nurse Sarah",
                "status": "Available",
            },
            {
                "time": "04:30 PM",
                "practitioner": "Nurse Michael",
                "status": "Available",
            },
        ],
        "notes": f"All appointments are scheduled at least 1 day in advance ({tomorrow_str} onwards) and include pediatric vital signs assessment and medication review.",
    }


def schedule_home_care_visit(
    date: str,
    time: str,
    child_name: str,
    parent_name: str,
    service_type: str = "Pediatric Nurse Visit",
    practitioner: str = None,
) -> Dict[str, Any]:
    """Schedule and confirm a specialized pediatric nurse home visit.

    Args:
        date: The confirmed date for the visit.
        time: The confirmed time for the visit (e.g. '09:00 AM', '2:00 PM').
        child_name: Name of the child/patient receiving care.
        parent_name: Name of the parent/carer confirming the booking.
        service_type: Type of home care service. Defaults to 'Pediatric Nurse Visit'.
        practitioner: Optional specific nurse requested (e.g. 'Nurse Sarah').
    """
    assigned_nurse = practitioner if practitioner else "Nurse Sarah"
    return {
        "booking_status": "Confirmed",
        "booking_id": "BK-CCH-2026-881",
        "child_name": child_name,
        "parent_name": parent_name,
        "service_type": service_type,
        "date": date,
        "time": time,
        "assigned_practitioner": assigned_nurse,
        "confirmation_message": f"Successfully booked {service_type} with {assigned_nurse} for {child_name} on {date} at {time}.",
    }


def update_hospital_emr(
    child_name: str,
    booked_visits: List[str] = None,
    approved_subsidies: List[str] = None,
    clinical_notes: str = None,
) -> Dict[str, Any]:
    """Update and persist clinical records, booked visits, and approved subsidies into the Hospital EMR system.

    Args:
        child_name: Name of the child patient.
        booked_visits: List of confirmed home care visits.
        approved_subsidies: List of approved funding subsidies.
        clinical_notes: Summary of clinical assessment notes.
    """
    return {
        "emr_update_status": "Success",
        "child_name": child_name,
        "patient_id": "P-CCH-883012",
        "vitals_logged": True,
        "booked_visits": booked_visits,
        "approved_subsidies": approved_subsidies,
        "clinical_notes_saved": clinical_notes,
        "timestamp": "2026-07-21T12:45:13Z",
    }
