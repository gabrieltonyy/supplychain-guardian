from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentState
from app.services.db_mitigation_discovery_service import (
    DbMitigationDiscoveryService,
)
from app.services.db_order_context_service import DbOrderContextService
from app.services.mitigation_service import mitigation_service


async def mitigation_strategist_node(
    state: AgentState,
    session: AsyncSession | None = None,
) -> AgentState:
    risk_assessment = state.get("risk_assessment")
    reasoning_summary = state.get("reasoning_summary")

    if risk_assessment is None:
        state["should_execute"] = False
        return state

    candidate_suppliers = None
    at_risk_supplier = None
    active_order = None

    if session is not None:
        discovery_service = DbMitigationDiscoveryService(session)
        order_service = DbOrderContextService(session)

        at_risk_supplier = (
            await discovery_service.get_original_supplier_context(
                supplier_id=risk_assessment.supplier_id,
            )
        )

        if at_risk_supplier is None:
            raise ValueError(
                f"Original supplier not found in DB: "
                f"{risk_assessment.supplier_id}"
            )

        active_order = await order_service.get_active_order_context(
            supplier_id=risk_assessment.supplier_id,
        )

        if active_order is None:
            raise ValueError(
                f"No active order found in DB for supplier: "
                f"{risk_assessment.supplier_id}"
            )

        candidate_suppliers = await discovery_service.find_candidates(
            original_supplier_id=risk_assessment.supplier_id,
            required_capacity=active_order.get("volume_units", 30000),
            limit=10,
        )

        if not candidate_suppliers:
            state["original_supplier_context"] = at_risk_supplier
            state["active_order_context"] = active_order
            state["candidate_suppliers"] = []
            state["mitigation_plan"] = None
            state["simulated_scenarios"] = []
            state["ranked_scenarios"] = []
            state["should_execute"] = False
            return state

    mitigation_plan, candidates, scenarios, ranked = (
        await mitigation_service.generate_mitigation_plan(
            supplier_id=risk_assessment.supplier_id,
            risk_assessment=risk_assessment,
            justification=reasoning_summary
            or "Mitigation plan generated from current risk assessment.",
            candidate_suppliers=candidate_suppliers,
            at_risk_supplier=at_risk_supplier,
            active_order=active_order,
        )
    )

    state["original_supplier_context"] = at_risk_supplier
    state["active_order_context"] = active_order
    state["candidate_suppliers"] = candidates
    state["mitigation_plan"] = mitigation_plan
    state["simulated_scenarios"] = scenarios
    state["ranked_scenarios"] = ranked
    state["should_execute"] = bool(
        mitigation_plan
        and mitigation_plan.recommended_options
    )

    return state