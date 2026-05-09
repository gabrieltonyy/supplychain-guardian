from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WorkflowEvent(Base):
    """
    Durable workflow timeline event.
    Used for replay, debugging, auditability, and observability.
    """

    __tablename__ = "workflow_events"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    workflow_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    supplier_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        index=True,
    )

    agent_name: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        index=True,
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    payload: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )