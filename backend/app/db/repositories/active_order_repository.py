from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.active_order import ActiveOrder


class ActiveOrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_latest_active_for_supplier(
        self,
        supplier_id: str,
    ) -> ActiveOrder | None:
        result = await self.session.execute(
            select(ActiveOrder)
            .where(
                ActiveOrder.supplier_id == supplier_id,
                ActiveOrder.status == "ACTIVE",
            )
            .order_by(desc(ActiveOrder.created_at))
            .limit(1)
        )

        return result.scalar_one_or_none()