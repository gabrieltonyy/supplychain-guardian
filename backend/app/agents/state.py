from app.schemas.assessments import (
    AnomalyDetection,
    RiskAssessment,
)
from app.schemas.execution import ExecutionRecord
from app.schemas.mitigation import (
    MitigationPlan,
    SimulatedScenario,
)


class AgentState(dict):
    """
    Shared LangGraph state passed between agents.

    This is the single source of truth for workflow orchestration.
    Each agent reads from and mutates this object.
    """

    # =====================================================
    # INPUT CONTEXT
    # =====================================================

    current_supplier_id: str

    # =====================================================
    # RISK ANALYST OUTPUTS
    # =====================================================

    risk_assessment: RiskAssessment | None

    anomaly_detection: AnomalyDetection | None

    reasoning_summary: str | None

    should_mitigate: bool

    # =====================================================
    # MITIGATION STRATEGIST OUTPUTS
    # =====================================================

    candidate_suppliers: list[dict]

    simulated_scenarios: list[SimulatedScenario]

    mitigation_plan: MitigationPlan | None

    should_execute: bool

    # =====================================================
    # EXECUTION AGENT OUTPUTS
    # =====================================================

    execution_record: ExecutionRecord | None

    should_audit: bool

    # =====================================================
    # SYSTEM / TRACEABILITY
    # =====================================================

    workflow_id: str | None

    correlation_id: str | None

    created_at: str | None


def build_initial_state(
    supplier_id: str,
    workflow_id: str | None = None,
) -> AgentState:
    """
    Create clean initial workflow state.
    """

    return AgentState(
        current_supplier_id=supplier_id,

        risk_assessment=None,
        anomaly_detection=None,
        reasoning_summary=None,
        should_mitigate=False,

        candidate_suppliers=[],
        simulated_scenarios=[],
        mitigation_plan=None,
        should_execute=False,

        execution_record=None,
        should_audit=False,

        workflow_id=workflow_id,
        correlation_id=None,
        created_at=None,
    )