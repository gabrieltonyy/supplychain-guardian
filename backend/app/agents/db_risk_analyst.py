from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentState
from app.llm.client import llm
from app.services.db_risk_service import DbRiskService


async def db_risk_analyst_node(
    state: AgentState,
    session: AsyncSession,
) -> AgentState:
    """
    Database-backed Risk Analyst node.

    Uses:
    - live external supplier signals
    - PostgreSQL historical risk scores
    - DB-backed anomaly detection
    - AMD-first LLM reasoning with local fallback
    """

    supplier_id = state["current_supplier_id"]
    region = state.get("supplier_region", "global")

    risk_service = DbRiskService(session)

    assessment, anomaly, signals = await risk_service.assess_supplier_risk(
        supplier_id=supplier_id,
        region=region,
    )

    signal_summary = [
        {
            "type": (
                signal.signal_type.value
                if hasattr(signal.signal_type, "value")
                else str(signal.signal_type)
            ),
            "source": signal.source,
            "severity": signal.severity,
            "confidence": signal.confidence,
            "region": signal.region,
        }
        for signal in signals
    ]

    reasoning = await llm.ainvoke(
        f"Supplier: {supplier_id}\n"
        f"Risk score: {assessment.score}/100\n"
        f"Risk level: {assessment.level.value}\n"
        f"Factor breakdown: {assessment.factor_breakdown}\n"
        f"Contributing signals: {assessment.contributing_signals}\n"
        f"Signal summary: {signal_summary}\n"
        f"Anomaly: {anomaly.model_dump(mode='json')}\n\n"
        "Write a concise operational risk explanation in 2 sentences. "
        "Mention the strongest live signal sources. "
        "State whether mitigation is needed. "
        "Do not invent suppliers or unsupported facts."
    )

    state["risk_assessment"] = assessment
    state["anomaly_detection"] = anomaly
    state["reasoning_summary"] = reasoning
    state["ai_reasoning_source"] = getattr(
        llm,
        "last_provider_used",
        "unknown",
    )
    state["risk_signals"] = signals

    state["should_mitigate"] = (
        assessment.level.value in {"HIGH", "CRITICAL"}
        or (
            anomaly.is_anomaly
            and anomaly.direction == "spike"
        )
    )

    return state