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

    current_supplier_id: str

    risk_assessment: RiskAssessment | None
    anomaly_detection: AnomalyDetection | None
    reasoning_summary: str | None
    ai_reasoning_source: str | None
    should_mitigate: bool

    candidate_suppliers: list[dict]
    simulated_scenarios: list[SimulatedScenario]
    mitigation_plan: MitigationPlan | None
    mitigation_reasoning_summary: str | None
    mitigation_reasoning_source: str | None
    should_execute: bool

    execution_record: ExecutionRecord | None
    execution_reasoning_summary: str | None
    execution_reasoning_source: str | None
    should_audit: bool

    audit_log_entry: object | None
    compliance_verdict: object | None
    compliance_reasoning_summary: str | None
    compliance_reasoning_source: str | None
    workflow_complete: bool

    workflow_id: str | None
    correlation_id: str | None
    created_at: str | None


def build_initial_state(
    supplier_id: str,
    workflow_id: str | None = None,
) -> AgentState:
    return AgentState(
        current_supplier_id=supplier_id,

        risk_assessment=None,
        anomaly_detection=None,
        reasoning_summary=None,
        ai_reasoning_source=None,
        should_mitigate=False,

        candidate_suppliers=[],
        simulated_scenarios=[],
        mitigation_plan=None,
        mitigation_reasoning_summary=None,
        mitigation_reasoning_source=None,
        should_execute=False,

        execution_record=None,
        execution_reasoning_summary=None,
        execution_reasoning_source=None,
        should_audit=False,

        audit_log_entry=None,
        compliance_verdict=None,
        compliance_reasoning_summary=None,
        compliance_reasoning_source=None,
        workflow_complete=False,

        workflow_id=workflow_id,
        correlation_id=None,
        created_at=None,
    )