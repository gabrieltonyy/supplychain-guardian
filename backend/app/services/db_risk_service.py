from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.risk_history_repository import (
    RiskHistoryRepository,
)

from app.schemas.assessments import (
    AnomalyDetection,
    RiskAssessment,
)

from app.schemas.signals import SignalEvent

from app.services.anomaly_detection_service import (
    AnomalyDetectionService,
)

from app.services.live_signal_ingestion_service import (
    live_signal_ingestion_service,
)

from app.services.risk_scoring_service import (
    risk_scoring_service,
)


SUPPLIER_CONTEXT = {
    "SUP-CN-001": {
        "country": "China",
        "region": "Shenzhen",
        "stock_symbol": "TSM",
        "latitude": 22.5431,
        "longitude": 114.0579,
    },
    "SUP-DE-001": {
        "country": "Germany",
        "region": "Frankfurt",
        "stock_symbol": "SAP",
        "latitude": 50.1109,
        "longitude": 8.6821,
    },
    "SUP-IN-001": {
        "country": "India",
        "region": "Delhi",
        "stock_symbol": "INFY",
        "latitude": 28.6139,
        "longitude": 77.2090,
    },
    "SUP-US-001": {
        "country": "United States",
        "region": "California",
        "stock_symbol": "AAPL",
        "latitude": 37.7749,
        "longitude": -122.4194,
    },
    "SUP-IR-001": {
        "country": "Iran",
        "region": "Tehran",
        "stock_symbol": None,
        "latitude": 35.6892,
        "longitude": 51.3890,
    },
}


class DbRiskService:
    """
    Database-backed live risk assessment service.
    """

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

        self.risk_history_repository = (
            RiskHistoryRepository(session)
        )

        self.anomaly_service = (
            AnomalyDetectionService(
                risk_history_repository=self.risk_history_repository,
                zscore_threshold=2.0,
            )
        )

    async def gather_live_signals(
        self,
        supplier_id: str,
    ) -> list[SignalEvent]:

        context = SUPPLIER_CONTEXT.get(
            supplier_id,
            {
                "country": "Unknown",
                "region": "Unknown",
                "stock_symbol": None,
                "latitude": None,
                "longitude": None,
            },
        )

        return await live_signal_ingestion_service.ingest_supplier_signals(
            supplier_id=supplier_id,
            country=context["country"],
            region=context["region"],
            stock_symbol=context["stock_symbol"],
            latitude=context["latitude"],
            longitude=context["longitude"],
        )

    async def assess_supplier_risk(
        self,
        supplier_id: str,
        region: str,
    ) -> tuple[
        RiskAssessment,
        AnomalyDetection,
        list[SignalEvent],
    ]:

        signals = await self.gather_live_signals(
            supplier_id=supplier_id,
        )

        scoring_result = (
            await risk_scoring_service.calculate_risk_score(
                supplier_id=supplier_id,
                signals=signals,
            )
        )

        assessment = RiskAssessment(
            supplier_id=supplier_id,
            score=scoring_result["score"],
            level=scoring_result["level"],
            factor_breakdown=scoring_result[
                "factor_breakdown"
            ],
            contributing_signals=scoring_result[
                "contributing_signals"
            ],
        )

        anomaly_dict = (
            await self.anomaly_service.detect_supplier_anomaly(
                supplier_id=supplier_id,
                current_score=assessment.score,
            )
        )

        anomaly = AnomalyDetection(
            is_anomaly=anomaly_dict["is_anomaly"],
            z_score=anomaly_dict.get("z_score"),
            baseline_mean=anomaly_dict.get(
                "baseline_mean"
            ),
            direction=anomaly_dict.get("direction"),
            reason=anomaly_dict.get("reason"),
        )

        return assessment, anomaly, signals