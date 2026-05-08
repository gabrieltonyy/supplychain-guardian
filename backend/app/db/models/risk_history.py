import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SupplierRiskHistory(Base):
    """
    Historical risk scores used for anomaly detection
    and trend analysis.
    """

    __tablename__ = "supplier_risk_history"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    supplier_id: Mapped[str] = mapped_column(
        ForeignKey("suppliers.id"),
        nullable=False,
        index=True,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )