from uuid import uuid4

from app.agents.compliance_agent import compliance_agent_node
from app.agents.db_risk_analyst import db_risk_analyst_node
from app.agents.execution_agent import execution_agent_node
from app.agents.mitigation_strategist import mitigation_strategist_node
from app.agents.state import build_initial_state
from app.db.session import AsyncSessionLocal
from app.services.workflow_persistence_service import (
    WorkflowPersistenceService,
)


async def run_db_supply_chain_workflow(
    supplier_id: str,
    supplier_region: str = "global",
) -> dict:
    """
    Run database-backed workflow.

    Current DB-backed part:
    - Risk Analyst uses PostgreSQL historical risk scores.
    """

    state = build_initial_state(supplier_id)

    state["supplier_region"] = supplier_region
    state["workflow_id"] = str(uuid4())
    state["correlation_id"] = str(uuid4())
    state["workflow_status"] = "running"

    async with AsyncSessionLocal() as session:
        persistence_service = WorkflowPersistenceService(session)
        await persistence_service.start_workflow(
            supplier_id=supplier_id,
            workflow_id=state["workflow_id"],
            correlation_id=state["correlation_id"],
        )

    await _log_workflow_event(
        state=state,
        event_type="workflow_started",
        status="success",
        message="Workflow execution started",
    )

    try:
        async with AsyncSessionLocal() as session:
            state = await db_risk_analyst_node(
                state=state,
                session=session,
            )

            persistence_service = WorkflowPersistenceService(session)
            await persistence_service.persist_risk_output(
                workflow_id=state["workflow_id"],
                assessment=state["risk_assessment"],
                anomaly_detection=state["anomaly_detection"],
                reasoning_summary=state.get("reasoning_summary"),
            )

        await _log_workflow_event(
            state=state,
            event_type="risk_assessment_completed",
            status="success",
            agent_name="db_risk_analyst",
            message="Risk assessment completed",
            payload={
                "risk_level": state["risk_assessment"].level,
                "risk_score": state["risk_assessment"].score,
                "should_mitigate": state.get("should_mitigate"),
                "anomaly_detection": state.get("anomaly_detection"),
            },
        )

        if not state.get("should_mitigate"):
            state["workflow_status"] = "completed_without_mitigation"
            state["workflow_complete"] = True

            await _log_workflow_event(
                state=state,
                event_type="mitigation_skipped",
                status="success",
                agent_name="mitigation_strategist",
                message="Mitigation skipped because risk did not require action",
                payload={
                    "workflow_status": state["workflow_status"],
                    "risk_level": state["risk_assessment"].level,
                    "should_mitigate": state.get("should_mitigate"),
                },
            )

            await _complete_persisted_workflow(state)
            return state

        async with AsyncSessionLocal() as session:
            state = await mitigation_strategist_node(
                state=state,
                session=session,
            )

        if state.get("mitigation_plan") is not None:
            async with AsyncSessionLocal() as session:
                persistence_service = WorkflowPersistenceService(session)
                persisted_plan = (
                    await persistence_service.persist_mitigation_output(
                        workflow_id=state["workflow_id"],
                        mitigation_plan=state["mitigation_plan"],
                        candidate_suppliers=state.get(
                            "candidate_suppliers",
                            [],
                        ),
                        simulated_scenarios=state.get(
                            "simulated_scenarios",
                            [],
                        ),
                    )
                )

                state["mitigation_plan"].id = persisted_plan.id

            await _log_workflow_event(
                state=state,
                event_type="mitigation_generated",
                status="success",
                agent_name="mitigation_strategist",
                message="Mitigation plan generated",
                payload={
                    "mitigation_plan_id": state["mitigation_plan"].id,
                    "recommended_options": len(
                        state["mitigation_plan"].recommended_options
                    ),
                    "should_execute": state.get("should_execute"),
                },
            )

        if not state.get("should_execute"):
            state["workflow_status"] = "completed_without_execution"
            state["workflow_complete"] = True

            await _log_workflow_event(
                state=state,
                event_type="execution_skipped",
                status="success",
                agent_name="execution_agent",
                message="Execution skipped because no executable mitigation was selected",
                payload={
                    "workflow_status": state["workflow_status"],
                    "should_execute": state.get("should_execute"),
                },
            )

            await _complete_persisted_workflow(state)
            return state

        async with AsyncSessionLocal() as session:
            state = await execution_agent_node(
                state=state,
                session=session,
            )

        if state.get("execution_record") is not None:
            async with AsyncSessionLocal() as session:
                persistence_service = WorkflowPersistenceService(session)
                await persistence_service.persist_execution_output(
                    workflow_id=state["workflow_id"],
                    execution_record=state["execution_record"],
                )

            await _log_workflow_event(
                state=state,
                event_type="execution_completed",
                status="success",
                agent_name="execution_agent",
                message="Execution workflow completed",
                payload={
                    "execution_id": state["execution_record"].execution_id,
                    "mitigation_plan_id": (
                        state["execution_record"].mitigation_plan_id
                    ),
                    "approval_status": (
                        state["execution_record"].approval_status
                    ),
                    "rfq_count": len(state["execution_record"].rfqs),
                },
            )

        if not state.get("should_audit"):
            state["workflow_status"] = "completed_without_audit"
            state["workflow_complete"] = True

            await _log_workflow_event(
                state=state,
                event_type="compliance_skipped",
                status="success",
                agent_name="compliance_agent",
                message="Compliance skipped because audit was not required",
                payload={
                    "workflow_status": state["workflow_status"],
                    "should_audit": state.get("should_audit"),
                },
            )

            await _complete_persisted_workflow(state)
            return state

        state = await compliance_agent_node(state)

        if state.get("audit_log_entry") is not None:
            async with AsyncSessionLocal() as session:
                persistence_service = WorkflowPersistenceService(session)

                await persistence_service.persist_compliance_output(
                    workflow_id=state["workflow_id"],
                    audit_log_entry=state["audit_log_entry"],
                )

            await _log_workflow_event(
                state=state,
                event_type="compliance_completed",
                status="success",
                agent_name="compliance_agent",
                message="Compliance audit completed",
                payload={
                    "log_id": state["audit_log_entry"].log_id,
                    "execution_record_id": (
                        state["audit_log_entry"].execution_record_id
                    ),
                    "verdict": state.get("compliance_verdict"),
                },
            )

        state["workflow_status"] = (
            "completed"
            if state.get("workflow_complete")
            else "completed_without_audit"
        )

        await _complete_persisted_workflow(state)

        await _log_workflow_event(
            state=state,
            event_type="workflow_completed",
            status="success",
            message="Workflow execution completed",
            payload={
                "workflow_status": state["workflow_status"],
                "workflow_complete": state.get("workflow_complete"),
            },
        )

        return state

    except Exception as exc:
        state["workflow_status"] = "failed"
        state["error_message"] = str(exc)

        async with AsyncSessionLocal() as session:
            persistence_service = WorkflowPersistenceService(session)
            await persistence_service.fail_workflow(
                workflow_id=state["workflow_id"],
                error_message=str(exc),
                final_state_snapshot=state,
            )

        await _log_workflow_event(
            state=state,
            event_type="workflow_failed",
            status="failed",
            message="Workflow execution failed",
            error_message=str(exc),
        )

        raise


async def _log_workflow_event(
    state: dict,
    event_type: str,
    status: str,
    agent_name: str | None = None,
    message: str | None = None,
    payload: dict | None = None,
    error_message: str | None = None,
) -> None:
    async with AsyncSessionLocal() as session:
        persistence_service = WorkflowPersistenceService(session)

        await persistence_service.log_event(
            workflow_id=state["workflow_id"],
            supplier_id=state["current_supplier_id"],
            event_type=event_type,
            status=status,
            agent_name=agent_name,
            message=message,
            payload=payload,
            error_message=error_message,
        )


async def _complete_persisted_workflow(
    state: dict,
) -> None:
    async with AsyncSessionLocal() as session:
        persistence_service = WorkflowPersistenceService(session)
        await persistence_service.complete_workflow(
            workflow_id=state["workflow_id"],
            workflow_status=state["workflow_status"],
            final_state_snapshot=state,
        )