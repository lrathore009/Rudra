"""Agent phase domain service — CRUD, preferences, and encoded artifacts."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.agents.data.models import AgentArtifact
from rudra.agents.types import AgentType
from rudra.memory.models.memory import Preference


class AgentDataService:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id

    async def create_artifact(
        self,
        agent_type: AgentType | str,
        artifact_type: str,
        title: str,
        content: str,
        *,
        metadata: dict[str, Any] | None = None,
        status: str = "active",
    ) -> AgentArtifact:
        artifact = AgentArtifact(
            user_id=self.user_id,
            agent_type=str(agent_type.value if isinstance(agent_type, AgentType) else agent_type),
            artifact_type=artifact_type,
            title=title,
            content=content,
            metadata_=metadata,
            status=status,
        )
        self.session.add(artifact)
        await self.session.flush()
        return artifact

    async def list_artifacts(
        self,
        agent_type: AgentType | str,
        *,
        artifact_type: str | None = None,
        status: str | None = None,
        limit: int = 20,
    ) -> list[AgentArtifact]:
        agent_val = agent_type.value if isinstance(agent_type, AgentType) else agent_type
        stmt = (
            select(AgentArtifact)
            .where(AgentArtifact.user_id == self.user_id, AgentArtifact.agent_type == agent_val)
            .order_by(AgentArtifact.created_at.desc())
            .limit(limit)
        )
        if artifact_type:
            stmt = stmt.where(AgentArtifact.artifact_type == artifact_type)
        if status:
            stmt = stmt.where(AgentArtifact.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_artifacts(
        self,
        agent_type: AgentType | str,
        query: str,
        *,
        artifact_type: str | None = None,
        limit: int = 10,
    ) -> list[AgentArtifact]:
        agent_val = agent_type.value if isinstance(agent_type, AgentType) else agent_type
        like = f"%{query.lower()}%"
        stmt = (
            select(AgentArtifact)
            .where(
                AgentArtifact.user_id == self.user_id,
                AgentArtifact.agent_type == agent_val,
                or_(
                    func.lower(AgentArtifact.title).like(like),
                    func.lower(AgentArtifact.content).like(like),
                ),
            )
            .order_by(AgentArtifact.created_at.desc())
            .limit(limit)
        )
        if artifact_type:
            stmt = stmt.where(AgentArtifact.artifact_type == artifact_type)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert_preference(
        self,
        category: str,
        key: str,
        value: str,
        *,
        confidence: float = 1.0,
        source: str | None = None,
    ) -> Preference:
        result = await self.session.execute(
            select(Preference).where(
                Preference.user_id == self.user_id,
                Preference.category == category,
                Preference.key == key,
            )
        )
        pref = result.scalar_one_or_none()
        if pref:
            pref.value = value
            pref.confidence = confidence
            if source:
                pref.source = source
        else:
            pref = Preference(
                user_id=self.user_id,
                category=category,
                key=key,
                value=value,
                confidence=confidence,
                source=source,
            )
            self.session.add(pref)
        await self.session.flush()
        return pref

    async def list_preferences(
        self,
        *,
        category: str | None = None,
        query: str | None = None,
        limit: int = 50,
    ) -> list[Preference]:
        stmt = (
            select(Preference)
            .where(Preference.user_id == self.user_id)
            .order_by(Preference.category, Preference.key)
            .limit(limit)
        )
        if category:
            stmt = stmt.where(Preference.category == category)
        if query:
            like = f"%{query.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Preference.key).like(like),
                    func.lower(Preference.value).like(like),
                    func.lower(Preference.category).like(like),
                )
            )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def preference_profile(self, categories: tuple[str, ...]) -> dict[str, dict[str, str]]:
        prefs = await self.list_preferences(limit=100)
        profile: dict[str, dict[str, str]] = {}
        for p in prefs:
            if p.category not in categories:
                continue
            profile.setdefault(p.category, {})[p.key] = p.value
        return profile
