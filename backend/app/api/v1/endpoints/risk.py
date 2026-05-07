from fastapi import APIRouter

from app.agents.risk_analyst import risk_analyst_node
from app.agents.state import build_initial_state


router = APIRouter(
    prefix="/risk",
    tags=["Risk"],
)


@router.post("/assess/{supplier_id}")
async def assess_supplier_risk(
    supplier_id: str,
):
    """
    Run Risk Analyst Agent for a supplier.
    Uses mock signal data for MVP.
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

    result = await risk_analyst_node(state)

    return {
        "success": True,
        "supplier_id": supplier_id,
        "risk_assessment": result["risk_assessment"].model_dump(mode="json"),
        "anomaly_detection": result["anomaly_detection"].model_dump(mode="json"),
        "reasoning_summary": result["reasoning_summary"],
        "should_mitigate": result["should_mitigate"],
    }