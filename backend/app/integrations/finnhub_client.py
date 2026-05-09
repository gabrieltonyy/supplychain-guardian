import json
import os

import httpx

from app.integrations.signal_normalizer import normalize_finnhub_quote
from app.integrations.signal_types import NormalizedExternalSignal


class FinnhubClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_seconds: float = 15.0,
    ):
        self.api_key = api_key or os.getenv("FINNHUB_API_KEY")
        self.base_url = (
            base_url
            or os.getenv("FINNHUB_BASE_URL")
            or "https://finnhub.io/api/v1"
        ).rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def get_quote(
        self,
        symbol: str,
    ) -> dict:
        if not self.api_key:
            raise ValueError("FINNHUB_API_KEY is not configured")

        url = f"{self.base_url}/quote"

        params = {
            "symbol": symbol,
            "token": self.api_key,
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

            response.raise_for_status()

            try:
                return response.json()

            except json.JSONDecodeError as exc:
                preview = response.text[:300]
                raise ValueError(
                    "Finnhub returned non-JSON response. "
                    f"status={response.status_code}, "
                    f"preview={preview}"
                ) from exc

    async def get_financial_signal(
        self,
        supplier_id: str,
        symbol: str,
    ) -> NormalizedExternalSignal:
        payload = await self.get_quote(symbol=symbol)

        return normalize_finnhub_quote(
            payload=payload,
            supplier_id=supplier_id,
            symbol=symbol,
        )


finnhub_client = FinnhubClient()