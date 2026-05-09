from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ExternalSignalSource(str, Enum):
    FINNHUB = "finnhub"
    GDELT = "gdelt"
    OPEN_METEO = "open_meteo"
    SHIPBOB = "shipbob"


class ExternalSignalType(str, Enum):
    FINANCIAL = "financial"
    GEOPOLITICAL = "geopolitical"
    WEATHER = "weather"
    LOGISTICS = "logistics"


class NormalizedExternalSignal(BaseModel):
    supplier_id: str | None = None
    source: ExternalSignalSource
    signal_type: ExternalSignalType

    severity: float = Field(
        ...,
        ge=0.0,
        le=100.0,
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    title: str
    summary: str | None = None

    country: str | None = None
    region: str | None = None

    raw_payload: dict[str, Any] = Field(default_factory=dict)

    observed_at: datetime = Field(default_factory=datetime.utcnow)