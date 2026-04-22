"""add topic label to raw texts

Revision ID: f2f7274f66b0
Revises: ba7340a79aa5
Create Date: 2026-04-22 17:57:00
"""

from alembic import op
import sqlalchemy as sa


revision = "f2f7274f66b0"
down_revision = "ba7340a79aa5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("raw_texts", sa.Column("topic_label", sa.String(length=150), nullable=True))
    op.create_index(op.f("ix_raw_texts_topic_label"), "raw_texts", ["topic_label"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_raw_texts_topic_label"), table_name="raw_texts")
    op.drop_column("raw_texts", "topic_label")
