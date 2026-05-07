from fastapi import APIRouter

from app.agents.mitigation_strategist import mitigation_strategist_node
from app.agents.risk_analyst import risk_analyst_node
from app.agents.state import build_initial_state


router = APIRouter(
    prefix="/mitigation",
    tags=["Mitigation"],
)


@router.post("/plan/{supplier_id}")
async def create_mitigation_plan(
    supplier_id: str,
):
    """
    Run Risk Analyst + Mitigation Strategist for a supplier.
    Uses mock data for MVP.
    """

    state = build_initial_state(supplier_id)

    state["supplier_region"] = "global"
    state["risk_score_history"] = [
        20,
        21,
        19,
        22,
        20,
        21,
        20,
        19,
        22,
        21,
    ]

    state = await risk_analyst_node(state)
    state = await mitigation_strategist_node(state)

    return {
        "success": True,
        "supplier_id": supplier_id,
        "risk_assessment": state["risk_assessment"].model_dump(mode="json"),
        "anomaly_detection": state["anomaly_detection"].model_dump(mode="json"),
        "candidate_suppliers": state["candidate_suppliers"],
        "simulated_scenarios": [
            scenario.model_dump(mode="json")
            for scenario in state["simulated_scenarios"]
        ],
        "mitigation_plan": state["mitigation_plan"].model_dump(mode="json"),
        "should_execute": state["should_execute"],
    }