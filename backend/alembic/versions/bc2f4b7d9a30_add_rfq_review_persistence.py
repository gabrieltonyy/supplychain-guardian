"""add rfq review persistence

Revision ID: bc2f4b7d9a30
Revises: 0f5cb9ef7641
Create Date: 2026-05-10 08:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "bc2f4b7d9a30"
down_revision = "0f5cb9ef7641"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for value in (
        "PENDING_APPROVAL",
        "APPROVED",
        "REVIEW_REQUESTED",
        "REJECTED",
        "COMPLIANCE_REVIEW",
    ):
        op.execute(f"ALTER TYPE rfqstatus ADD VALUE IF NOT EXISTS '{value}'")

    op.add_column("rfqs", sa.Column("supplier_code", sa.String(length=64), nullable=True))
    op.add_column("rfqs", sa.Column("workflow_id", sa.String(length=128), nullable=True))
    op.add_column("rfqs", sa.Column("price", sa.Float(), nullable=True))
    op.add_column("rfqs", sa.Column("currency", sa.String(length=8), nullable=False, server_default="USD"))
    op.add_column("rfqs", sa.Column("lead_time_days", sa.Integer(), nullable=True))
    op.add_column("rfqs", sa.Column("risk_summary", sa.Text(), nullable=True))
    op.add_column("rfqs", sa.Column("notes", sa.Text(), nullable=True))
    op.add_column("rfqs", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))

    op.create_index(op.f("ix_rfqs_supplier_code"), "rfqs", ["supplier_code"], unique=False)
    op.create_index(op.f("ix_rfqs_workflow_id"), "rfqs", ["workflow_id"], unique=False)

    op.create_table(
        "rfq_action_history",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("rfq_record_id", sa.String(length=64), nullable=False),
        sa.Column("rfq_id", sa.String(length=128), nullable=False),
        sa.Column("action_type", sa.String(length=64), nullable=False),
        sa.Column("previous_status", sa.String(length=64), nullable=False),
        sa.Column("new_status", sa.String(length=64), nullable=False),
        sa.Column("actor", sa.String(length=120), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["rfq_record_id"],
            ["rfqs.id"],
            name=op.f("fk_rfq_action_history_rfq_record_id_rfqs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rfq_action_history")),
    )
    op.create_index(op.f("ix_rfq_action_history_action_type"), "rfq_action_history", ["action_type"], unique=False)
    op.create_index(op.f("ix_rfq_action_history_created_at"), "rfq_action_history", ["created_at"], unique=False)
    op.create_index(op.f("ix_rfq_action_history_new_status"), "rfq_action_history", ["new_status"], unique=False)
    op.create_index(op.f("ix_rfq_action_history_rfq_id"), "rfq_action_history", ["rfq_id"], unique=False)
    op.create_index(op.f("ix_rfq_action_history_rfq_record_id"), "rfq_action_history", ["rfq_record_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_rfq_action_history_rfq_record_id"), table_name="rfq_action_history")
    op.drop_index(op.f("ix_rfq_action_history_rfq_id"), table_name="rfq_action_history")
    op.drop_index(op.f("ix_rfq_action_history_new_status"), table_name="rfq_action_history")
    op.drop_index(op.f("ix_rfq_action_history_created_at"), table_name="rfq_action_history")
    op.drop_index(op.f("ix_rfq_action_history_action_type"), table_name="rfq_action_history")
    op.drop_table("rfq_action_history")

    op.drop_index(op.f("ix_rfqs_workflow_id"), table_name="rfqs")
    op.drop_index(op.f("ix_rfqs_supplier_code"), table_name="rfqs")
    op.drop_column("rfqs", "updated_at")
    op.drop_column("rfqs", "notes")
    op.drop_column("rfqs", "risk_summary")
    op.drop_column("rfqs", "lead_time_days")
    op.drop_column("rfqs", "currency")
    op.drop_column("rfqs", "price")
    op.drop_column("rfqs", "workflow_id")
    op.drop_column("rfqs", "supplier_code")
