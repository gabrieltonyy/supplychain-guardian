"""add workflow id to compliance audit logs

Revision ID: 394a6ce7dd20
Revises: 2c4e4b7a9f3f
Create Date: 2026-05-09 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "394a6ce7dd20"
down_revision = "2c4e4b7a9f3f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "compliance_audit_logs",
        sa.Column("workflow_id", sa.String(length=128), nullable=True),
    )

    op.create_index(
        op.f("ix_compliance_audit_logs_workflow_id"),
        "compliance_audit_logs",
        ["workflow_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_compliance_audit_logs_workflow_id"),
        table_name="compliance_audit_logs",
    )

    op.drop_column("compliance_audit_logs", "workflow_id")