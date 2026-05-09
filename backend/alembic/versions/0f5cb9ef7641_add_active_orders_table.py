"""add active orders table

Revision ID: 0f5cb9ef7641
Revises: a446128c5a7a
Create Date: 2026-05-09 14:23:58.701875
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0f5cb9ef7641"
down_revision = "a446128c5a7a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "active_orders",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("supplier_id", sa.String(length=64), nullable=False),
        sa.Column("supplier_name", sa.String(length=255), nullable=False),
        sa.Column("destination_country", sa.String(length=120), nullable=False),
        sa.Column("destination", sa.String(length=255), nullable=False),
        sa.Column("volume_units", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.String(length=50), nullable=False),
        sa.Column("line_items", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_active_orders")),
    )

    op.create_index(
        op.f("ix_active_orders_supplier_id"),
        "active_orders",
        ["supplier_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_active_orders_status"),
        "active_orders",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_active_orders_status"),
        table_name="active_orders",
    )

    op.drop_index(
        op.f("ix_active_orders_supplier_id"),
        table_name="active_orders",
    )

    op.drop_table("active_orders")