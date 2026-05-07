from app.agents.state import AgentState
from app.llm.client import llm
from app.services.risk_service import risk_service


async def risk_analyst_node(state: AgentState) -> AgentState:
    """
    LangGraph node for Risk Analyst Agent.

    Responsibilities:
    - gather supplier risk signals,
    - compute risk score,
    - detect anomaly,
    - generate human-readable reasoning summary,
    - mutate AgentState for the next agent.
    """

    supplier_id = state["current_supplier_id"]

    region = state.get("supplier_region", "global")

    history = state.get("risk_score_history", [])

    assessment, anomaly, signals = await risk_service.assess_supplier_risk(
        supplier_id=supplier_id,
        region=region,
        history=history,
        use_mock_data=True,
    )

    reasoning = await llm.ainvoke(
        f"Supplier {supplier_id} risk score: "
        f"{assessment.score}/100 ({assessment.level.value}).\n"
        f"Factor breakdown: {assessment.factor_breakdown}.\n"
        f"Anomaly detected: {anomaly.model_dump(mode='json')}.\n"
        "In 2 sentences, explain the primary risk driver and recommended urgency. "
        "Do not hallucinate suppliers or suggest mitigations — only describe what the data shows."
    )

    state["risk_assessment"] = assessment
    state["anomaly_detection"] = anomaly
    state["reasoning_summary"] = reasoning
    state["risk_signals"] = signals

    state["should_mitigate"] = (
        assessment.level.value in {"HIGH", "CRITICAL"}
        or anomaly.is_anomaly
    )

    return state