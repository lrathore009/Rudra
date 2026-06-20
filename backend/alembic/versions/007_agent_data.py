"""Agent phase domain data — artifacts encoded per specialist agent.

Revision ID: 007
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agent_artifacts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.String(128), nullable=False),
        sa.Column("agent_type", sa.String(64), nullable=False),
        sa.Column("artifact_type", sa.String(64), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(32), server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_artifacts_user_agent", "agent_artifacts", ["user_id", "agent_type"])
    op.create_index("ix_agent_artifacts_type", "agent_artifacts", ["artifact_type"])


def downgrade() -> None:
    op.drop_index("ix_agent_artifacts_type", table_name="agent_artifacts")
    op.drop_index("ix_agent_artifacts_user_agent", table_name="agent_artifacts")
    op.drop_table("agent_artifacts")
