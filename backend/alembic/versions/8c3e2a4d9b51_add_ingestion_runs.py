"""add ingestion runs

Revision ID: 8c3e2a4d9b51
Revises: 6f7b1f0d093f
Create Date: 2026-04-23 16:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "8c3e2a4d9b51"
down_revision = "6f7b1f0d093f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "ingestion_runs" not in inspector.get_table_names():
        op.create_table(
            "ingestion_runs",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("source_type", sa.String(length=50), nullable=False),
            sa.Column("source_name", sa.String(length=150), nullable=True),
            sa.Column("source_file", sa.String(length=500), nullable=True),
            sa.Column("status", sa.String(length=50), nullable=False),
            sa.Column("inserted_count", sa.Integer(), nullable=False),
            sa.Column("skipped_count", sa.Integer(), nullable=False),
            sa.Column("duplicate_count", sa.Integer(), nullable=False),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column(
                "started_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    index_names = {index["name"] for index in inspector.get_indexes("ingestion_runs")}
    indexes = {
        op.f("ix_ingestion_runs_id"): ["id"],
        op.f("ix_ingestion_runs_source_name"): ["source_name"],
        op.f("ix_ingestion_runs_source_type"): ["source_type"],
        op.f("ix_ingestion_runs_status"): ["status"],
    }
    for index_name, columns in indexes.items():
        if index_name not in index_names:
            op.create_index(index_name, "ingestion_runs", columns, unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ingestion_runs_status"), table_name="ingestion_runs")
    op.drop_index(op.f("ix_ingestion_runs_source_type"), table_name="ingestion_runs")
    op.drop_index(op.f("ix_ingestion_runs_source_name"), table_name="ingestion_runs")
    op.drop_index(op.f("ix_ingestion_runs_id"), table_name="ingestion_runs")
    op.drop_table("ingestion_runs")
