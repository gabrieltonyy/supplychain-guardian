from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.rfq import RFQActionHistory, RFQRecord
from app.schemas.execution import RFQStatus
from app.schemas.rfqs import RFQActionType


class RFQService:
    """
    Query and mutate persisted RFQ review records.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_rfqs(
        self,
        search: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[RFQRecord], int]:
        stmt = select(RFQRecord)
        count_stmt = select(func.count(RFQRecord.id))
        filters = []

        if status and status.upper() != "ALL":
            filters.append(RFQRecord.status == self._parse_status(status))

        if search:
            query = f"%{search.strip()}%"
            filters.append(
                or_(
                    RFQRecord.rfq_id.ilike(query),
                    RFQRecord.supplier_id.ilike(query),
                    RFQRecord.supplier_code.ilike(query),
                    RFQRecord.supplier_name.ilike(query),
                    RFQRecord.workflow_id.ilike(query),
                )
            )

        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        result = await self.session.execute(
            stmt.order_by(RFQRecord.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(result.scalars().all()), total

    async def get_rfq(self, rfq_id: str) -> RFQRecord | None:
        result = await self.session.execute(
            select(RFQRecord).where(
                or_(
                    RFQRecord.id == rfq_id,
                    RFQRecord.rfq_id == rfq_id,
                )
            )
        )

        return result.scalar_one_or_none()

    async def approve(
        self,
        rfq_id: str,
        actor: str = "procurement_user",
        note: str | None = None,
    ) -> RFQRecord | None:
        return await self._transition(
            rfq_id=rfq_id,
            action_type=RFQActionType.APPROVE,
            new_status=RFQStatus.APPROVED,
            actor=actor,
            note=note,
        )

    async def request_review(
        self,
        rfq_id: str,
        actor: str = "procurement_user",
        note: str | None = None,
    ) -> RFQRecord | None:
        return await self._transition(
            rfq_id=rfq_id,
            action_type=RFQActionType.REQUEST_REVIEW,
            new_status=RFQStatus.REVIEW_REQUESTED,
            actor=actor,
            note=note,
        )

    async def reject(
        self,
        rfq_id: str,
        actor: str = "procurement_user",
        note: str | None = None,
    ) -> RFQRecord | None:
        return await self._transition(
            rfq_id=rfq_id,
            action_type=RFQActionType.REJECT,
            new_status=RFQStatus.REJECTED,
            actor=actor,
            note=note,
        )

    async def list_actions(
        self,
        rfq_id: str,
    ) -> list[RFQActionHistory] | None:
        rfq = await self.get_rfq(rfq_id)

        if rfq is None:
            return None

        result = await self.session.execute(
            select(RFQActionHistory)
            .where(RFQActionHistory.rfq_record_id == rfq.id)
            .order_by(RFQActionHistory.created_at.desc())
        )

        return list(result.scalars().all())

    async def _transition(
        self,
        rfq_id: str,
        action_type: RFQActionType,
        new_status: RFQStatus,
        actor: str,
        note: str | None,
    ) -> RFQRecord | None:
        rfq = await self.get_rfq(rfq_id)

        if rfq is None:
            return None

        previous_status = self._status_name(rfq.status)
        now = datetime.now(UTC)

        rfq.status = new_status
        rfq.updated_at = now

        if note:
            rfq.notes = note

        self.session.add(
            RFQActionHistory(
                rfq_record_id=rfq.id,
                rfq_id=rfq.rfq_id,
                action_type=action_type.value,
                previous_status=previous_status,
                new_status=new_status.name,
                actor=actor or "procurement_user",
                note=note,
                created_at=now,
            )
        )

        await self.session.commit()
        await self.session.refresh(rfq)

        return rfq

    def _parse_status(self, status: str) -> RFQStatus:
        normalized = status.strip().upper().replace(" ", "_").replace("-", "_")
        return RFQStatus[normalized]

    def _status_name(self, status: RFQStatus | str) -> str:
        if isinstance(status, RFQStatus):
            return status.name

        return str(status).upper()
