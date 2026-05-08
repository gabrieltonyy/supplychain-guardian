from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.supplier import Supplier


class SupplierRepository:
    """
    Database access layer for supplier records.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        supplier_id: str,
    ) -> Supplier | None:
        result = await self.session.execute(
            select(Supplier).where(
                Supplier.id == supplier_id
            )
        )

        return result.scalar_one_or_none()

    async def list_all(
        self,
    ) -> list[Supplier]:
        result = await self.session.execute(
            select(Supplier).order_by(Supplier.name)
        )

        return list(result.scalars().all())

    async def list_approved_alternatives(
        self,
        product_categories: list[str],
        exclude_regions: list[str],
        min_capacity_units: int = 0,
    ) -> list[Supplier]:
        """
        Find approved alternative suppliers.

        MVP query uses broad matching.
        We will refine with category overlap later.
        """

        query = select(Supplier).where(
            Supplier.compliance_status == "APPROVED",
            Supplier.capacity_units_per_month >= min_capacity_units,
        )

        if exclude_regions:
            query = query.where(
                Supplier.region.notin_(exclude_regions)
            )

        result = await self.session.execute(query)

        suppliers = list(result.scalars().all())

        if not product_categories:
            return suppliers

        return [
            supplier
            for supplier in suppliers
            if set(supplier.product_categories or []).intersection(
                product_categories
            )
        ]

    async def create(
        self,
        supplier: Supplier,
    ) -> Supplier:
        self.session.add(supplier)
        await self.session.flush()
        await self.session.refresh(supplier)

        return supplier

    async def upsert_many(
        self,
        suppliers: list[Supplier],
    ) -> list[Supplier]:
        """
        Simple MVP insert-many helper.

        Later we can replace this with PostgreSQL ON CONFLICT.
        """

        self.session.add_all(suppliers)
        await self.session.flush()

        for supplier in suppliers:
            await self.session.refresh(supplier)

        return suppliers