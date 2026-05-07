from datetime import datetime, UTC
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    JSON,
    String,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RiskWeightConfig(Base):
    """
    Configurable weights for supplier risk scoring.
    Used by Risk Analyst Agent.
    """

    __tablename__ = "risk_weight_configs"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    financial_weight: Mapped[float] = mapped_column(
        Float,
        default=0.30,
        nullable=False,
    )

    geopolitical_weight: Mapped[float] = mapped_column(
        Float,
        default=0.25,
        nullable=False,
    )

    logistics_weight: Mapped[float] = mapped_column(
        Float,
        default=0.20,
        nullable=False,
    )

    weather_weight: Mapped[float] = mapped_column(
        Float,
        default=0.15,
        nullable=False,
    )

    tariff_weight: Mapped[float] = mapped_column(
        Float,
        default=0.10,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


class MitigationWeightConfig(Base):
    """
    Configurable TOPSIS ranking weights.
    Used by Mitigation Strategist Agent.
    """

    __tablename__ = "mitigation_weight_configs"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    cost_delta_weight: Mapped[float] = mapped_column(
        Float,
        default=0.30,
        nullable=False,
    )

    lead_time_weight: Mapped[float] = mapped_column(
        Float,
        default=0.25,
        nullable=False,
    )

    residual_risk_weight: Mapped[float] = mapped_column(
        Float,
        default=0.25,
        nullable=False,
    )

    onboarding_weight: Mapped[float] = mapped_column(
        Float,
        default=0.10,
        nullable=False,
    )

    confidence_weight: Mapped[float] = mapped_column(
        Float,
        default=0.10,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


class SystemConfig(Base):
    """
    Generic system configuration store.
    Used for feature flags, thresholds, and runtime tuning.
    """

    __tablename__ = "system_configs"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    config_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    config_value: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=lambda: datetime.now(UTC),
    )