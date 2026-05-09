from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.active_order_repository import (
    ActiveOrderRepository,
)


class DbOrderContextService:
    def __init__(self, session: AsyncSession):
        self.repository = ActiveOrderRepository(session)

    async def get_active_order_context(
        self,
        supplier_id: str,
    ) -> dict | None:
        order = await self.repository.get_latest_active_for_supplier(
            supplier_id=supplier_id,
        )

        if order is None:
            return None

        return {
            "supplier_id": order.supplier_id,
            "supplier_name": order.supplier_name,
            "destination_country": order.destination_country,
            "destination": order.destination,
            "volume_units": order.volume_units,
            "risk_level": order.risk_level,
            "line_items": order.line_items or [],
        }