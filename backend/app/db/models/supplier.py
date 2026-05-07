from datetime import datetime, UTC
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.schemas.suppliers import (
    ComplianceStatus,
    RelationshipStatus,
    SupplierStatus,
)


class Supplier(Base):
    """
    Supplier master record.
    Used by all agents during discovery,
    simulation, execution, and monitoring.
    """

    __tablename__ = "suppliers"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    country: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        index=True,
    )

    region: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        index=True,
    )

    contact_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    product_categories: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=list,
    )

    certifications: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=list,
    )

    status: Mapped[SupplierStatus] = mapped_column(
        Enum(SupplierStatus),
        default=SupplierStatus.ACTIVE,
        nullable=False,
    )

    compliance_status: Mapped[ComplianceStatus] = mapped_column(
        Enum(ComplianceStatus),
        default=ComplianceStatus.APPROVED,
        nullable=False,
    )

    relationship_status: Mapped[RelationshipStatus] = mapped_column(
        Enum(RelationshipStatus),
        default=RelationshipStatus.NEW,
        nullable=False,
    )

    unit_cost: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    typical_lead_time_days: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    capacity_units_per_month: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    on_time_delivery_rate: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    quality_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    latest_risk_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    supplier_profile_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    embedding_refreshed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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