from datetime import datetime, UTC
from typing import Any

from app.core.config import settings
from app.ingestion.base import BaseSignalFetcher
from app.schemas.signals import SignalEvent, SignalType


class LogisticsFetcher(BaseSignalFetcher):
    """
    Fetches logistics disruption indicators from
    ShipBob-style fulfillment/shipping APIs.
    """

    source_name = "shipbob"

    async def fetch(
        self,
        supplier_id: str,
        region: str,
        warehouse_id: str,
    ) -> SignalEvent:
        headers = {
            "Authorization": f"Bearer {settings.SHIPBOB_API_KEY}",
            "Content-Type": "application/json",
        }

        data = await self.get_json(
            f"{settings.SHIPBOB_BASE_URL}/inventory",
            headers=headers,
            params={
                "warehouse_id": warehouse_id,
            },
        )

        severity = self._calculate_logistics_severity(data)

        confidence = 1.0 if settings.SHIPBOB_API_KEY else 0.5

        return SignalEvent(
            signal_type=SignalType.LOGISTICS,
            supplier_id=supplier_id,
            region=region,
            severity=severity,
            confidence=confidence,
            raw_value=data,
            source=self.source_name,
            fetched_at=datetime.now(UTC),
        )

    def _calculate_logistics_severity(
        self,
        data: dict[str, Any],
    ) -> float:
        """
        Convert logistics operational issues into normalized severity.
        """

        disruptions = data.get("disruptions", [])
        delayed_shipments = data.get("delayed_shipments", 0)
        warehouse_utilization = data.get("warehouse_utilization_pct", 0)

        disruption_factor = min(len(disruptions) / 10, 1.0)

        shipment_factor = min(delayed_shipments / 100, 1.0)

        utilization_factor = min(
            max((warehouse_utilization - 70) / 30, 0),
            1.0,
        )

        severity = (
            disruption_factor * 0.4
            + shipment_factor * 0.35
            + utilization_factor * 0.25
        )

        return round(min(severity, 1.0), 3)