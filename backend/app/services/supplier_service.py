from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.supplier import Supplier
from app.db.repositories.supplier_repository import SupplierRepository


class SupplierService:
    """
    Supplier business service.

    Provides DB-backed supplier lookups while preserving
    clean service-level behavior for agents and workflows.
    """

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.repository = SupplierRepository(session)

    async def get_supplier_by_id(
        self,
        supplier_id: str,
    ) -> Supplier | None:
        return await self.repository.get_by_id(supplier_id)

    async def list_suppliers(self) -> list[Supplier]:
        return await self.repository.list_all()

    async def list_approved_alternatives(
        self,
        product_categories: list[str],
        exclude_regions: list[str],
        min_capacity_units: int = 0,
    ) -> list[Supplier]:
        return await self.repository.list_approved_alternatives(
            product_categories=product_categories,
            exclude_regions=exclude_regions,
            min_capacity_units=min_capacity_units,
        )


def supplier_to_dict(
    supplier: Supplier,
) -> dict:
    """
    Convert Supplier ORM model into plain dict used by agents.
    """

    return {
        "id": supplier.id,
        "name": supplier.name,
        "country": supplier.country,
        "region": supplier.region,
        "contact_email": supplier.contact_email,
        "product_categories": supplier.product_categories or [],
        "certifications": supplier.certifications or [],
        "status": supplier.status.value.lower(),
        "compliance_status": supplier.compliance_status.value.lower(),
        "relationship_status": supplier.relationship_status.value.lower(),
        "unit_cost": supplier.unit_cost,
        "typical_lead_time_days": supplier.typical_lead_time_days,
        "capacity_units_per_month": supplier.capacity_units_per_month,
        "on_time_delivery_rate": supplier.on_time_delivery_rate,
        "quality_score": supplier.quality_score,
        "latest_risk_score": supplier.latest_risk_score,
        "supplier_profile_text": supplier.supplier_profile_text,
        "embedding_refreshed_at": supplier.embedding_refreshed_at,
    }