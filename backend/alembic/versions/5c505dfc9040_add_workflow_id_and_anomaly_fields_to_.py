"""add workflow id and anomaly fields to risk assessments

Revision ID: 5c505dfc9040
Revises: 7a1f2d9c4e6b
Create Date: 2026-05-08 21:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5c505dfc9040"
down_revision = "7a1f2d9c4e6b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "risk_assessments",
        sa.Column("workflow_id", sa.String(length=128), nullable=True),
    )

    op.add_column(
        "risk_assessments",
        sa.Column("anomaly_direction", sa.String(length=32), nullable=True),
    )

    op.add_column(
        "risk_assessments",
        sa.Column("anomaly_z_score", sa.Float(), nullable=True),
    )

    op.add_column(
        "risk_assessments",
        sa.Column("anomaly_baseline_mean", sa.Float(), nullable=True),
    )

    op.create_index(
        op.f("ix_risk_assessments_workflow_id"),
        "risk_assessments",
        ["workflow_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_risk_assessments_workflow_id"),
        table_name="risk_assessments",
    )

    op.drop_column(
        "risk_assessments",
        "anomaly_baseline_mean",
    )

    op.drop_column(
        "risk_assessments",
        "anomaly_z_score",
    )

    op.drop_column(
        "risk_assessments",
        "anomaly_direction",
    )

    op.drop_column(
        "risk_assessments",
        "workflow_id",
    )