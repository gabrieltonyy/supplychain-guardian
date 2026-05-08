from datetime import datetime, UTC
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    Enum,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.schemas.compliance import ComplianceVerdict


class ComplianceAuditLog(Base):
    """
    Immutable compliance audit log.

    Application rule:
    - insert only
    - no update/delete methods should be created for this table
    """

    __tablename__ = "compliance_audit_logs"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    log_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
        index=True,
    )

    workflow_run_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    agent_id: Mapped[str] = mapped_column(
        String(120),
        default="compliance_agent",
        nullable=False,
    )

    agent_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    execution_record_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    input_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    sanctions_results: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    regulatory_results: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    verdict: Mapped[ComplianceVerdict] = mapped_column(
        Enum(ComplianceVerdict),
        nullable=False,
        index=True,
    )

    verdict_rationale: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    llm_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )