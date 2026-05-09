from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc
from app.db.models.workflow_run import WorkflowRun


class WorkflowRunRepository:
    """
    Database access layer for durable workflow runs.
    """

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_by_workflow_id(
        self,
        workflow_id: str,
    ) -> WorkflowRun | None:
        result = await self.session.execute(
            select(WorkflowRun).where(
                WorkflowRun.workflow_id == workflow_id
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        supplier_id: str,
        workflow_id: str,
        workflow_status: str,
        correlation_id: str | None = None,
    ) -> WorkflowRun:
        record = WorkflowRun(
            supplier_id=supplier_id,
            workflow_id=workflow_id,
            workflow_status=workflow_status,
            correlation_id=correlation_id,
        )

        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)

        return record

    async def start_or_update(
        self,
        supplier_id: str,
        workflow_id: str,
        correlation_id: str | None = None,
    ) -> WorkflowRun:
        record = await self.get_by_workflow_id(workflow_id)

        if record is None:
            return await self.create(
                supplier_id=supplier_id,
                workflow_id=workflow_id,
                workflow_status="running",
                correlation_id=correlation_id,
            )

        now = datetime.now(UTC)

        record.supplier_id = supplier_id
        record.workflow_status = "running"
        record.correlation_id = correlation_id
        record.completed_at = None
        record.error_message = None
        record.final_state_snapshot = None
        record.updated_at = now

        await self.session.flush()
        await self.session.refresh(record)

        return record

    async def complete(
        self,
        workflow_id: str,
        workflow_status: str,
        final_state_snapshot: dict | None = None,
    ) -> WorkflowRun:
        record = await self.get_by_workflow_id(workflow_id)

        if record is None:
            raise ValueError(
                f"Workflow run not found: {workflow_id}"
            )

        now = datetime.now(UTC)

        record.workflow_status = workflow_status
        record.completed_at = now
        record.error_message = None
        record.final_state_snapshot = final_state_snapshot
        record.updated_at = now

        await self.session.flush()
        await self.session.refresh(record)

        return record

    async def list_recent(
        self,
        limit: int = 50,
    ) -> list[WorkflowRun]:
        result = await self.session.execute(
            select(WorkflowRun)
            .order_by(desc(WorkflowRun.started_at))
            .limit(limit)
        )

        return list(result.scalars().all())

    async def fail(
        self,
        workflow_id: str,
        error_message: str,
        final_state_snapshot: dict | None = None,
    ) -> WorkflowRun:
        record = await self.get_by_workflow_id(workflow_id)

        if record is None:
            raise ValueError(
                f"Workflow run not found: {workflow_id}"
            )

        now = datetime.now(UTC)

        record.workflow_status = "failed"
        record.completed_at = now
        record.error_message = error_message
        record.final_state_snapshot = final_state_snapshot
        record.updated_at = now

        await self.session.flush()
        await self.session.refresh(record)

        return record
