from datetime import UTC, datetime
from typing import Any

from app.ingestion.base import BaseSignalFetcher
from app.integrations.openmeteo_client import openmeteo_client
from app.schemas.signals import SignalEvent, SignalType


class WeatherFetcher(BaseSignalFetcher):
    source_name = "open-meteo"

    async def fetch(
        self,
        lat: float,
        lon: float,
        supplier_id: str,
        region: str,
    ) -> SignalEvent:
        data = await openmeteo_client.get_current_weather(
            latitude=lat,
            longitude=lon,
        )

        severity = self._calculate_weather_severity(data)

        return SignalEvent(
            signal_type=SignalType.WEATHER,
            supplier_id=supplier_id,
            region=region,
            severity=severity,
            confidence=1.0,
            raw_value=data,
            source=self.source_name,
            fetched_at=datetime.now(UTC),
        )

    def _calculate_weather_severity(
        self,
        data: dict[str, Any],
    ) -> float:
        current = data.get("current", {})

        precipitation = float(current.get("precipitation") or 0)
        wind_speed = float(current.get("wind_speed_10m") or 0)
        temperature = float(current.get("temperature_2m") or 0)

        precipitation_score = min(precipitation / 20, 1.0)
        wind_score = min(wind_speed / 60, 1.0)

        temperature_score = 0.0
        if temperature >= 40 or temperature <= -5:
            temperature_score = 1.0

        severity = (
            precipitation_score * 0.45
            + wind_score * 0.4
            + temperature_score * 0.15
        )

        return round(min(severity, 1.0), 3)


weather_fetcher = WeatherFetcher()