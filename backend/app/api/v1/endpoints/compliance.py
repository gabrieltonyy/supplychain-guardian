from fastapi import APIRouter

from app.agents.compliance_agent import compliance_agent_node
from app.agents.execution_agent import execution_agent_node
from app.agents.mitigation_strategist import mitigation_strategist_node
from app.agents.risk_analyst import risk_analyst_node
from app.agents.state import build_initial_state


router = APIRouter(
    prefix="/compliance",
    tags=["Compliance"],
)


@router.post("/audit/{supplier_id}")
async def run_compliance_audit(
    supplier_id: str,
):
    """
    Run Risk Analyst → Mitigation Strategist → Execution Agent → Compliance Agent.
    Uses mock data for MVP.
    """

    state = build_initial_state(supplier_id)

    state["supplier_region"] = "global"
    state["workflow_id"] = f"MVP-WF-{supplier_id}"
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
    state = await compliance_agent_node(state)

    return {
        "success": True,
        "supplier_id": supplier_id,
        "risk_assessment": state["risk_assessment"].model_dump(mode="json"),
        "mitigation_plan": state["mitigation_plan"].model_dump(mode="json"),
        "execution_record": state["execution_record"].model_dump(mode="json"),
        "compliance_verdict": state["compliance_verdict"].value,
        "audit_log_entry": state["audit_log_entry"].model_dump(mode="json"),
        "workflow_complete": state["workflow_complete"],
    }