from datetime import UTC, datetime
from typing import Any

from app.ingestion.base import BaseSignalFetcher
from app.integrations.finnhub_client import finnhub_client
from app.schemas.signals import SignalEvent, SignalType


class FinancialFetcher(BaseSignalFetcher):
    source_name = "finnhub"

    async def fetch(
        self,
        supplier_id: str,
        region: str,
        symbol: str,
    ) -> SignalEvent:
        data = await finnhub_client.get_quote(symbol=symbol)

        severity = self._calculate_financial_severity(data)

        return SignalEvent(
            signal_type=SignalType.FINANCIAL,
            supplier_id=supplier_id,
            region=region,
            severity=severity,
            confidence=1.0,
            raw_value=data,
            source=self.source_name,
            fetched_at=datetime.now(UTC),
        )

    def _calculate_financial_severity(
        self,
        data: dict[str, Any],
    ) -> float:
        percent_change = data.get("dp")

        if percent_change is None:
            return 0.3

        if percent_change >= 0:
            return 0.1

        decline = abs(float(percent_change))

        if decline >= 20:
            return 1.0

        return round(min(decline / 20, 1.0), 3)


financial_fetcher = FinancialFetcher()