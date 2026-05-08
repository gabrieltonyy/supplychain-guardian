from uuid import uuid4

from app.engine.compliance_verdict import compute_compliance_verdict
from app.engine.regulatory_validator import run_regulatory_checks
from app.engine.sanctions_screener import screen_all_suppliers
from app.llm.client import llm
from app.schemas.compliance import AuditLogEntry
from app.schemas.execution import ExecutionRecord
from app.schemas.mitigation import MitigationPlan
from app.services.mitigation_service import mitigation_service


class ComplianceService:
    """
    Coordinates sanctions screening, regulatory checks,
    verdict computation, and immutable audit log creation.
    """

    async def get_supplier_for_compliance(
        self,
        supplier_id: str,
    ) -> dict:
        suppliers = await mitigation_service.get_alternative_suppliers(
            {"id": supplier_id}
        )

        supplier_lookup = {
            supplier["id"]: supplier
            for supplier in suppliers
        }

        supplier = supplier_lookup.get(supplier_id)

        if supplier is None:
            return {
                "id": supplier_id,
                "name": supplier_id,
                "country_code": "UNKNOWN",
            }

        supplier["country_code"] = self._country_to_code(
            supplier.get("country")
        )

        return supplier

    async def generate_audit_log(
        self,
        execution_record: ExecutionRecord,
        mitigation_plan: MitigationPlan,
        workflow_run_id: str | None = None,
    ) -> AuditLogEntry:
        supplier_ids = list(
            {
                rfq.supplier_id
                for rfq in execution_record.rfqs
            }
        )

        suppliers = [
            await self.get_supplier_for_compliance(supplier_id)
            for supplier_id in supplier_ids
        ]

        current_order = await mitigation_service.get_active_order(
            mitigation_plan.original_supplier_id
        )

        # Add compliance-relevant mock metadata to order.
        for item in current_order["line_items"]:
            item.setdefault("category", "electronics")
            item.setdefault("hs_code", "854231")

        sanctions_results = await screen_all_suppliers(suppliers)

        regulatory_results = []

        for supplier in suppliers:
            results = await run_regulatory_checks(
                supplier=supplier,
                order=current_order,
            )
            regulatory_results.extend(results)

        verdict, rationale = compute_compliance_verdict(
            sanctions_results=sanctions_results,
            regulatory_results=regulatory_results,
        )

        llm_summary = await llm.ainvoke(
            f"Compliance review for execution record "
            f"{execution_record.execution_id}.\n"
            f"Verdict: {verdict.value}.\n"
            f"Rationale: {rationale}.\n"
            "Write a concise audit summary based only on this data."
        )

        return AuditLogEntry(
            log_id=str(uuid4()),
            workflow_run_id=workflow_run_id or str(uuid4()),
            agent_version="0.1.0",
            execution_record_id=execution_record.execution_id,
            input_hash=AuditLogEntry.compute_input_hash(
                execution_record.model_dump(mode="json")
            ),
            sanctions_results=sanctions_results,
            regulatory_results=regulatory_results,
            verdict=verdict,
            verdict_rationale=rationale,
            llm_summary=llm_summary,
        )

    def _country_to_code(
        self,
        country: str | None,
    ) -> str:
        mapping = {
            "India": "IN",
            "Germany": "DE",
            "Vietnam": "VN",
            "China": "CN",
            "Kenya": "KE",
        }

        return mapping.get(country or "", country or "UNKNOWN")


compliance_service = ComplianceService()