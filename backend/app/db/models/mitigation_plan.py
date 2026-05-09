from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MitigationPlanRecord(Base):
    """
    Persisted mitigation strategy generated
    by the Mitigation Strategist Agent.
    """

    __tablename__ = "mitigation_plans"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    workflow_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    original_supplier_id: Mapped[str] = mapped_column(
        ForeignKey("suppliers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    recommended_options: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    candidate_suppliers: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    simulated_scenarios: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    justification: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_by_agent: Mapped[str] = mapped_column(
        String(120),
        default="mitigation_strategist",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )