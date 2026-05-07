from datetime import datetime, UTC
from typing import Any

from app.core.config import settings
from app.ingestion.base import BaseSignalFetcher
from app.schemas.signals import SignalEvent, SignalType


class FinancialFetcher(BaseSignalFetcher):
    """
    Fetches financial health indicators for supplier-linked companies.
    Uses Finnhub-style company quote data.
    """

    source_name = "finnhub"

    async def fetch(
        self,
        supplier_id: str,
        region: str,
        symbol: str,
    ) -> SignalEvent:
        params = {
            "symbol": symbol,
            "token": settings.FINNHUB_API_KEY,
        }

        data = await self.get_json(
            f"{settings.FINNHUB_BASE_URL}/quote",
            params=params,
        )

        severity = self._calculate_financial_severity(data)

        confidence = 1.0 if settings.FINNHUB_API_KEY else 0.5

        return SignalEvent(
            signal_type=SignalType.FINANCIAL,
            supplier_id=supplier_id,
            region=region,
            severity=severity,
            confidence=confidence,
            raw_value=data,
            source=self.source_name,
            fetched_at=datetime.now(UTC),
        )

    def _calculate_financial_severity(
        self,
        data: dict[str, Any],
    ) -> float:
        """
        Convert stock movement into financial risk severity.

        Finnhub quote fields:
        c  = current price
        pc = previous close
        dp = percent change
        """

        percent_change = data.get("dp")

        if percent_change is None:
            return 0.3

        # Negative price movement increases supplier financial risk.
        if percent_change >= 0:
            return 0.1

        decline = abs(float(percent_change))

        if decline >= 20:
            return 1.0

        severity = decline / 20

        return round(min(severity, 1.0), 3)