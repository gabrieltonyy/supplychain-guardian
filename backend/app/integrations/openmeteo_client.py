import json

import httpx

from app.integrations.signal_normalizer import (
    normalize_openmeteo_current,
)
from app.integrations.signal_types import NormalizedExternalSignal


class OpenMeteoClient:
    def __init__(
        self,
        base_url: str = "https://api.open-meteo.com/v1",
        timeout_seconds: float = 15.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def get_current_weather(
        self,
        latitude: float,
        longitude: float,
    ) -> dict:
        url = f"{self.base_url}/forecast"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "precipitation,"
                "wind_speed_10m"
            ),
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
                    "Open-Meteo returned non-JSON response. "
                    f"status={response.status_code}, "
                    f"preview={preview}"
                ) from exc

    async def get_weather_signal(
        self,
        supplier_id: str,
        latitude: float,
        longitude: float,
        country: str | None = None,
        region: str | None = None,
    ) -> NormalizedExternalSignal:
        payload = await self.get_current_weather(
            latitude=latitude,
            longitude=longitude,
        )

        return normalize_openmeteo_current(
            payload=payload,
            supplier_id=supplier_id,
            country=country,
            region=region,
        )


openmeteo_client = OpenMeteoClient()