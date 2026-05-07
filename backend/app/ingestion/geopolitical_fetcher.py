from datetime import datetime, UTC
from typing import Any

from app.core.config import settings
from app.ingestion.base import BaseSignalFetcher
from app.schemas.signals import SignalEvent, SignalType


class GeopoliticalFetcher(BaseSignalFetcher):
    """
    Fetches geopolitical instability indicators
    from GDELT-style event feeds.
    """

    source_name = "gdelt"

    async def fetch(
        self,
        supplier_id: str,
        region: str,
        query: str,
    ) -> SignalEvent:
        params = {
            "query": query,
            "mode": "ArtList",
            "maxrecords": 50,
            "format": "json",
        }

        data = await self.get_json(
            f"{settings.GDELT_BASE_URL}/doc/doc",
            params=params,
        )

        severity = self._calculate_geopolitical_severity(data)

        return SignalEvent(
            signal_type=SignalType.GEOPOLITICAL,
            supplier_id=supplier_id,
            region=region,
            severity=severity,
            confidence=0.9,
            raw_value=data,
            source=self.source_name,
            fetched_at=datetime.now(UTC),
        )

    def _calculate_geopolitical_severity(
        self,
        data: dict[str, Any],
    ) -> float:
        """
        Convert geopolitical activity into a normalized risk score.
        """

        articles = data.get("articles", [])

        if not articles:
            return 0.0

        article_count = len(articles)

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
        ]

        keyword_hits = 0

        for article in articles:
            title = (article.get("title") or "").lower()

            if any(keyword in title for keyword in tension_keywords):
                keyword_hits += 1

        article_factor = min(article_count / 50, 1.0)
        tension_factor = min(keyword_hits / article_count, 1.0)

        severity = (article_factor * 0.4) + (tension_factor * 0.6)

        return round(min(severity, 1.0), 3)