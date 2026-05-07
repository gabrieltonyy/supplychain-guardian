from datetime import datetime, UTC
from typing import Any

from app.core.config import settings
from app.ingestion.base import BaseSignalFetcher
from app.schemas.signals import SignalEvent, SignalType


class TariffFetcher(BaseSignalFetcher):
    """
    Fetches tariff/trade restriction indicators
    from World Bank WITS-style trade APIs.
    """

    source_name = "world-bank-wits"

    async def fetch(
        self,
        supplier_id: str,
        region: str,
        reporter_country: str,
        partner_country: str,
        product_code: str,
    ) -> SignalEvent:
        params = {
            "reporter": reporter_country,
            "partner": partner_country,
            "product": product_code,
        }

        data = await self.get_json(
            settings.WITS_BASE_URL,
            params=params,
        )

        severity = self._calculate_tariff_severity(data)

        return SignalEvent(
            signal_type=SignalType.TARIFF,
            supplier_id=supplier_id,
            region=region,
            severity=severity,
            confidence=0.85,
            raw_value=data,
            source=self.source_name,
            fetched_at=datetime.now(UTC),
        )

    def _calculate_tariff_severity(
        self,
        data: dict[str, Any],
    ) -> float:
        """
        Convert tariff/trade restriction metrics into normalized severity.
        """

        tariff_rate = float(data.get("tariff_rate_pct", 0))
        restriction_count = int(data.get("trade_restrictions", 0))

        tariff_factor = min(tariff_rate / 50, 1.0)

        restriction_factor = min(restriction_count / 10, 1.0)

        severity = (
            tariff_factor * 0.7
            + restriction_factor * 0.3
        )

        return round(min(severity, 1.0), 3)