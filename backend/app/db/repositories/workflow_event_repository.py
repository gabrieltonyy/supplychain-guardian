from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.workflow_event import WorkflowEvent


class WorkflowEventRepository:
    """
    Database access layer for workflow timeline events.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        workflow_id: str,
        supplier_id: str,
        event_type: str,
        status: str,
        agent_name: str | None = None,
        message: str | None = None,
        payload: dict | None = None,
        error_message: str | None = None,
    ) -> WorkflowEvent:
        record = WorkflowEvent(
            workflow_id=workflow_id,
            supplier_id=supplier_id,
            event_type=event_type,
            agent_name=agent_name,
            status=status,
            message=message,
            payload=payload,
            error_message=error_message,
        )

        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)

        return record

    async def list_by_workflow_id(
        self,
        workflow_id: str,
    ) -> list[WorkflowEvent]:
        result = await self.session.execute(
            select(WorkflowEvent)
            .where(WorkflowEvent.workflow_id == workflow_id)
            .order_by(asc(WorkflowEvent.created_at))
        )

        return list(result.scalars().all())

    async def list_recent(
        self,
        limit: int = 100,
    ) -> list[WorkflowEvent]:
        result = await self.session.execute(
            select(WorkflowEvent)
            .order_by(desc(WorkflowEvent.created_at))
            .limit(limit)
        )

        return list(result.scalars().all())