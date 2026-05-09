from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.supplier import Supplier
from app.db.repositories.supplier_repository import SupplierRepository


class DbMitigationDiscoveryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.supplier_repository = SupplierRepository(session)

    async def get_original_supplier_context(
        self,
        supplier_id: str,
    ) -> dict | None:
        supplier = await self.supplier_repository.get_by_id(supplier_id)

        if supplier is None:
            return None

        return self._supplier_to_candidate(
            supplier=supplier,
            original_supplier=supplier,
        )

    async def find_candidates(
        self,
        original_supplier_id: str,
        required_capacity: int = 30000,
        limit: int = 10,
    ) -> list[dict]:
        original_supplier = await self.supplier_repository.get_by_id(
            original_supplier_id
        )

        if original_supplier is None:
            return []

        product_categories = original_supplier.product_categories or []

        candidates = await self.supplier_repository.find_alternative_suppliers(
            original_supplier_id=original_supplier_id,
            product_categories=product_categories,
            required_capacity=required_capacity,
            max_risk_score=50.0,
            limit=limit,
        )

        return [
            self._supplier_to_candidate(
                supplier=supplier,
                original_supplier=original_supplier,
            )
            for supplier in candidates
        ]

    def _supplier_to_candidate(
        self,
        supplier: Supplier,
        original_supplier: Supplier,
    ) -> dict:
        return {
            "id": supplier.id,
            "name": supplier.name,
            "country": supplier.country,
            "region": supplier.region,
            "contact_email": supplier.contact_email,
            "product_categories": supplier.product_categories or [],
            "unit_cost": float(supplier.unit_cost or 0),
            "typical_lead_time_days": supplier.typical_lead_time_days or 0,
            "latest_risk_score": float(supplier.latest_risk_score or 0),
            "capacity_units_per_month": supplier.capacity_units_per_month or 0,
            "relationship_status": (
                supplier.relationship_status.value
                if hasattr(supplier.relationship_status, "value")
                else str(supplier.relationship_status)
            ).lower(),
            "compliance_status": (
                supplier.compliance_status.value
                if hasattr(supplier.compliance_status, "value")
                else str(supplier.compliance_status)
            ).lower(),
            "similarity_score": self._calculate_similarity_score(
                supplier=supplier,
                original_supplier=original_supplier,
            ),
        }

    def _calculate_similarity_score(
        self,
        supplier: Supplier,
        original_supplier: Supplier,
    ) -> float:
        score = 0.0

        supplier_categories = set(supplier.product_categories or [])
        original_categories = set(original_supplier.product_categories or [])

        if original_categories:
            overlap = supplier_categories.intersection(original_categories)
            score += (len(overlap) / len(original_categories)) * 0.45

        compliance_status = (
            supplier.compliance_status.value
            if hasattr(supplier.compliance_status, "value")
            else str(supplier.compliance_status)
        )

        relationship_status = (
            supplier.relationship_status.value
            if hasattr(supplier.relationship_status, "value")
            else str(supplier.relationship_status)
        )

        if compliance_status == "APPROVED":
            score += 0.2

        if supplier.latest_risk_score is not None:
            if supplier.latest_risk_score <= 20:
                score += 0.2
            elif supplier.latest_risk_score <= 35:
                score += 0.15
            elif supplier.latest_risk_score <= 50:
                score += 0.1

        if supplier.capacity_units_per_month:
            if supplier.capacity_units_per_month >= 50000:
                score += 0.1
            elif supplier.capacity_units_per_month >= 30000:
                score += 0.05

        if relationship_status in {
            "ACTIVE_SECONDARY",
            "PREFERRED",
            "APPROVED_BACKUP",
        }:
            score += 0.05

        return round(min(score, 1.0), 2)