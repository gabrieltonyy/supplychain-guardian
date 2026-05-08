from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.mitigation_plan import MitigationPlanRecord
from app.schemas.mitigation import MitigationPlan, SimulatedScenario


class MitigationRepository:
    """
    Database access layer for mitigation plans.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_plan(
        self,
        plan: MitigationPlan,
        candidate_suppliers: list[dict],
        simulated_scenarios: list[SimulatedScenario],
    ) -> MitigationPlanRecord:
        record = MitigationPlanRecord(
            original_supplier_id=plan.original_supplier_id,
            risk_score=plan.risk_score,
            recommended_options=[
                option.model_dump(mode="json")
                for option in plan.recommended_options
            ],
            candidate_suppliers=candidate_suppliers,
            simulated_scenarios=[
                scenario.model_dump(mode="json")
                for scenario in simulated_scenarios
            ],
            justification=plan.justification,
        )

        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)

        return record

    async def get_by_id(
        self,
        plan_id: str,
    ) -> MitigationPlanRecord | None:
        result = await self.session.execute(
            select(MitigationPlanRecord).where(
                MitigationPlanRecord.id == plan_id
            )
        )

        return result.scalar_one_or_none()

    async def get_latest_for_supplier(
        self,
        supplier_id: str,
    ) -> MitigationPlanRecord | None:
        result = await self.session.execute(
            select(MitigationPlanRecord)
            .where(MitigationPlanRecord.original_supplier_id == supplier_id)
            .order_by(desc(MitigationPlanRecord.created_at))
            .limit(1)
        )

        return result.scalar_one_or_none()