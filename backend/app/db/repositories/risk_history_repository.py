from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.risk_history import (
    SupplierRiskHistory,
)


class RiskHistoryRepository:
    """
    Repository for supplier risk history persistence
    and anomaly-analysis retrieval.
    """

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
        self,
        supplier_id: str,
        risk_score: float,
    ) -> SupplierRiskHistory:
        record = SupplierRiskHistory(
            supplier_id=supplier_id,
            risk_score=risk_score,
        )

        self.session.add(record)

        await self.session.commit()
        await self.session.refresh(record)

        return record

    async def list_by_supplier(
        self,
        supplier_id: str,
        limit: int = 20,
    ) -> list[SupplierRiskHistory]:
        stmt = (
            select(SupplierRiskHistory)
            .where(
                SupplierRiskHistory.supplier_id
                == supplier_id
            )
            .order_by(
                desc(
                    SupplierRiskHistory.assessed_at
                )
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())

    async def get_recent_scores(
        self,
        supplier_id: str,
        limit: int = 12,
    ) -> list[float]:
        records = await self.list_by_supplier(
            supplier_id=supplier_id,
            limit=limit,
        )

        ordered = list(reversed(records))

        return [
            r.risk_score
            for r in ordered
        ]