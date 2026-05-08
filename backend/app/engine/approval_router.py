from app.core.config import settings
from app.schemas.execution import ApprovalStatus, RFQDocument
from app.schemas.mitigation import MitigationPlan


def pre_execution_gate(
    mitigation_plan: MitigationPlan,
) -> dict:
    """
    Determine whether execution can be auto-approved
    or must route to human review.
    """

    issues: list[str] = []
    auto_eligible = True

    for option in mitigation_plan.recommended_options:
        if option.confidence < settings.AUTO_APPROVAL_MIN_CONFIDENCE:
            issues.append(
                f"Supplier {option.supplier_id}: confidence "
                f"{option.confidence:.0%} below threshold"
            )
            auto_eligible = False

        if option.residual_risk_score > settings.AUTO_APPROVAL_MAX_RESIDUAL_RISK:
            issues.append(
                f"Supplier {option.supplier_id}: residual risk "
                f"{option.residual_risk_score} exceeds auto-approval threshold"
            )
            auto_eligible = False

        if option.cost_delta_pct > settings.AUTO_APPROVAL_MAX_COST_DELTA:
            issues.append(
                f"Supplier {option.supplier_id}: cost delta "
                f"+{option.cost_delta_pct:.1f}% exceeds auto-approval threshold"
            )
            auto_eligible = False

        if option.onboarding_weeks > settings.AUTO_APPROVAL_MAX_ONBOARDING_WEEKS:
            issues.append(
                f"Supplier {option.supplier_id}: onboarding "
                f"{option.onboarding_weeks} weeks exceeds auto-approval threshold"
            )
            auto_eligible = False

    return {
        "auto_eligible": auto_eligible,
        "issues": issues,
        "gate_passed": True,
    }


async def route_approval(
    rfqs: list[RFQDocument],
    gate_result: dict,
    mitigation_plan: MitigationPlan,
) -> ApprovalStatus:
    """
    Route RFQs through auto-approval or human approval path.

    MVP behavior:
    - auto eligible => AUTO_APPROVED
    - otherwise => PENDING_HUMAN
    """

    _ = rfqs
    _ = mitigation_plan

    if gate_result["auto_eligible"]:
        return ApprovalStatus.AUTO_APPROVED

    return ApprovalStatus.PENDING_HUMAN