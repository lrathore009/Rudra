"""Alembic migration environment."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from rudra.core.config import get_settings
from rudra.memory.models.base import Base
from rudra.memory.models.memory import *  # noqa: F401, F403
from rudra.security.audit import AuditLog  # noqa: F401
from rudra.auth.models import User  # noqa: F401
from rudra.graph.models import (  # noqa: F401
    Entity,
    EntityAlias,
    GraphRelationship,
    MemoryEntityLink,
    ProjectEntityLink,
)
from rudra.projects.models import (  # noqa: F401
    FounderProject,
    ProjectMetric,
    ProjectMilestone,
    ProjectTask,
    ProjectUpdate,
)
from rudra.documents.models import Document, DocumentChunk, DocumentEntity  # noqa: F401
from rudra.integrations.models import (  # noqa: F401
    DailyBriefing,
    EACommitment,
    EAFeedItem,
    EAFinanceSnapshot,
    EAHealthMetric,
    EATranscript,
    ExternalAccount,
    ExternalEmail,
    ExternalEvent,
    Integration,
)
from rudra.research.models import ResearchJob, ResearchWatchlist  # noqa: F401
from rudra.domains.models import (  # noqa: F401
    ConciergeRequest,
    LuxuryAlert,
    LuxuryIntelSnapshot,
    OpsSlaEvent,
    PresentationDeck,
    PresentationSlide,
    RetrievalTrace,
    TravelLeg,
    TravelTrip,
    VendorInteraction,
    WritingDraft,
    WritingDraftVersion,
)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    return get_settings().database_url


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    url = get_url()
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = url

    connect_args: dict = {}
    if "supabase.co" in url or "supabase.com" in url:
        connect_args["ssl"] = "require"
        connect_args["statement_cache_size"] = 0

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
