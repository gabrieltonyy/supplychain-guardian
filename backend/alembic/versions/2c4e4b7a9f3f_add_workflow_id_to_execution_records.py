"""add workflow id to execution records

Revision ID: 2c4e4b7a9f3f
Revises: 7ac3d69cfcb3
Create Date: 2026-05-09 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "2c4e4b7a9f3f"
down_revision = "7ac3d69cfcb3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "execution_records",
        sa.Column("workflow_id", sa.String(length=128), nullable=True),
    )

    op.create_index(
        op.f("ix_execution_records_workflow_id"),
        "execution_records",
        ["workflow_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_execution_records_workflow_id"),
        table_name="execution_records",
    )

    op.drop_column("execution_records", "workflow_id")