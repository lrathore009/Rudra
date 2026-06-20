"""Writing draft studio — versioned drafts and tone refinement."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.agents.data.service import AgentDataService
from rudra.agents.types import AgentType
from rudra.domains.models import WritingDraft, WritingDraftVersion


class DraftService:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id

    async def save(
        self,
        title: str,
        content: str,
        *,
        fmt: str = "email",
        tone: str | None = None,
    ) -> WritingDraft:
        draft = WritingDraft(
            user_id=self.user_id,
            title=title,
            content=content,
            format=fmt,
            tone=tone,
            status="draft",
            current_version=1,
        )
        self.session.add(draft)
        await self.session.flush()
        self.session.add(
            WritingDraftVersion(draft_id=draft.id, version=1, content=content)
        )
        await self.session.flush()
        data = AgentDataService(self.session, self.user_id)
        await data.create_artifact(
            AgentType.WRITING,
            "draft",
            title,
            content,
            metadata={"draft_id": str(draft.id), "format": fmt, "tone": tone},
        )
        return draft

    async def get(self, draft_id: uuid.UUID) -> WritingDraft | None:
        result = await self.session.execute(
            select(WritingDraft).where(
                WritingDraft.id == draft_id,
                WritingDraft.user_id == self.user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_drafts(self, *, status: str | None = None, limit: int = 20) -> list[WritingDraft]:
        stmt = (
            select(WritingDraft)
            .where(WritingDraft.user_id == self.user_id)
            .order_by(WritingDraft.updated_at.desc())
            .limit(limit)
        )
        if status:
            stmt = stmt.where(WritingDraft.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def rewrite(
        self,
        draft_id: uuid.UUID,
        new_content: str,
        *,
        brain: Any = None,
        tone: str | None = None,
    ) -> WritingDraft | None:
        draft = await self.get(draft_id)
        if not draft:
            return None
        content = new_content
        if brain is not None:
            from rudra.brain.orchestrator import Brain, Message

            b = brain if isinstance(brain, Brain) else Brain()
            style = await AgentDataService(self.session, self.user_id).preference_profile(("writing",))
            style_block = str(style.get("writing", {}))
            result = await b.think(
                [
                    Message(
                        role="user",
                        content=f"Rewrite in owner voice (tone={tone or draft.tone or 'default'}):\n\n{new_content}",
                    )
                ],
                system=f"Writing profile:\n{style_block}\nRemove filler. Match sign-off and avoid-list.",
                model_tier="fast",
            )
            content = result.content

        draft.current_version += 1
        draft.content = content
        if tone:
            draft.tone = tone
        self.session.add(
            WritingDraftVersion(draft_id=draft.id, version=draft.current_version, content=content)
        )
        await self.session.flush()
        return draft

    async def export_markdown(self, draft_id: uuid.UUID) -> str | None:
        draft = await self.get(draft_id)
        if not draft:
            return None
        return f"# {draft.title}\n\n{draft.content}\n"

    async def stale_drafts(self, *, days: int = 7) -> list[WritingDraft]:
        from datetime import datetime, timedelta, timezone

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        drafts = await self.list_drafts(status="draft", limit=50)
        return [d for d in drafts if d.updated_at and d.updated_at < cutoff]

    async def export_for_federation(self, *, limit: int = 30) -> list[dict[str, Any]]:
        drafts = await self.list_drafts(limit=limit)
        return [
            {
                "type": "writing_draft",
                "title": d.title,
                "content": d.content[:4000],
                "format": d.format,
                "status": d.status,
            }
            for d in drafts
        ]
