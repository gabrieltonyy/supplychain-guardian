from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.execution_repository import ExecutionRepository
from app.db.repositories.mitigation_repository import MitigationRepository
from app.db.repositories.risk_repository import RiskRepository
from app.db.repositories.compliance_repository import ComplianceRepository
from app.db.repositories.workflow_event_repository import WorkflowEventRepository
from app.db.repositories.workflow_run_repository import (
    WorkflowRunRepository,
)


TERMINAL_WORKFLOW_STATUSES = {
    "completed",
    "completed_without_mitigation",
    "completed_without_execution",
    "completed_without_audit",
    "failed",
}


class WorkflowPersistenceService:
    """
    Coordinates durable workflow-run persistence.
    """

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session
        self.repository = WorkflowRunRepository(session)
        self.risk_repository = RiskRepository(session)
        self.mitigation_repository = MitigationRepository(session)
        self.execution_repository = ExecutionRepository(session)
        self.compliance_repository = ComplianceRepository(session)
        self.event_repository = WorkflowEventRepository(session)

    async def start_workflow(
        self,
        supplier_id: str,
        workflow_id: str,
        correlation_id: str | None = None,
    ):
        record = await self.repository.start_or_update(
            supplier_id=supplier_id,
            workflow_id=workflow_id,
            correlation_id=correlation_id,
        )

        await self.session.commit()

        return record

    async def persist_risk_output(
        self,
        workflow_id: str,
        assessment,
        anomaly_detection,
        reasoning_summary: str | None = None,
    ):
        record = await self.risk_repository.save_assessment(
            assessment=assessment,
            anomaly_data=self._to_json_safe(anomaly_detection),
            reasoning_summary=reasoning_summary,
            workflow_id=workflow_id,
        )

        await self.session.commit()

        return record

    async def persist_mitigation_output(
        self,
        workflow_id: str,
        mitigation_plan,
        candidate_suppliers: list[dict],
        simulated_scenarios: list,
    ):
        record = await self.mitigation_repository.save_plan(
            plan=mitigation_plan,
            candidate_suppliers=self._to_json_safe(candidate_suppliers),
            simulated_scenarios=self._to_json_safe(simulated_scenarios),
            workflow_id=workflow_id,
        )

        await self.session.commit()

        return record

    async def persist_execution_output(
        self,
        workflow_id: str,
        execution_record,
    ):
        await self.execution_repository.save_rfqs(
            rfqs=execution_record.rfqs,
            mitigation_plan_id=execution_record.mitigation_plan_id,
            workflow_id=workflow_id,
        )

        record = await self.execution_repository.save_execution_record(
            execution_record=execution_record,
            workflow_id=workflow_id,
        )

        await self.session.commit()

        return record

    async def persist_compliance_output(
        self,
        workflow_id: str,
        audit_log_entry,
    ):
        record = await self.compliance_repository.save_audit_log(
            audit_entry=audit_log_entry,
            workflow_id=workflow_id,
        )

        await self.session.commit()

        return record

    async def complete_workflow(
        self,
        workflow_id: str,
        workflow_status: str,
        final_state_snapshot: dict | None = None,
    ):
        self._validate_terminal_status(workflow_status)

        record = await self.repository.complete(
            workflow_id=workflow_id,
            workflow_status=workflow_status,
            final_state_snapshot=self._to_json_safe(
                final_state_snapshot
            ),
        )

        await self.session.commit()

        return record

    async def log_event(
        self,
        workflow_id: str,
        supplier_id: str,
        event_type: str,
        status: str,
        agent_name: str | None = None,
        message: str | None = None,
        payload: dict | None = None,
        error_message: str | None = None,
    ):
        record = await self.event_repository.create(
            workflow_id=workflow_id,
            supplier_id=supplier_id,
            event_type=event_type,
            agent_name=agent_name,
            status=status,
            message=message,
            payload=self._to_json_safe(payload),
            error_message=error_message,
        )

        await self.session.commit()

        return record

    async def fail_workflow(
        self,
        workflow_id: str,
        error_message: str,
        final_state_snapshot: dict | None = None,
    ):
        record = await self.repository.fail(
            workflow_id=workflow_id,
            error_message=error_message,
            final_state_snapshot=self._to_json_safe(
                final_state_snapshot
            ),
        )

        await self.session.commit()

        return record

    def _validate_terminal_status(
        self,
        workflow_status: str,
    ) -> None:
        if workflow_status not in TERMINAL_WORKFLOW_STATUSES:
            raise ValueError(
                f"Unsupported workflow status: {workflow_status}"
            )

    def _to_json_safe(
        self,
        value: Any,
    ) -> Any:
        if value is None:
            return None

        if isinstance(value, BaseModel):
            return value.model_dump(mode="json")

        if isinstance(value, Enum):
            return value.value

        if isinstance(value, datetime | date):
            return value.isoformat()

        if isinstance(value, dict):
            return {
                str(key): self._to_json_safe(item)
                for key, item in value.items()
            }

        if isinstance(value, list | tuple | set):
            return [
                self._to_json_safe(item)
                for item in value
            ]

        return value
