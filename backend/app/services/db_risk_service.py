from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.risk_history_repository import (
    RiskHistoryRepository,
)
from app.engine.scorer import compute_risk_score
from app.schemas.assessments import (
    AnomalyDetection,
    RiskAssessment,
)
from app.schemas.signals import (
    SignalEvent,
    SignalType,
)
from app.services.anomaly_detection_service import (
    AnomalyDetectionService,
)


class DbRiskService:
    """
    Database-backed Risk Analyst service.

    This service replaces fixed mock history with
    real seeded historical supplier risk scores.
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

    async def gather_seed_signals(
        self,
        supplier_id: str,
        region: str,
    ) -> list[SignalEvent]:
        """
        Seed-based signal generator.

        Later this becomes:
        - API ingestion
        - streaming Kafka events
        - live geopolitical feeds
        - weather integrations
        """

        if supplier_id == "SUP-CN-001":
            return [
                SignalEvent(
                    signal_type=SignalType.FINANCIAL,
                    supplier_id=supplier_id,
                    region=region,
                    severity=0.85,
                    confidence=0.95,
                    source="seed-finnhub",
                    raw_value={
                        "stock_proxy_change_pct": -17.0,
                        "credit_outlook": "negative",
                    },
                ),
                SignalEvent(
                    signal_type=SignalType.GEOPOLITICAL,
                    supplier_id=supplier_id,
                    region=region,
                    severity=0.75,
                    confidence=0.90,
                    source="seed-gdelt",
                    raw_value={
                        "articles": 42,
                        "keywords": [
                            "trade restriction",
                            "port congestion",
                            "electronics tariffs",
                        ],
                    },
                ),
                SignalEvent(
                    signal_type=SignalType.LOGISTICS,
                    supplier_id=supplier_id,
                    region=region,
                    severity=0.60,
                    confidence=0.88,
                    source="seed-shipbob",
                    raw_value={
                        "delayed_shipments_pct": 38,
                        "warehouse_utilization_pct": 92,
                    },
                ),
            ]

        if supplier_id == "SUP-DE-001":
            return [
                SignalEvent(
                    signal_type=SignalType.FINANCIAL,
                    supplier_id=supplier_id,
                    region=region,
                    severity=0.18,
                    confidence=0.97,
                    source="seed-finnhub",
                    raw_value={
                        "stock_proxy_change_pct": 3.2,
                        "credit_outlook": "stable",
                    },
                ),
                SignalEvent(
                    signal_type=SignalType.LOGISTICS,
                    supplier_id=supplier_id,
                    region=region,
                    severity=0.12,
                    confidence=0.95,
                    source="seed-shipbob",
                    raw_value={
                        "delayed_shipments_pct": 4,
                        "warehouse_utilization_pct": 55,
                    },
                ),
            ]

        if supplier_id == "SUP-IN-001":
            return [
                SignalEvent(
                    signal_type=SignalType.WEATHER,
                    supplier_id=supplier_id,
                    region=region,
                    severity=0.40,
                    confidence=0.91,
                    source="seed-open-meteo",
                    raw_value={
                        "flood_risk": "moderate",
                        "rainfall_mm": 82,
                    },
                ),
                SignalEvent(
                    signal_type=SignalType.FINANCIAL,
                    supplier_id=supplier_id,
                    region=region,
                    severity=0.35,
                    confidence=0.92,
                    source="seed-finnhub",
                    raw_value={
                        "supplier_growth_pct": 4.8,
                    },
                ),
            ]

        if supplier_id == "SUP-VN-001":
            return [
                SignalEvent(
                    signal_type=SignalType.WEATHER,
                    supplier_id=supplier_id,
                    region=region,
                    severity=0.72,
                    confidence=0.94,
                    source="seed-open-meteo",
                    raw_value={
                        "storm_alert": True,
                        "flood_risk": "high",
                    },
                ),
                SignalEvent(
                    signal_type=SignalType.LOGISTICS,
                    supplier_id=supplier_id,
                    region=region,
                    severity=0.58,
                    confidence=0.90,
                    source="seed-shipbob",
                    raw_value={
                        "port_delay_days": 5,
                    },
                ),
            ]

        if supplier_id == "SUP-RU-001":
            return [
                SignalEvent(
                    signal_type=SignalType.GEOPOLITICAL,
                    supplier_id=supplier_id,
                    region=region,
                    severity=0.95,
                    confidence=0.99,
                    source="seed-gdelt",
                    raw_value={
                        "sanctions_articles": 140,
                        "keywords": [
                            "trade sanctions",
                            "restricted exports",
                        ],
                    },
                ),
                SignalEvent(
                    signal_type=SignalType.TARIFF,
                    supplier_id=supplier_id,
                    region=region,
                    severity=0.80,
                    confidence=0.95,
                    source="seed-wits",
                    raw_value={
                        "tariff_change_pct": 25,
                    },
                ),
            ]

        if supplier_id == "SUP-IR-001":
            return [
                SignalEvent(
                    signal_type=SignalType.GEOPOLITICAL,
                    supplier_id=supplier_id,
                    region=region,
                    severity=1.0,
                    confidence=1.0,
                    source="seed-gdelt",
                    raw_value={
                        "sanctions_status": "blocked",
                    },
                ),
            ]

        return [
            SignalEvent(
                signal_type=SignalType.FINANCIAL,
                supplier_id=supplier_id,
                region=region,
                severity=0.20,
                confidence=0.90,
                source="seed-default",
                raw_value={
                    "note": "default low-risk seeded signal",
                },
            )
        ]

    async def assess_supplier_risk(
        self,
        supplier_id: str,
        region: str,
    ) -> tuple[
        RiskAssessment,
        AnomalyDetection,
        list[SignalEvent],
    ]:
        """
        Run DB-backed risk assessment.
        """

        signals = await self.gather_seed_signals(
            supplier_id=supplier_id,
            region=region,
        )

        assessment = compute_risk_score(signals)

        anomaly_dict = (
            await self.anomaly_service.detect_supplier_anomaly(
                supplier_id=supplier_id,
                current_score=assessment.score,
            )
        )

        anomaly = AnomalyDetection(
            is_anomaly=anomaly_dict["is_anomaly"],
            z_score=anomaly_dict.get("z_score"),
            baseline_mean=anomaly_dict.get("baseline_mean"),
            direction=anomaly_dict.get("direction"),
            reason=anomaly_dict.get("reason"),
        )

        return assessment, anomaly, signals