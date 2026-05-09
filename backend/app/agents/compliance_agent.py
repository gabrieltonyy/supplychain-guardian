from app.agents.state import AgentState
from app.llm.client import llm
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
    - generate AMD-vLLM compliance reasoning summary,
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

    compliance_reasoning = await llm.ainvoke(
        f"Compliance verdict: {audit_entry.verdict.value}\n"
        f"Verdict rationale: {audit_entry.verdict_rationale}\n"
        f"Execution record: "
        f"{execution_record.model_dump(mode='json')}\n"
        f"Mitigation plan: "
        f"{mitigation_plan.model_dump(mode='json')}\n"
        f"Sanctions results: {audit_entry.sanctions_results}\n"
        f"Regulatory results: {audit_entry.regulatory_results}\n\n"
        "Write a concise compliance audit summary in 2 sentences. "
        "Mention whether the workflow is cleared or flagged. "
        "Mention human approval status if relevant. "
        "Do not invent regulations or unsupported findings."
    )

    audit_entry.llm_summary = compliance_reasoning

    state["audit_log_entry"] = audit_entry
    state["compliance_verdict"] = audit_entry.verdict
    state["compliance_reasoning_summary"] = compliance_reasoning
    state["compliance_reasoning_source"] = getattr(
        llm,
        "last_provider_used",
        "unknown",
    )
    state["workflow_complete"] = True

    return state