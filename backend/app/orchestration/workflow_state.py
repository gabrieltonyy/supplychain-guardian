from typing import Any, TypedDict


class WorkflowState(TypedDict, total=False):
    """
    Shared LangGraph workflow state.

    This mirrors AgentState as a TypedDict because LangGraph
    works better with explicit typed dictionary state.
    """

    # Input context
    current_supplier_id: str
    supplier_region: str
    risk_score_history: list[float]

    # Risk Analyst outputs
    risk_assessment: Any
    anomaly_detection: Any
    reasoning_summary: str
    risk_signals: list[Any]
    should_mitigate: bool

    # Mitigation Strategist outputs
    candidate_suppliers: list[dict]
    simulated_scenarios: list[Any]
    ranked_scenarios: list[Any]
    mitigation_plan: Any
    should_execute: bool

    # Execution Agent outputs
    execution_record: Any
    should_audit: bool

    # Compliance Agent outputs
    audit_log_entry: Any
    compliance_verdict: Any
    workflow_complete: bool

    # Orchestration metadata
    workflow_id: str
    correlation_id: str | None
    current_node: str
    workflow_status: str
    retry_count: int
    error_message: str | None