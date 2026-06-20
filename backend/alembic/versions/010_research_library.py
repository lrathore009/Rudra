"""Migration 010 — Phase 2 research library depth."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EMBEDDING_DIM = 768


def upgrade() -> None:
    op.add_column("research_reports", sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=True))
    op.add_column("research_reports", sa.Column("topic_tags", sa.dialects.postgresql.JSONB(), nullable=True))
    op.add_column("research_reports", sa.Column("parent_id", sa.Uuid(), nullable=True))
    op.add_column("research_reports", sa.Column("metadata", sa.dialects.postgresql.JSONB(), nullable=True))
    op.add_column("research_reports", sa.Column("query_hash", sa.String(64), nullable=True))
    op.create_index("ix_research_reports_query_hash", "research_reports", ["user_id", "query_hash"])

    op.create_table(
        "research_watchlist",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.String(128), nullable=False),
        sa.Column("topic", sa.String(256), nullable=False),
        sa.Column("query_template", sa.Text(), nullable=False),
        sa.Column("ttl_days", sa.Integer(), server_default="30"),
        sa.Column("last_run_at", sa.String(64), nullable=True),
        sa.Column("last_report_id", sa.Uuid(), nullable=True),
        sa.Column("enabled", sa.Boolean(), server_default="true"),
        sa.Column("metadata", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_research_watchlist_user", "research_watchlist", ["user_id"])

    op.create_table(
        "research_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.String(128), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("status", sa.String(32), server_default="completed"),
        sa.Column("report_id", sa.Uuid(), nullable=True),
        sa.Column("source_count", sa.Integer(), server_default="0"),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("telemetry", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_research_jobs_user", "research_jobs", ["user_id"])


def downgrade() -> None:
    op.drop_table("research_jobs")
    op.drop_table("research_watchlist")
    op.drop_index("ix_research_reports_query_hash", table_name="research_reports")
    op.drop_column("research_reports", "query_hash")
    op.drop_column("research_reports", "metadata")
    op.drop_column("research_reports", "parent_id")
    op.drop_column("research_reports", "topic_tags")
    op.drop_column("research_reports", "embedding")
