"""split opinion assessments

Revision ID: 6f7b1f0d093f
Revises: f2f7274f66b0
Create Date: 2026-04-23 13:03:00
"""

from alembic import op
import sqlalchemy as sa


revision = "6f7b1f0d093f"
down_revision = "f2f7274f66b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "opinion_assessments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("opinion_target_id", sa.Integer(), nullable=False),
        sa.Column("assessment_text", sa.String(length=200), nullable=False),
        sa.Column("assessment_sentiment", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["opinion_target_id"], ["opinion_targets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_opinion_assessments_assessment_sentiment"),
        "opinion_assessments",
        ["assessment_sentiment"],
        unique=False,
    )
    op.create_index(
        op.f("ix_opinion_assessments_assessment_text"),
        "opinion_assessments",
        ["assessment_text"],
        unique=False,
    )
    op.create_index(
        op.f("ix_opinion_assessments_id"),
        "opinion_assessments",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_opinion_assessments_opinion_target_id"),
        "opinion_assessments",
        ["opinion_target_id"],
        unique=False,
    )

    op.execute("delete from opinion_targets where target_name like '%: %'")


def downgrade() -> None:
    op.drop_index(op.f("ix_opinion_assessments_opinion_target_id"), table_name="opinion_assessments")
    op.drop_index(op.f("ix_opinion_assessments_id"), table_name="opinion_assessments")
    op.drop_index(op.f("ix_opinion_assessments_assessment_text"), table_name="opinion_assessments")
    op.drop_index(op.f("ix_opinion_assessments_assessment_sentiment"), table_name="opinion_assessments")
    op.drop_table("opinion_assessments")
