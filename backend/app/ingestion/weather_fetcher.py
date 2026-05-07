from datetime import datetime, UTC
from typing import Any

from app.core.config import settings
from app.ingestion.base import BaseSignalFetcher
from app.schemas.signals import SignalEvent, SignalType


class WeatherFetcher(BaseSignalFetcher):
    """
    Fetches weather forecast data and converts it into
    normalized supplier risk signals.
    """

    source_name = "open-meteo"

    async def fetch(
        self,
        lat: float,
        lon: float,
        supplier_id: str,
        region: str,
    ) -> SignalEvent:
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "weathercode,precipitation_sum,windspeed_10m_max",
            "forecast_days": 7,
            "timezone": "UTC",
        }

        data = await self.get_json(
            settings.OPEN_METEO_BASE_URL,
            params=params,
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
        """
        Convert weather forecast values into a 0.0–1.0 risk severity.
        """

        daily = data.get("daily", {})

        precipitation_values = daily.get("precipitation_sum", []) or [0]
        wind_values = daily.get("windspeed_10m_max", []) or [0]

        max_precip = max(precipitation_values)
        max_wind = max(wind_values)

        precipitation_score = min(max_precip / 100, 1.0)
        wind_score = min(max_wind / 120, 1.0)

        severity = (precipitation_score * 0.6) + (wind_score * 0.4)

        return round(min(severity, 1.0), 3)