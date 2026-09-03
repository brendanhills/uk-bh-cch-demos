"""Dedicated Financial & Cost Estimation Tools for Cymbal Children's Hospital."""

from typing import Any, Dict


def calculate_home_care_financials(
    number_of_visits: int,
    base_rate_per_visit: float = 150.00,
    subsidy_type: str = None,
    subsidy_rate: float = 0.0,
) -> Dict[str, Any]:
    """Calculate base costs, subsidy discount amounts, and net total out-of-pocket costs for home care visits.

    Args:
        number_of_visits: Number of pediatric nurse visits.
        base_rate_per_visit: Base cost per visit in AUD. Defaults to 150.00.
        subsidy_type: Optional subsidy type (e.g., 'Medicare', 'NDIS', 'Hospital Assistance').
        subsidy_rate: Optional subsidy discount percentage as decimal (e.g. 0.15 for 15%).
    """
    if subsidy_type and subsidy_rate == 0.0:
        sub_lower = subsidy_type.lower()
        if "medicare" in sub_lower:
            subsidy_rate = 0.15
        elif "ndis" in sub_lower:
            subsidy_rate = 0.20
        elif "hospital" in sub_lower or "assistance" in sub_lower:
            subsidy_rate = 0.10
        else:
            subsidy_rate = 0.15

    total_base_cost = number_of_visits * base_rate_per_visit
    subsidy_discount = total_base_cost * subsidy_rate
    net_out_of_pocket = total_base_cost - subsidy_discount

    base_str = f"${total_base_cost:,.2f}".rstrip("0").rstrip(".")
    discount_str = f"${subsidy_discount:,.2f}".rstrip("0").rstrip(".")
    net_str = f"${net_out_of_pocket:,.2f}".rstrip("0").rstrip(".")

    if subsidy_type and subsidy_rate > 0:
        spoken_summary = (
            f"For {number_of_visits} visits, the base cost is {base_str}. "
            f"With your {int(subsidy_rate * 100)}% {subsidy_type} rebate, that saves you {discount_str}, "
            f"so you'd pay {net_str} in total."
        )
    else:
        spoken_summary = f"For {number_of_visits} visits, the total cost is {base_str}."

    return {
        "number_of_visits": number_of_visits,
        "base_rate_per_visit": base_rate_per_visit,
        "total_base_cost": total_base_cost,
        "subsidy_type": subsidy_type,
        "subsidy_rate": subsidy_rate,
        "subsidy_discount": subsidy_discount,
        "net_out_of_pocket": net_out_of_pocket,
        "spoken_summary": spoken_summary,
    }


def get_home_care_cost_estimate(
    number_of_visits: int, service_type: str = "Pediatric Nurse Visit"
) -> Dict[str, Any]:
    """Generate a cost estimate for specialized clinical nurse home care visits.

    Args:
        number_of_visits: The number of nurse home visits required.
        service_type: Type of home care service. Defaults to 'Pediatric Nurse Visit'.
    """
    return calculate_home_care_financials(
        number_of_visits=number_of_visits, base_rate_per_visit=150.00
    )


def approve_funding_subsidy(
    subsidy_type: str, requested_rate: float
) -> Dict[str, Any]:
    """Approve funding subsidy rate (NDIS, Medicare, Hospital Assistance).

    Note: Rates higher than 20% (0.20) require supervisor sign-off.

    Args:
        subsidy_type: Type of funding subsidy (e.g., 'NDIS', 'Medicare', 'Hospital Assistance').
        requested_rate: Decimal representation of the subsidy percentage (e.g., 0.15 for 15%).
    """
    if requested_rate > 0.20:
        return {
            "approved": False,
            "subsidy_type": subsidy_type,
            "requested_rate": requested_rate,
            "message": "Subsidy rate exceeds 20% (0.20). Clinical supervisor approval is required for this rate.",
        }

    return {
        "approved": True,
        "subsidy_type": subsidy_type,
        "approved_rate": requested_rate,
        "message": f"Successfully approved {subsidy_type} subsidy rate of {int(requested_rate * 100)}%.",
    }


def apply_subsidy_to_support_plan(
    subsidy_type: str,
    approved_rate: float,
    support_plan_id: str = "SP-CCH-9921",
) -> Dict[str, Any]:
    """Register and apply an approved funding subsidy rate onto the active support plan.

    Args:
        subsidy_type: Type of approved funding subsidy.
        approved_rate: The approved subsidy percentage (as a decimal).
        support_plan_id: The ID of the support plan. Defaults to 'SP-CCH-9921'.
    """
    return {
        "status": "Applied",
        "support_plan_id": support_plan_id,
        "subsidy_type": subsidy_type,
        "applied_rate": approved_rate,
        "confirmation_message": f"Registered {subsidy_type} subsidy at {int(approved_rate * 100)}% onto support plan {support_plan_id}.",
    }
