from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.compliance_audit import ComplianceAuditLog
from app.db.models.execution_record import ExecutionRecordModel
from app.db.models.mitigation_plan import MitigationPlanRecord
from app.db.models.rfq import RFQRecord
from app.db.models.risk_assessment import RiskAssessmentRecord
from app.db.models.workflow_event import WorkflowEvent
from app.db.models.workflow_run import WorkflowRun


class WorkflowQueryService:
    """
    Read/replay service for persisted workflow runs.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_runs(
        self,
        limit: int = 50,
    ) -> list[WorkflowRun]:
        result = await self.session.execute(
            select(WorkflowRun)
            .order_by(desc(WorkflowRun.started_at))
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_run(
        self,
        workflow_id: str,
    ) -> WorkflowRun | None:
        result = await self.session.execute(
            select(WorkflowRun).where(
                WorkflowRun.workflow_id == workflow_id
            )
        )

        return result.scalar_one_or_none()

    async def get_timeline(
        self,
        workflow_id: str,
    ) -> list[WorkflowEvent]:
        result = await self.session.execute(
            select(WorkflowEvent)
            .where(WorkflowEvent.workflow_id == workflow_id)
            .order_by(WorkflowEvent.created_at)
        )

        return list(result.scalars().all())

    async def get_replay(
        self,
        workflow_id: str,
    ) -> dict | None:
        workflow_run = await self.get_run(workflow_id)

        if workflow_run is None:
            return None

        risk_result = await self.session.execute(
            select(RiskAssessmentRecord)
            .where(RiskAssessmentRecord.workflow_id == workflow_id)
            .order_by(desc(RiskAssessmentRecord.assessed_at))
            .limit(1)
        )
        risk_assessment = risk_result.scalar_one_or_none()

        mitigation_result = await self.session.execute(
            select(MitigationPlanRecord)
            .where(MitigationPlanRecord.workflow_id == workflow_id)
            .order_by(desc(MitigationPlanRecord.created_at))
            .limit(1)
        )
        mitigation_plan = mitigation_result.scalar_one_or_none()

        execution_result = await self.session.execute(
            select(ExecutionRecordModel)
            .where(ExecutionRecordModel.workflow_id == workflow_id)
            .order_by(desc(ExecutionRecordModel.created_at))
            .limit(1)
        )
        execution_record = execution_result.scalar_one_or_none()

        rfqs = []
        if execution_record is not None:
            rfq_result = await self.session.execute(
                select(RFQRecord)
                .where(
                    RFQRecord.mitigation_plan_id
                    == execution_record.mitigation_plan_id
                )
                .order_by(RFQRecord.generated_at)
            )
            rfqs = list(rfq_result.scalars().all())

        compliance_result = await self.session.execute(
            select(ComplianceAuditLog)
            .where(ComplianceAuditLog.workflow_id == workflow_id)
            .order_by(desc(ComplianceAuditLog.created_at))
            .limit(1)
        )
        compliance_audit = compliance_result.scalar_one_or_none()

        timeline = await self.get_timeline(workflow_id)

        return {
            "workflow_run": self._model_to_dict(workflow_run),
            "risk_assessment": self._model_to_dict(risk_assessment),
            "mitigation_plan": self._model_to_dict(mitigation_plan),
            "execution_record": self._model_to_dict(execution_record),
            "rfqs": [
                self._model_to_dict(rfq)
                for rfq in rfqs
            ],
            "compliance_audit": self._model_to_dict(compliance_audit),
            "timeline": [
                self._model_to_dict(event)
                for event in timeline
            ],
        }

    def _model_to_dict(self, model):
        if model is None:
            return None

        result = {}

        for column in model.__table__.columns:
            value = getattr(model, column.name)

            if hasattr(value, "value"):
                value = value.value

            if hasattr(value, "isoformat"):
                value = value.isoformat()

            result[column.name] = value

        return result