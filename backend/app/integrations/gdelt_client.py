import json

import httpx

from app.integrations.signal_normalizer import normalize_gdelt_article
from app.integrations.signal_types import NormalizedExternalSignal


class GdeltClient:
    def __init__(
        self,
        base_url: str = "https://api.gdeltproject.org/api/v2",
        timeout_seconds: float = 15.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def search_articles(
        self,
        query: str,
        max_records: int = 5,
    ) -> dict:
        url = f"{self.base_url}/doc/doc"

        params = {
            "query": query,
            "mode": "artlist",
            "maxrecords": max_records,
            "format": "json",
        }

        async with httpx.AsyncClient(
            timeout=self.timeout_seconds,
            follow_redirects=True,
        ) as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    "User-Agent": "SupplyChainGuardian/1.0",
                    "Accept": "application/json",
                },
            )

            if response.status_code == 429:
                return {
                    "articles": [],
                    "rate_limited": True,
                }

            response.raise_for_status()

            try:
                return response.json()

            except json.JSONDecodeError as exc:
                preview = response.text[:300]

                raise ValueError(
                    "GDELT returned non-JSON response. "
                    f"status={response.status_code}, "
                    f"preview={preview}"
                ) from exc

    async def get_geopolitical_signals(
        self,
        supplier_id: str,
        country: str,
        keywords: list[str] | None = None,
        max_records: int = 5,
    ) -> list[NormalizedExternalSignal]:
        search_keywords = keywords or [
            "supply chain",
            "export restrictions",
            "port disruption",
            "strike",
            "sanctions",
        ]

        signals: list[NormalizedExternalSignal] = []

        for keyword in search_keywords:
            query = f"{country} {keyword}"

            payload = await self.search_articles(
                query=query,
                max_records=max_records,
            )

            if payload.get("rate_limited"):
                break

            articles = payload.get("articles", [])

            for article in articles:
                signals.append(
                    normalize_gdelt_article(
                        article=article,
                        supplier_id=supplier_id,
                        country=country,
                    )
                )

            if signals:
                break

        return signals[:max_records]


gdelt_client = GdeltClient()