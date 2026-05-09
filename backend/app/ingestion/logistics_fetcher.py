from datetime import UTC, datetime
from typing import Any

from app.ingestion.base import BaseSignalFetcher
from app.integrations.shipbob_client import shipbob_client
from app.schemas.signals import SignalEvent, SignalType


class LogisticsFetcher(BaseSignalFetcher):
    source_name = "shipbob"

    async def fetch(
        self,
        supplier_id: str,
        region: str,
        warehouse_id: str | None = None,
    ) -> SignalEvent:
        _ = warehouse_id

        data = await shipbob_client.get_channel()

        severity = self._calculate_logistics_severity(data)

        return SignalEvent(
            signal_type=SignalType.LOGISTICS,
            supplier_id=supplier_id,
            region=region,
            severity=severity,
            confidence=0.85 if not data.get("error") else 0.4,
            raw_value=data,
            source=self.source_name,
            fetched_at=datetime.now(UTC),
        )

    def _calculate_logistics_severity(
        self,
        data: dict[str, Any],
    ) -> float:
        if data.get("error"):
            return 0.5

        items = data.get("items", [])

        if not items:
            return 0.2

        return 0.0


logistics_fetcher = LogisticsFetcher()