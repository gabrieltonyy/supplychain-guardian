import asyncio

from app.db.qdrant import search_similar_suppliers
from app.engine.ranker import rank_scenarios
from app.engine.simulator import simulate_switch
from app.schemas.assessments import RiskAssessment
from app.schemas.mitigation import (
    MitigationPlan,
    RecommendedOption,
    SimulatedScenario,
)


class MitigationService:
    """
    Coordinates candidate discovery, switch simulation,
    TOPSIS ranking, and mitigation plan generation.
    """

    async def get_at_risk_supplier(
        self,
        supplier_id: str,
    ) -> dict:
        """
        Mock supplier lookup.
        Later replaced by PostgreSQL supplier repository.
        """

        return {
            "id": supplier_id,
            "name": "Original Supplier",
            "country": "China",
            "region": "East Asia",
            "product_categories": ["electronics", "components"],
            "unit_cost": 10.0,
            "typical_lead_time_days": 20,
            "capacity_units_per_month": 80000,
        }

    async def get_active_order(
        self,
        supplier_id: str,
    ) -> dict:
        """
        Mock active order lookup.
        Later replaced by order service / ERP connector.
        """

        return {
            "supplier_id": supplier_id,
            "supplier_name": "Original Supplier",
            "destination_country": "Kenya",
            "destination": "Nairobi Warehouse",
            "volume_units": 30000,
            "risk_level": "HIGH",
            "line_items": [
                {
                    "sku": "SKU-001",
                    "description": "Semiconductor Chip",
                    "quantity": 30000,
                    "unit": "pcs",
                    "unit_cost": 10.0,
                }
            ],
        }

    async def get_alternative_suppliers(
        self,
        at_risk_supplier: dict,
    ) -> list[dict]:
        """
        Legacy mock hard-filtered supplier list.

        DB-backed workflows should pass candidate_suppliers directly
        into generate_mitigation_plan().
        """

        _ = at_risk_supplier

        return [
            {
                "id": "SUP-ALT-001",
                "name": "Apex India Manufacturing",
                "country": "India",
                "region": "South Asia",
                "contact_email": "sales@apexindia.example",
                "product_categories": ["electronics", "components"],
                "unit_cost": 11.0,
                "typical_lead_time_days": 18,
                "latest_risk_score": 28,
                "capacity_units_per_month": 50000,
                "relationship_status": "dormant",
                "compliance_status": "approved",
            },
            {
                "id": "SUP-ALT-002",
                "name": "EuroTech Components",
                "country": "Germany",
                "region": "Europe",
                "contact_email": "rfq@eurotech.example",
                "product_categories": ["electronics", "components"],
                "unit_cost": 12.15,
                "typical_lead_time_days": 15,
                "latest_risk_score": 18,
                "capacity_units_per_month": 45000,
                "relationship_status": "active_secondary",
                "compliance_status": "approved",
            },
            {
                "id": "SUP-ALT-003",
                "name": "VietPro Industrial",
                "country": "Vietnam",
                "region": "Southeast Asia",
                "contact_email": "sales@vietpro.example",
                "product_categories": ["electronics", "components"],
                "unit_cost": 10.15,
                "typical_lead_time_days": 24,
                "latest_risk_score": 35,
                "capacity_units_per_month": 60000,
                "relationship_status": "new",
                "compliance_status": "approved",
            },
        ]

    async def discover_candidates(
        self,
        at_risk_supplier: dict,
        risk_assessment: RiskAssessment,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Legacy discovery using:
        - hard-filtered mock supplier lookup,
        - vector similarity ranking.
        """

        _ = risk_assessment

        hard_filter_task = self.get_alternative_suppliers(at_risk_supplier)

        vector_search_task = search_similar_suppliers(
            supplier_id=at_risk_supplier["id"],
            top_k=top_k * 2,
            filters={"status": "active"},
        )

        hard_results, vector_results = await asyncio.gather(
            hard_filter_task,
            vector_search_task,
        )

        hard_by_id = {
            supplier["id"]: supplier
            for supplier in hard_results
        }

        ranked_candidates = []

        for vector_result in vector_results:
            supplier_id = vector_result["id"]

            if supplier_id in hard_by_id:
                supplier = hard_by_id[supplier_id]
                supplier["similarity_score"] = vector_result.get(
                    "similarity_score"
                )
                ranked_candidates.append(supplier)

        return ranked_candidates[:top_k]

    async def generate_mitigation_plan(
        self,
        supplier_id: str,
        risk_assessment: RiskAssessment,
        justification: str,
        candidate_suppliers: list[dict] | None = None,
        at_risk_supplier: dict | None = None,
        active_order: dict | None = None,
    ) -> tuple[
        MitigationPlan,
        list[dict],
        list[SimulatedScenario],
        list[tuple[SimulatedScenario, float]],
    ]:
        """
        Main mitigation workflow.

        If candidate_suppliers is provided, it is used directly.
        This enables DB-backed supplier discovery while preserving
        the legacy mock/Qdrant fallback.
        """

        if at_risk_supplier is None:
            at_risk_supplier = await self.get_at_risk_supplier(supplier_id)

        if active_order is None:
            current_order = await self.get_active_order(supplier_id)
        else:
            current_order = active_order

        current_order["supplier_name"] = at_risk_supplier.get(
            "name",
            current_order.get("supplier_name"),
        )

        for item in current_order.get("line_items", []):
            item["unit_cost"] = at_risk_supplier.get(
                "unit_cost",
                item.get("unit_cost", 0),
            )

        if candidate_suppliers:
            candidates = candidate_suppliers
        else:
            candidates = await self.discover_candidates(
                at_risk_supplier=at_risk_supplier,
                risk_assessment=risk_assessment,
            )

        if not candidates:
            plan = MitigationPlan(
                original_supplier_id=supplier_id,
                risk_score=risk_assessment.score,
                recommended_options=[],
                justification=justification,
            )

            return plan, [], [], []

        scenarios = await asyncio.gather(
            *[
                asyncio.to_thread(
                    simulate_switch,
                    at_risk_supplier,
                    candidate,
                    current_order,
                    risk_assessment,
                )
                for candidate in candidates
            ]
        )

        ranked = rank_scenarios(list(scenarios))

        top3 = ranked[:3]

        recommended_options = [
            RecommendedOption(
                rank=index + 1,
                supplier_id=scenario.supplier_id,
                topsis_score=round(score, 3),
                cost_delta_pct=scenario.cost_delta_pct,
                lead_time_delta_days=scenario.lead_time_delta_days,
                residual_risk_score=scenario.residual_risk_score,
                onboarding_weeks=scenario.onboarding_weeks,
                confidence=scenario.confidence,
            )
            for index, (scenario, score) in enumerate(top3)
        ]

        plan = MitigationPlan(
            original_supplier_id=supplier_id,
            risk_score=risk_assessment.score,
            recommended_options=recommended_options,
            justification=justification,
        )

        return plan, candidates, list(scenarios), ranked


mitigation_service = MitigationService()