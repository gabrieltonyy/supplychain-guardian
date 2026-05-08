from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.supplier import (
    ComplianceStatus,
    Supplier,
    SupplierStatus,
)


class SupplierRepository:
    """
    Repository layer for supplier persistence and querying.
    """

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_by_id(
        self,
        supplier_id: str,
    ) -> Supplier | None:
        stmt = select(Supplier).where(
            Supplier.id == supplier_id
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def list_all(
        self,
    ) -> list[Supplier]:
        stmt = select(Supplier)

        result = await self.session.execute(stmt)

        return list(result.scalars().all())

    async def list_active_suppliers(
        self,
    ) -> list[Supplier]:
        stmt = select(Supplier).where(
            Supplier.status == SupplierStatus.ACTIVE
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())

    async def list_approved_alternatives(
        self,
        product_categories: list[str],
        exclude_regions: list[str],
        min_capacity_units: int = 0,
    ) -> list[Supplier]:
        """
        Retrieve approved suppliers matching product categories.

        Used by mitigation strategist agent.
        """

        stmt = (
            select(Supplier)
            .where(
                Supplier.status == SupplierStatus.ACTIVE,
                Supplier.compliance_status
                == ComplianceStatus.APPROVED,
                Supplier.capacity_units_per_month
                >= min_capacity_units,
            )
        )

        result = await self.session.execute(stmt)

        suppliers = list(result.scalars().all())

        filtered = []

        for supplier in suppliers:
            supplier_categories = (
                supplier.product_categories or []
            )

            overlaps = any(
                category in supplier_categories
                for category in product_categories
            )

            if not overlaps:
                continue

            if supplier.region in exclude_regions:
                continue

            filtered.append(supplier)

        return filtered