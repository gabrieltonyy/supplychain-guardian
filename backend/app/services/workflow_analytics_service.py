from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.risk_assessment import RiskAssessmentRecord
from app.db.models.workflow_run import WorkflowRun


class WorkflowAnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def workflow_summary(self):
        total_result = await self.session.execute(
            select(func.count(WorkflowRun.id))
        )
        total_runs = total_result.scalar() or 0

        completed_result = await self.session.execute(
            select(func.count(WorkflowRun.id)).where(
                WorkflowRun.workflow_status == "completed"
            )
        )
        completed_runs = completed_result.scalar() or 0

        completed_without_mitigation_result = await self.session.execute(
            select(func.count(WorkflowRun.id)).where(
                WorkflowRun.workflow_status == "completed_without_mitigation"
            )
        )
        completed_without_mitigation_runs = (
            completed_without_mitigation_result.scalar() or 0
        )

        failed_result = await self.session.execute(
            select(func.count(WorkflowRun.id)).where(
                WorkflowRun.workflow_status == "failed"
            )
        )
        failed_runs = failed_result.scalar() or 0

        successful_runs = (
            completed_runs
            + completed_without_mitigation_runs
        )

        return {
            "total_runs": total_runs,
            "completed_runs": completed_runs,
            "completed_without_mitigation_runs": (
                completed_without_mitigation_runs
            ),
            "failed_runs": failed_runs,
            "successful_runs": successful_runs,
            "success_rate": (
                round((successful_runs / total_runs) * 100, 2)
                if total_runs > 0
                else 0
            ),
        }

    async def risk_distribution(self):
        result = await self.session.execute(
            select(
                RiskAssessmentRecord.level,
                func.count(RiskAssessmentRecord.id),
            ).group_by(
                RiskAssessmentRecord.level
            )
        )

        rows = result.all()

        return [
            {
                "risk_level": (
                    row[0].value
                    if hasattr(row[0], "value")
                    else str(row[0])
                ),
                "count": row[1],
            }
            for row in rows
        ]

    async def supplier_risk_rankings(
        self,
        limit: int = 10,
    ):
        result = await self.session.execute(
            select(
                RiskAssessmentRecord.supplier_id,
                func.avg(
                    RiskAssessmentRecord.score
                ).label("avg_risk_score"),
                func.count(
                    RiskAssessmentRecord.id
                ).label("assessment_count"),
            )
            .group_by(RiskAssessmentRecord.supplier_id)
            .order_by(
                func.avg(
                    RiskAssessmentRecord.score
                ).desc()
            )
            .limit(limit)
        )

        rows = result.all()

        return [
            {
                "supplier_id": row[0],
                "average_risk_score": round(float(row[1]), 2),
                "assessment_count": row[2],
            }
            for row in rows
        ]