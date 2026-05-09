"""add workflow id to mitigation plans

Revision ID: 7ac3d69cfcb3
Revises: 5c505dfc9040
Create Date: 2026-05-09 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "7ac3d69cfcb3"
down_revision = "5c505dfc9040"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "mitigation_plans",
        sa.Column("workflow_id", sa.String(length=128), nullable=True),
    )

    op.create_index(
        op.f("ix_mitigation_plans_workflow_id"),
        "mitigation_plans",
        ["workflow_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_mitigation_plans_workflow_id"),
        table_name="mitigation_plans",
    )

    op.drop_column("mitigation_plans", "workflow_id")