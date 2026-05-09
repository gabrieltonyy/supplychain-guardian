"""add workflow events table

Revision ID: a446128c5a7a
Revises: 17057e0a38ea
Create Date: 2026-05-09 11:43:00.070936
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a446128c5a7a"
down_revision = "17057e0a38ea"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_events",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("workflow_id", sa.String(length=128), nullable=False),
        sa.Column("supplier_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("agent_name", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_workflow_events"),
        ),
    )

    op.create_index(
        op.f("ix_workflow_events_workflow_id"),
        "workflow_events",
        ["workflow_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_workflow_events_supplier_id"),
        "workflow_events",
        ["supplier_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_workflow_events_event_type"),
        "workflow_events",
        ["event_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_workflow_events_agent_name"),
        "workflow_events",
        ["agent_name"],
        unique=False,
    )

    op.create_index(
        op.f("ix_workflow_events_status"),
        "workflow_events",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_workflow_events_created_at"),
        "workflow_events",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_workflow_events_created_at"),
        table_name="workflow_events",
    )

    op.drop_index(
        op.f("ix_workflow_events_status"),
        table_name="workflow_events",
    )

    op.drop_index(
        op.f("ix_workflow_events_agent_name"),
        table_name="workflow_events",
    )

    op.drop_index(
        op.f("ix_workflow_events_event_type"),
        table_name="workflow_events",
    )

    op.drop_index(
        op.f("ix_workflow_events_supplier_id"),
        table_name="workflow_events",
    )

    op.drop_index(
        op.f("ix_workflow_events_workflow_id"),
        table_name="workflow_events",
    )

    op.drop_table("workflow_events")