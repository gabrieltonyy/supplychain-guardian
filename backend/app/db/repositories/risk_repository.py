from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.risk_assessment import RiskAssessmentRecord
from app.schemas.assessments import RiskAssessment


class RiskRepository:
    """
    Database access layer for supplier risk assessments.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_assessment(
        self,
        assessment: RiskAssessment,
        anomaly_data: dict | None = None,
        reasoning_summary: str | None = None,
    ) -> RiskAssessmentRecord:
        record = RiskAssessmentRecord(
            supplier_id=assessment.supplier_id,
            score=assessment.score,
            level=assessment.level,
            factor_breakdown=assessment.factor_breakdown,
            contributing_signals=assessment.contributing_signals,
            anomaly_detected=bool(
                anomaly_data and anomaly_data.get("is_anomaly")
            ),
            anomaly_data=anomaly_data,
            reasoning_summary=reasoning_summary,
            assessed_at=assessment.assessed_at,
        )

        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)

        return record

    async def get_latest_for_supplier(
        self,
        supplier_id: str,
    ) -> RiskAssessmentRecord | None:
        result = await self.session.execute(
            select(RiskAssessmentRecord)
            .where(RiskAssessmentRecord.supplier_id == supplier_id)
            .order_by(desc(RiskAssessmentRecord.assessed_at))
            .limit(1)
        )

        return result.scalar_one_or_none()

    async def get_score_history(
        self,
        supplier_id: str,
        limit: int = 30,
    ) -> list[float]:
        result = await self.session.execute(
            select(RiskAssessmentRecord.score)
            .where(RiskAssessmentRecord.supplier_id == supplier_id)
            .order_by(desc(RiskAssessmentRecord.assessed_at))
            .limit(limit)
        )

        scores = list(result.scalars().all())

        return list(reversed(scores))