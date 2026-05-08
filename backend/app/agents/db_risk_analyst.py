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
    - seeded supplier signals
    - PostgreSQL historical risk scores
    - DB-backed anomaly detection
    """

    supplier_id = state["current_supplier_id"]
    region = state.get("supplier_region", "global")

    risk_service = DbRiskService(session)

    assessment, anomaly, signals = await risk_service.assess_supplier_risk(
        supplier_id=supplier_id,
        region=region,
    )

    reasoning = await llm.ainvoke(
        f"Supplier {supplier_id} risk score: "
        f"{assessment.score}/100 ({assessment.level.value}).\n"
        f"Factor breakdown: {assessment.factor_breakdown}.\n"
        f"Anomaly detected: {anomaly.model_dump(mode='json')}.\n"
        "In 2 sentences, explain the primary risk driver and recommended urgency. "
        "Do not hallucinate suppliers or suggest mitigations."
    )

    state["risk_assessment"] = assessment
    state["anomaly_detection"] = anomaly
    state["reasoning_summary"] = reasoning
    state["risk_signals"] = signals

    state["should_mitigate"] = (
        assessment.level.value in {"HIGH", "CRITICAL"}
        or (
            anomaly.is_anomaly
            and anomaly.direction == "spike"
        )
    )

    return state