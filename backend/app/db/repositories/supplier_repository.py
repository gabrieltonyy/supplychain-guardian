from sqlalchemy import not_, select
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
                not_(Supplier.id.like("SUP-ALT-%")),
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

    async def find_alternative_suppliers(
        self,
        original_supplier_id: str,
        product_categories: list[str],
        exclude_regions: list[str] | None = None,
        required_capacity: int = 30000,
        max_risk_score: float = 50.0,
        limit: int = 10,
    ) -> list[Supplier]:
        """
        DB-backed alternative supplier discovery.

        Rules:
        - exclude original supplier
        - exclude legacy SUP-ALT-* mock/demo suppliers
        - supplier must be active
        - supplier must be approved
        - supplier must have sufficient capacity
        - supplier risk must be below threshold
        - supplier must overlap categories
        - optionally exclude regions
        """

        exclude_regions = exclude_regions or []

        stmt = (
            select(Supplier)
            .where(
                Supplier.id != original_supplier_id,
                not_(Supplier.id.like("SUP-ALT-%")),
                Supplier.status == SupplierStatus.ACTIVE,
                Supplier.compliance_status
                == ComplianceStatus.APPROVED,
                Supplier.capacity_units_per_month
                >= required_capacity,
                Supplier.latest_risk_score
                <= max_risk_score,
            )
        )

        result = await self.session.execute(stmt)

        suppliers = list(result.scalars().all())

        filtered: list[Supplier] = []

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

        filtered.sort(
            key=lambda s: (
                s.latest_risk_score or 9999,
                s.typical_lead_time_days or 9999,
                s.unit_cost or 9999,
            )
        )

        return filtered[:limit]