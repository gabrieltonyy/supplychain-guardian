from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field

from app.schemas.common import BaseSchema


class SignalType(str, Enum):
    """
    Types of external risk signals.
    """

    WEATHER = "weather"
    GEOPOLITICAL = "geopolitical"
    FINANCIAL = "financial"
    LOGISTICS = "logistics"
    TARIFF = "tariff"


class SignalSource(str, Enum):
    """
    External provider/source identifiers.
    """

    OPEN_METEO = "open-meteo"
    GDELT = "gdelt"
    FINNHUB = "finnhub"
    SHIPBOB = "shipbob"
    WITS = "world-bank-wits"


class SignalEvent(BaseSchema):
    """
    Normalized external signal event.

    All ingestion fetchers must emit this schema.
    """

    signal_type: SignalType

    supplier_id: str
    region: str

    severity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized severity score (0.0–1.0)",
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence level of the signal",
    )

    source: str

    raw_value: dict[str, Any] = Field(
        default_factory=dict,
        description="Original provider payload for auditability",
    )

    fetched_at: datetime = Field(
        default_factory=datetime.utcnow
    )


class SignalBatch(BaseSchema):
    """
    Batch of supplier signals.
    """

    supplier_id: str
    signals: list[SignalEvent]
    generated_at: datetime = Field(
        default_factory=datetime.utcnow
    )