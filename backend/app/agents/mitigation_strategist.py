from app.agents.state import AgentState
from app.llm.client import llm
from app.services.mitigation_service import mitigation_service


async def mitigation_strategist_node(state: AgentState) -> AgentState:
    """
    LangGraph node for Mitigation Strategist Agent.

    Responsibilities:
    - validate Risk Analyst output,
    - discover alternative suppliers,
    - simulate supplier switch scenarios,
    - rank alternatives using TOPSIS,
    - generate a mitigation plan,
    - mutate AgentState for Execution Agent.
    """

    if not state.get("should_mitigate"):
        return state

    risk_assessment = state.get("risk_assessment")

    if risk_assessment is None:
        return state

    supplier_id = state["current_supplier_id"]

    justification = await llm.ainvoke(
        f"Original supplier: {supplier_id} "
        f"(risk score: {risk_assessment.score}/100, level: {risk_assessment.level.value}).\n"
        "Generate a concise mitigation recommendation summary based only on ranked supplier simulation data. "
        "Do not invent supplier capabilities."
    )

    plan, candidates, scenarios, ranked = await mitigation_service.generate_mitigation_plan(
        supplier_id=supplier_id,
        risk_assessment=risk_assessment,
        justification=justification,
    )

    state["candidate_suppliers"] = candidates
    state["simulated_scenarios"] = scenarios
    state["mitigation_plan"] = plan
    state["ranked_scenarios"] = ranked

    state["should_execute"] = bool(plan.recommended_options)

    return state