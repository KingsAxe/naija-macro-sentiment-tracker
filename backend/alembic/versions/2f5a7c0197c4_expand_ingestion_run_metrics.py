"""expand ingestion run metrics

Revision ID: 2f5a7c0197c4
Revises: 8c3e2a4d9b51
Create Date: 2026-04-23 16:55:00
"""

from alembic import op
import sqlalchemy as sa


revision = "2f5a7c0197c4"
down_revision = "8c3e2a4d9b51"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("ingestion_runs") as batch_op:
        batch_op.add_column(sa.Column("fetched_count", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("rejected_count", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("qa_summary", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("ingestion_runs") as batch_op:
        batch_op.drop_column("qa_summary")
        batch_op.drop_column("rejected_count")
        batch_op.drop_column("fetched_count")
