import asyncio

from app.engine.anomaly import detect_anomaly
from app.engine.scorer import compute_risk_score
from app.ingestion.financial_fetcher import FinancialFetcher
from app.ingestion.geopolitical_fetcher import GeopoliticalFetcher
from app.ingestion.logistics_fetcher import LogisticsFetcher
from app.ingestion.tariff_fetcher import TariffFetcher
from app.ingestion.weather_fetcher import WeatherFetcher
from app.schemas.assessments import AnomalyDetection, RiskAssessment
from app.schemas.signals import SignalEvent


class RiskService:
    """
    Coordinates signal gathering, risk scoring,
    anomaly detection, and persistence hooks.
    """

    def __init__(self) -> None:
        self.weather_fetcher = WeatherFetcher()
        self.geopolitical_fetcher = GeopoliticalFetcher()
        self.financial_fetcher = FinancialFetcher()
        self.logistics_fetcher = LogisticsFetcher()
        self.tariff_fetcher = TariffFetcher()

    async def gather_mock_signals(
        self,
        supplier_id: str,
        region: str,
    ) -> list[SignalEvent]:
        """
        MVP-safe mock signal gatherer.

        This allows us to test the full Risk Analyst pipeline
        before wiring live external APIs and supplier metadata.
        """

        return [
            SignalEvent(
                signal_type="financial",
                supplier_id=supplier_id,
                region=region,
                severity=0.85,
                confidence=0.95,
                source="mock-finnhub",
                raw_value={"dp": -17},
            ),
            SignalEvent(
                signal_type="geopolitical",
                supplier_id=supplier_id,
                region=region,
                severity=0.75,
                confidence=0.90,
                source="mock-gdelt",
                raw_value={"articles": 40},
            ),
            SignalEvent(
                signal_type="logistics",
                supplier_id=supplier_id,
                region=region,
                severity=0.60,
                confidence=0.88,
                source="mock-shipbob",
                raw_value={"delayed_shipments": 60},
            ),
            SignalEvent(
                signal_type="weather",
                supplier_id=supplier_id,
                region=region,
                severity=0.45,
                confidence=1.00,
                source="mock-open-meteo",
                raw_value={"precipitation_sum": 45},
            ),
            SignalEvent(
                signal_type="tariff",
                supplier_id=supplier_id,
                region=region,
                severity=0.30,
                confidence=0.85,
                source="mock-wits",
                raw_value={"tariff_rate_pct": 15},
            ),
        ]

    async def gather_live_signals(
        self,
        supplier_context: dict,
    ) -> list[SignalEvent]:
        """
        Gather live external signals concurrently.

        Expected supplier_context fields:
        - supplier_id
        - region
        - lat
        - lon
        - geopolitical_query
        - financial_symbol
        - warehouse_id
        - reporter_country
        - partner_country
        - product_code
        """

        tasks = [
            self.weather_fetcher.fetch(
                lat=supplier_context["lat"],
                lon=supplier_context["lon"],
                supplier_id=supplier_context["supplier_id"],
                region=supplier_context["region"],
            ),
            self.geopolitical_fetcher.fetch(
                supplier_id=supplier_context["supplier_id"],
                region=supplier_context["region"],
                query=supplier_context["geopolitical_query"],
            ),
            self.financial_fetcher.fetch(
                supplier_id=supplier_context["supplier_id"],
                region=supplier_context["region"],
                symbol=supplier_context["financial_symbol"],
            ),
            self.logistics_fetcher.fetch(
                supplier_id=supplier_context["supplier_id"],
                region=supplier_context["region"],
                warehouse_id=supplier_context["warehouse_id"],
            ),
            self.tariff_fetcher.fetch(
                supplier_id=supplier_context["supplier_id"],
                region=supplier_context["region"],
                reporter_country=supplier_context["reporter_country"],
                partner_country=supplier_context["partner_country"],
                product_code=supplier_context["product_code"],
            ),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        signals: list[SignalEvent] = []

        for result in results:
            if isinstance(result, Exception):
                continue

            signals.append(result)

        return signals

    async def assess_supplier_risk(
        self,
        supplier_id: str,
        region: str,
        history: list[float] | None = None,
        use_mock_data: bool = True,
    ) -> tuple[RiskAssessment, AnomalyDetection, list[SignalEvent]]:
        """
        Main risk assessment workflow.
        """

        if use_mock_data:
            signals = await self.gather_mock_signals(
                supplier_id=supplier_id,
                region=region,
            )
        else:
            raise NotImplementedError(
                "Live supplier context lookup will be implemented after supplier service"
            )

        assessment = compute_risk_score(signals)

        anomaly = detect_anomaly(
            current_score=assessment.score,
            history=history or [],
        )

        return assessment, anomaly, signals


risk_service = RiskService()