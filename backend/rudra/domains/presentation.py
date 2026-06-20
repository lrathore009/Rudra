"""Presentation deck builder — structured slides from sources."""

from __future__ import annotations

import re
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.agents.data.service import AgentDataService
from rudra.agents.types import AgentType
from rudra.domains.librarian import LibrarianRetrievalService
from rudra.domains.models import PresentationDeck, PresentationSlide
from rudra.research.hybrid import hybrid_search_reports
from rudra.research.reports import ResearchReportService


class DeckService:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id

    async def create_outline(
        self,
        title: str,
        outline: str,
        *,
        audience: str = "executive",
        slides: int = 6,
    ) -> PresentationDeck:
        deck = PresentationDeck(
            user_id=self.user_id,
            title=title,
            audience=audience,
            slide_count=slides,
            metadata_={"source": "outline"},
        )
        self.session.add(deck)
        await self.session.flush()
        parts = [p.strip() for p in re.split(r"\n(?=Slide|\d+\.)", outline) if p.strip()]
        if not parts:
            parts = [outline]
        for idx, part in enumerate(parts[:slides], start=1):
            title_line = part.split("\n", 1)[0][:512]
            self.session.add(
                PresentationSlide(
                    deck_id=deck.id,
                    sequence=idx,
                    title=title_line,
                    content=part,
                    speaker_notes=f"Audience: {audience}",
                )
            )
        deck.slide_count = min(len(parts), slides)
        await self.session.flush()
        data = AgentDataService(self.session, self.user_id)
        await data.create_artifact(
            AgentType.PRESENTATION,
            "deck_outline",
            title,
            outline,
            metadata={"deck_id": str(deck.id), "slides": deck.slide_count},
        )
        return deck

    async def build_from_sources(
        self,
        title: str,
        query: str,
        *,
        audience: str = "executive",
        slide_count: int = 6,
    ) -> PresentationDeck:
        librarian = LibrarianRetrievalService(self.session, self.user_id)
        sources = await librarian.unified_search(query, limit=slide_count + 2)
        report_svc = ResearchReportService(self.session, self.user_id)
        research = await hybrid_search_reports(report_svc, query, limit=3)

        deck = PresentationDeck(
            user_id=self.user_id,
            title=title,
            audience=audience,
            status="draft",
            metadata_={"query": query},
        )
        self.session.add(deck)
        await self.session.flush()

        slide_defs = [
            ("Title", title, f"Opening for {audience} audience"),
            ("Context", query, "Frame the narrative"),
        ]
        for src in sources[: slide_count - 3]:
            slide_defs.append((src["title"][:80], src["snippet"], f"Source: {src['type']}"))
        for report, _ in research[:2]:
            slide_defs.append((report.title[:80], report.content[:400], "Research library"))
        slide_defs.append(("Conclusion", "Next steps and ask", "Close with action items"))

        for idx, (stitle, content, notes) in enumerate(slide_defs[:slide_count], start=1):
            self.session.add(
                PresentationSlide(
                    deck_id=deck.id,
                    sequence=idx,
                    title=stitle,
                    content=content,
                    speaker_notes=notes,
                    sources=[s for s in sources[:3]],
                )
            )
        deck.slide_count = min(len(slide_defs), slide_count)
        await self.session.flush()
        return deck

    async def get_deck(self, deck_id: uuid.UUID) -> PresentationDeck | None:
        result = await self.session.execute(
            select(PresentationDeck).where(
                PresentationDeck.id == deck_id,
                PresentationDeck.user_id == self.user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_decks(self, *, limit: int = 10) -> list[PresentationDeck]:
        result = await self.session.execute(
            select(PresentationDeck)
            .where(PresentationDeck.user_id == self.user_id)
            .order_by(PresentationDeck.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_slides(self, deck_id: uuid.UUID) -> list[PresentationSlide]:
        result = await self.session.execute(
            select(PresentationSlide)
            .where(PresentationSlide.deck_id == deck_id)
            .order_by(PresentationSlide.sequence)
        )
        return list(result.scalars().all())

    async def export_markdown(self, deck_id: uuid.UUID) -> str | None:
        deck = await self.get_deck(deck_id)
        if not deck:
            return None
        slides = await self.list_slides(deck_id)
        lines = [f"# {deck.title}", f"Audience: {deck.audience}", ""]
        for s in slides:
            lines.extend([f"## Slide {s.sequence}: {s.title}", s.content, "", f"_Notes: {s.speaker_notes or ''}_", ""])
        return "\n".join(lines)

    async def export_for_federation(self, *, limit: int = 10) -> list[dict[str, Any]]:
        decks = await self.list_decks(limit=limit)
        out = []
        for d in decks:
            slides = await self.list_slides(d.id)
            out.append(
                {
                    "type": "presentation_deck",
                    "title": d.title,
                    "slides": [{"title": s.title, "content": s.content[:500]} for s in slides],
                }
            )
        return out
