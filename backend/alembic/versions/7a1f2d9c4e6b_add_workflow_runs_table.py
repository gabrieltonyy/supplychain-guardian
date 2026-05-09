"""add workflow runs table

Revision ID: 7a1f2d9c4e6b
Revises: f16030eddb4c
Create Date: 2026-05-08 20:05:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7a1f2d9c4e6b"
down_revision = "f16030eddb4c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_runs",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("workflow_id", sa.String(length=128), nullable=False),
        sa.Column("supplier_id", sa.String(length=64), nullable=False),
        sa.Column("workflow_status", sa.String(length=64), nullable=False),
        sa.Column("correlation_id", sa.String(length=128), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("final_state_snapshot", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_workflow_runs"),
        ),
    )

    op.create_index(
        op.f("ix_workflow_runs_correlation_id"),
        "workflow_runs",
        ["correlation_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_workflow_runs_supplier_id"),
        "workflow_runs",
        ["supplier_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_workflow_runs_workflow_id"),
        "workflow_runs",
        ["workflow_id"],
        unique=True,
    )

    op.create_index(
        op.f("ix_workflow_runs_workflow_status"),
        "workflow_runs",
        ["workflow_status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_workflow_runs_workflow_status"),
        table_name="workflow_runs",
    )

    op.drop_index(
        op.f("ix_workflow_runs_workflow_id"),
        table_name="workflow_runs",
    )

    op.drop_index(
        op.f("ix_workflow_runs_supplier_id"),
        table_name="workflow_runs",
    )

    op.drop_index(
        op.f("ix_workflow_runs_correlation_id"),
        table_name="workflow_runs",
    )

    op.drop_table("workflow_runs")