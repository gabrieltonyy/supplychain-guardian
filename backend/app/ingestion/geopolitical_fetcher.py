from datetime import UTC, datetime
from typing import Any

from app.ingestion.base import BaseSignalFetcher
from app.integrations.gdelt_client import gdelt_client
from app.schemas.signals import SignalEvent, SignalType


class GeopoliticalFetcher(BaseSignalFetcher):
    source_name = "gdelt"

    async def fetch(
        self,
        supplier_id: str,
        region: str,
        query: str,
    ) -> SignalEvent:
        data = await gdelt_client.search_articles(
            query=query,
            max_records=50,
        )

        severity = self._calculate_geopolitical_severity(data)

        confidence = 0.5 if data.get("rate_limited") else 0.9

        return SignalEvent(
            signal_type=SignalType.GEOPOLITICAL,
            supplier_id=supplier_id,
            region=region,
            severity=severity,
            confidence=confidence,
            raw_value=data,
            source=self.source_name,
            fetched_at=datetime.now(UTC),
        )

    def _calculate_geopolitical_severity(
        self,
        data: dict[str, Any],
    ) -> float:
        if data.get("rate_limited"):
            return 0.0

        articles = data.get("articles", [])

        if not articles:
            return 0.0

        tension_keywords = [
            "war",
            "conflict",
            "sanction",
            "protest",
            "military",
            "attack",
            "trade restriction",
            "tariff",
            "embargo",
            "export control",
            "restriction",
            "strike",
            "shutdown",
        ]

        keyword_hits = 0

        for article in articles:
            title = (article.get("title") or "").lower()

            if any(keyword in title for keyword in tension_keywords):
                keyword_hits += 1

        article_factor = min(len(articles) / 50, 1.0)
        tension_factor = min(keyword_hits / len(articles), 1.0)

        severity = (article_factor * 0.4) + (tension_factor * 0.6)

        return round(min(severity, 1.0), 3)


geopolitical_fetcher = GeopoliticalFetcher()