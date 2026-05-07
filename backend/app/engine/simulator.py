from app.schemas.assessments import RiskAssessment
from app.schemas.mitigation import SimulatedScenario


def estimate_freight_delta(
    origin: str,
    destination: str,
    volume: int,
) -> float:
    """
    Simple MVP freight cost adjustment.

    Later this can use logistics APIs, lane pricing,
    port congestion data, or distance calculations.
    """

    if origin.lower() == destination.lower():
        return 0.0

    if volume >= 50000:
        return 4.0

    if volume >= 10000:
        return 6.5

    return 9.0


def simulate_switch(
    at_risk_supplier: dict,
    candidate: dict,
    current_order: dict,
    risk_assessment: RiskAssessment,
) -> SimulatedScenario:
    """
    Simulate the cost, lead-time, and residual-risk impact
    of switching from the at-risk supplier to a candidate supplier.
    """

    _ = risk_assessment

    current_unit_cost = at_risk_supplier["unit_cost"]
    candidate_unit_cost = candidate["unit_cost"]

    unit_cost_delta_pct = (
        (candidate_unit_cost - current_unit_cost)
        / current_unit_cost
    ) * 100

    freight_delta_pct = estimate_freight_delta(
        origin=candidate["country"],
        destination=current_order["destination_country"],
        volume=current_order["volume_units"],
    )

    total_cost_delta_pct = unit_cost_delta_pct + freight_delta_pct

    lead_time_delta_days = (
        candidate["typical_lead_time_days"]
        - at_risk_supplier["typical_lead_time_days"]
    )

    residual_risk_score = candidate.get("latest_risk_score", 30.0)

    relationship_status = candidate.get("relationship_status", "new")

    if relationship_status == "new":
        onboarding_weeks = 4
    elif relationship_status == "dormant":
        onboarding_weeks = 2
    else:
        onboarding_weeks = 0

    data_completeness = sum(
        [
            candidate.get("unit_cost") is not None,
            candidate.get("typical_lead_time_days") is not None,
            candidate.get("latest_risk_score") is not None,
            candidate.get("capacity_units_per_month") is not None,
        ]
    ) / 4.0

    return SimulatedScenario(
        supplier_id=candidate["id"],
        supplier_name=candidate["name"],
        cost_delta_pct=round(total_cost_delta_pct, 1),
        lead_time_delta_days=lead_time_delta_days,
        residual_risk_score=residual_risk_score,
        onboarding_weeks=onboarding_weeks,
        confidence=data_completeness,
        breakdown={
            "unit_cost_delta_pct": round(unit_cost_delta_pct, 1),
            "freight_delta_pct": round(freight_delta_pct, 1),
            "candidate_country": candidate["country"],
        },
    )