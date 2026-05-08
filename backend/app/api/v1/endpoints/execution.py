from fastapi import APIRouter

from app.agents.execution_agent import execution_agent_node
from app.agents.mitigation_strategist import mitigation_strategist_node
from app.agents.risk_analyst import risk_analyst_node
from app.agents.state import build_initial_state


router = APIRouter(
    prefix="/execution",
    tags=["Execution"],
)


@router.post("/run/{supplier_id}")
async def run_execution_workflow(
    supplier_id: str,
):
    """
    Run Risk Analyst → Mitigation Strategist → Execution Agent.
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
    state = await execution_agent_node(state)

    return {
        "success": True,
        "supplier_id": supplier_id,
        "risk_assessment": state["risk_assessment"].model_dump(mode="json"),
        "mitigation_plan": state["mitigation_plan"].model_dump(mode="json"),
        "execution_record": state["execution_record"].model_dump(mode="json"),
        "should_audit": state["should_audit"],
    }