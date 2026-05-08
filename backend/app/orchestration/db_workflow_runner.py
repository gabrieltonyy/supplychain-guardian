from uuid import uuid4

from app.agents.compliance_agent import compliance_agent_node
from app.agents.db_risk_analyst import db_risk_analyst_node
from app.agents.execution_agent import execution_agent_node
from app.agents.mitigation_strategist import mitigation_strategist_node
from app.agents.state import build_initial_state
from app.db.session import AsyncSessionLocal


async def run_db_supply_chain_workflow(
    supplier_id: str,
    supplier_region: str = "global",
) -> dict:
    """
    Run database-backed workflow.

    Current DB-backed part:
    - Risk Analyst uses PostgreSQL historical risk scores.
    """

    state = build_initial_state(supplier_id)

    state["supplier_region"] = supplier_region
    state["workflow_id"] = str(uuid4())
    state["correlation_id"] = str(uuid4())
    state["workflow_status"] = "running"

    async with AsyncSessionLocal() as session:
        state = await db_risk_analyst_node(
            state=state,
            session=session,
        )

    if not state.get("should_mitigate"):
        state["workflow_status"] = "completed_without_mitigation"
        state["workflow_complete"] = True
        return state

    state = await mitigation_strategist_node(state)

    if not state.get("should_execute"):
        state["workflow_status"] = "completed_without_execution"
        state["workflow_complete"] = True
        return state

    state = await execution_agent_node(state)

    if not state.get("should_audit"):
        state["workflow_status"] = "completed_without_audit"
        state["workflow_complete"] = True
        return state

    state = await compliance_agent_node(state)

    state["workflow_status"] = (
        "completed"
        if state.get("workflow_complete")
        else "completed_without_full_execution"
    )

    return state