from datetime import datetime
from enum import Enum

from pydantic import Field

from app.schemas.common import BaseSchema


class RiskLevel(str, Enum):
    """
    Supplier risk classification.
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskAssessment(BaseSchema):
    """
    Final computed supplier risk assessment.
    """

    supplier_id: str

    score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Composite risk score (0–100)",
    )

    level: RiskLevel

    factor_breakdown: dict[str, float] = Field(
        default_factory=dict,
        description="Per-signal-type contribution scores",
    )

    contributing_signals: list[str] = Field(
        default_factory=list,
        description="External signal sources used",
    )

    assessed_at: datetime = Field(
        default_factory=datetime.utcnow
    )


class AnomalyDetection(BaseSchema):
    """
    Statistical anomaly analysis result.
    """

    is_anomaly: bool

    z_score: float | None = None

    baseline_mean: float | None = None

    direction: str | None = Field(
        default=None,
        description="spike or drop",
    )

    reason: str | None = None


class RiskAssessmentRecord(BaseSchema):
    """
    Combined assessment + anomaly + reasoning payload.
    Used for persistence and agent state passing.
    """

    assessment: RiskAssessment

    anomaly_detection: AnomalyDetection

    reasoning_summary: str

    generated_at: datetime = Field(
        default_factory=datetime.utcnow
    )