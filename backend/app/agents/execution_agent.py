from app.agents.state import AgentState
from app.services.execution_service import execution_service


async def execution_agent_node(state: AgentState) -> AgentState:
    """
    LangGraph node for Execution Agent.

    Responsibilities:
    - validate Mitigation Strategist output,
    - generate RFQs,
    - route approval,
    - simulate dispatch where eligible,
    - write ExecutionRecord into AgentState.
    """

    if not state.get("should_execute"):
        return state

    mitigation_plan = state.get("mitigation_plan")

    if mitigation_plan is None:
        return state

    execution_record = await execution_service.generate_execution_record(
        mitigation_plan=mitigation_plan,
    )

    state["execution_record"] = execution_record
    state["should_audit"] = True

    return state