from app.agents.state import AgentState
from app.services.compliance_service import compliance_service


async def compliance_agent_node(state: AgentState) -> AgentState:
    """
    LangGraph node for Compliance Agent.

    Responsibilities:
    - validate Execution Agent output,
    - screen suppliers,
    - run regulatory checks,
    - compute compliance verdict,
    - generate immutable audit payload,
    - mutate AgentState with final compliance result.
    """

    if not state.get("should_audit"):
        return state

    execution_record = state.get("execution_record")
    mitigation_plan = state.get("mitigation_plan")

    if execution_record is None or mitigation_plan is None:
        return state

    audit_entry = await compliance_service.generate_audit_log(
        execution_record=execution_record,
        mitigation_plan=mitigation_plan,
        workflow_run_id=state.get("workflow_id") or "MVP-WORKFLOW",
    )

    state["audit_log_entry"] = audit_entry
    state["compliance_verdict"] = audit_entry.verdict
    state["workflow_complete"] = True

    return state