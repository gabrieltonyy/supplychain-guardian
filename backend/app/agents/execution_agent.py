from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentState
from app.llm.client import llm
from app.services.db_order_context_service import DbOrderContextService
from app.services.execution_service import execution_service


async def execution_agent_node(
    state: AgentState,
    session: AsyncSession | None = None,
) -> AgentState:
    """
    LangGraph node for Execution Agent.

    Responsibilities:
    - generate RFQs from mitigation plan,
    - prepare execution record,
    - keep execution pending human approval,
    - generate AMD-vLLM execution reasoning summary.
    """

    if not state.get("should_execute"):
        return state

    mitigation_plan = state.get("mitigation_plan")

    if mitigation_plan is None:
        return state

    active_order = state.get("active_order_context")

    if active_order is None and session is not None:
        order_service = DbOrderContextService(session)
        active_order = await order_service.get_active_order_context(
            supplier_id=mitigation_plan.original_supplier_id,
        )

    execution_record = await execution_service.generate_execution_record(
        mitigation_plan=mitigation_plan,
        candidate_suppliers=state.get(
            "candidate_suppliers",
            [],
        ),
        active_order=active_order,
    )

    execution_reasoning = await llm.ainvoke(
        f"Mitigation plan: {mitigation_plan.model_dump(mode='json')}\n"
        f"Execution record: {execution_record.model_dump(mode='json')}\n"
        f"Active order: {active_order}\n\n"
        "Write a concise execution summary in 2 sentences. "
        "Explain what RFQs were generated, why human approval is still required, "
        "and do not invent dispatch actions that have not happened."
    )

    state["active_order_context"] = active_order
    state["execution_record"] = execution_record
    state["execution_reasoning_summary"] = execution_reasoning
    state["execution_reasoning_source"] = getattr(
        llm,
        "last_provider_used",
        "unknown",
    )
    state["should_audit"] = True

    return state