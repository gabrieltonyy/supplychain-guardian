"""add created_by_agent to compliance audit logs

Revision ID: 17057e0a38ea
Revises: 394a6ce7dd20
Create Date: 2026-05-09 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "17057e0a38ea"
down_revision = "394a6ce7dd20"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "compliance_audit_logs",
        sa.Column(
            "created_by_agent",
            sa.String(length=120),
            nullable=False,
            server_default="compliance_agent",
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "compliance_audit_logs",
        "created_by_agent",
    )