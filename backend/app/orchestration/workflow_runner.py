from uuid import uuid4

from app.orchestration.supply_chain_graph import supply_chain_graph
from app.orchestration.workflow_state import WorkflowState


async def run_supply_chain_workflow(
    supplier_id: str,
    supplier_region: str = "global",
    risk_score_history: list[float] | None = None,
) -> WorkflowState:
    """
    Run full SupplyChain Guardian workflow using LangGraph.

    Flow:
    Risk Analyst → Mitigation Strategist → Execution Agent → Compliance Agent
    """

    initial_state: WorkflowState = {
        "current_supplier_id": supplier_id,
        "supplier_region": supplier_region,
        "risk_score_history": risk_score_history or [],
        "workflow_id": str(uuid4()),
        "correlation_id": str(uuid4()),
        "workflow_status": "running",
        "retry_count": 0,
        "error_message": None,
    }

    final_state = await supply_chain_graph.ainvoke(initial_state)

    final_state["workflow_status"] = (
        "completed"
        if final_state.get("workflow_complete")
        else "completed_without_full_execution"
    )

    return final_state