"""Per-agent phase context enrichment — inject encoded domain data before execution."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from rudra.agents.data.service import AgentDataService
from rudra.agents.profiles import AGENT_PROFILES
from rudra.agents.types import AgentType
from rudra.graph.service import GraphService
from rudra.integrations.service import BriefingService
from rudra.memory.models.memory import MemoryType
from rudra.memory.service import MemoryService
from rudra.projects.service import ProjectService
from rudra.research.reports import ResearchReportService


async def enrich_agent_phase(
    query: str,
    agent_type: AgentType,
    session: AsyncSession,
    user_id: str,
    blocks: list[str],
    sources_used: list[dict[str, str]],
) -> None:
    """Append agent-specific encoded data blocks (mutates lists in place)."""
    profile = AGENT_PROFILES[agent_type]
    data = AgentDataService(session, user_id)
    memory = MemoryService(session, user_id)

    if profile.memory_tags:
        tagged = await memory.search_by_tags(list(profile.memory_tags), limit=6)
        if tagged:
            blocks.append(f"\n## {agent_type.value.replace('_', ' ').title()} Domain Memories\n")
            for mem in tagged:
                blocks.append(f"- [{mem.memory_type}] {mem.title}: {mem.content[:220]}")
                sources_used.append({"type": "memory", "title": mem.title, "id": str(mem.id)})

    if agent_type == AgentType.EXECUTIVE_ASSISTANT:
        await _enrich_executive(session, user_id, blocks, sources_used)
    elif agent_type == AgentType.RESEARCH_ANALYST:
        await _enrich_research(session, user_id, query, blocks, sources_used)
    elif agent_type == AgentType.CONCIERGE:
        await _enrich_concierge(data, blocks, sources_used, session, user_id)
    elif agent_type == AgentType.LUXURY_ANALYST:
        await _enrich_luxury(data, blocks, sources_used, session, user_id)
    elif agent_type == AgentType.TRAVEL:
        await _enrich_travel(data, memory, blocks, sources_used, session, user_id)
    elif agent_type == AgentType.KNOWLEDGE_LIBRARIAN:
        await _enrich_librarian(session, user_id, query, blocks, sources_used)
    elif agent_type == AgentType.WRITING:
        await _enrich_writing(data, blocks, sources_used, session, user_id)
    elif agent_type == AgentType.PRESENTATION:
        await _enrich_presentation(session, user_id, data, blocks, sources_used)
    elif agent_type == AgentType.OPERATIONS:
        await _enrich_operations(data, blocks, sources_used, session, user_id)

    await _inject_free_intel(query, agent_type, blocks, sources_used)


async def _inject_free_intel(
    query: str,
    agent_type: AgentType,
    blocks: list[str],
    sources_used: list[dict[str, str]],
) -> None:
    import asyncio

    from rudra.core.config import get_settings
    from rudra.jarvis.connectors.agent_free_sources.registry import AgentFreeSourcesRegistry

    registry = AgentFreeSourcesRegistry()
    # Phase 3: live free-source HTTP is bounded — it must never delay enrichment past budget.
    try:
        items = await asyncio.wait_for(
            registry.fetch(agent_type, query, limit=6),
            timeout=get_settings().free_sources_budget_seconds,
        )
    except Exception:  # noqa: BLE001 - timeout/network failure → skip free intel, keep cached data
        return
    if not items:
        return
    label = agent_type.value.replace("_", " ").title()
    blocks.append(f"\n## {label} Free Intelligence\n")
    for item in items:
        blocks.append(f"- [{item.provider}] {item.title}: {item.content[:180]}")
        sources_used.append(
            {"type": item.provider, "title": item.title, "url": item.url or "", "category": item.category}
        )


async def _enrich_executive(
    session: AsyncSession,
    user_id: str,
    blocks: list[str],
    sources_used: list[dict[str, str]],
) -> None:
    from rudra.integrations.executive import ExecutiveCommandService

    stack = await ExecutiveCommandService(session, user_id).get_command_stack()
    prefs = await AgentDataService(session, user_id).list_preferences(category="executive")

    if prefs:
        blocks.append("\n## Executive Preferences\n")
        for p in prefs:
            blocks.append(f"- {p.key}: {p.value}")

    blocks.append("\n## Active Project Priorities\n")
    for card in stack["projects"]["projects"][:6]:
        blocks.append(
            f"- P{card['priority']} · {card['name']} ({card['progress_percent']}%): {card['next_action']}"
        )
        sources_used.append({"type": "project", "title": card["name"], "id": card["id"]})

    weather = stack["tier2"].get("weather")
    if weather:
        blocks.append("\n## Weather\n")
        blocks.append(f"- {weather['location']}: {weather['summary']}")
        sources_used.append({"type": "weather", "title": weather["location"]})

    if stack["tier1"]["calendar"]:
        blocks.append("\n## Upcoming Calendar\n")
        for event in stack["tier1"]["calendar"][:5]:
            blocks.append(f"- {event.get('starts_at')} · {event.get('title')}")
            sources_used.append({"type": "calendar", "title": event.get("title", "Event")})

    if stack["tier1"]["email"]:
        blocks.append("\n## Priority Inbox\n")
        for mail in stack["tier1"]["email"][:5]:
            flag = " [ACTION]" if mail.get("needs_attention") else ""
            blocks.append(f"- {mail.get('sender')}: {mail.get('subject')}{flag}")
            sources_used.append({"type": "email", "title": mail.get("subject", "Email")})

    if stack["commitments"]:
        blocks.append("\n## Open Commitments\n")
        for c in stack["commitments"][:6]:
            blocks.append(f"- {c['title']}")
            sources_used.append({"type": "commitment", "title": c["title"], "id": c["id"]})

    if stack["tier1"]["tasks"]:
        blocks.append("\n## Tasks\n")
        for task in stack["tier1"]["tasks"][:5]:
            blocks.append(f"- [{task.get('status')}] {task.get('title')}")

    if stack["tier3"]["travel"]:
        blocks.append("\n## Travel\n")
        for t in stack["tier3"]["travel"][:3]:
            blocks.append(f"- {t.get('title')}")

    if stack["tier2"]["finance"]:
        blocks.append("\n## Finance Pulse\n")
        for line in stack["tier2"]["finance"][:4]:
            blocks.append(f"- {line.get('label')}: {line.get('amount')} {line.get('currency', 'USD')}")

    if stack["tier4"]["health"]:
        blocks.append("\n## Health / Recovery\n")
        for h in stack["tier4"]["health"][:3]:
            blocks.append(f"- {h.get('metric_type')}: {h.get('value')} {h.get('unit') or ''}")

    briefing_svc = BriefingService(session, user_id)
    briefing = await briefing_svc.get_latest()
    if briefing:
        blocks.append("\n## Daily Command Briefing\n")
        blocks.append(briefing.content[:2000])
        sources_used.append({"type": "briefing", "title": briefing.briefing_date})


async def _enrich_research(
    session: AsyncSession,
    user_id: str,
    query: str,
    blocks: list[str],
    sources_used: list[dict[str, str]],
) -> None:
    from rudra.research.hybrid import hybrid_search_reports

    svc = ResearchReportService(session, user_id)
    if query:
        hits = await hybrid_search_reports(svc, query, limit=4)
        reports = [r for r, _ in hits]
    else:
        reports = await svc.list_recent(limit=5)
    trends = await svc.trends()
    if trends["count"]:
        blocks.append(
            f"\n## Research Library Stats\n"
            f"- {trends['count']} reports · avg confidence {trends['avg_confidence']:.2f} · stale {trends['stale_count']}"
        )
    if reports:
        blocks.append("\n## Research Library\n")
        for r in reports:
            blocks.append(
                f"- {r.title} (confidence {r.confidence_score:.2f}): {r.content[:180]}"
            )
            sources_used.append({"type": "research_report", "title": r.title, "id": str(r.id)})


async def _enrich_concierge(
    data: AgentDataService,
    blocks: list[str],
    sources_used: list[dict[str, str]],
    session: AsyncSession | None = None,
    user_id: str = "owner",
) -> None:
    prefs = await data.list_preferences(limit=30)
    dining = [p for p in prefs if p.category in ("dining", "hotels")]
    if dining:
        blocks.append("\n## Concierge Preferences\n")
        for p in dining:
            blocks.append(f"- [{p.category}] {p.key}: {p.value}")

    if session:
        from rudra.domains.concierge import ExperienceService

        svc = ExperienceService(session, user_id)
        requests = await svc.list_open(limit=5)
        if requests:
            blocks.append("\n## Open Experience Requests\n")
            for req in requests:
                blocks.append(f"- [{req.status}] {req.title}: {req.details[:160]}")
                sources_used.append({"type": "concierge_request", "title": req.title, "id": str(req.id)})
        return

    requests = await data.list_artifacts(
        AgentType.CONCIERGE, artifact_type="experience_request", status="active", limit=5
    )
    if requests:
        blocks.append("\n## Open Experience Requests\n")
        for req in requests:
            blocks.append(f"- {req.title}: {req.content[:160]}")
            sources_used.append({"type": "experience_request", "title": req.title, "id": str(req.id)})


async def _enrich_luxury(
    data: AgentDataService,
    blocks: list[str],
    sources_used: list[dict[str, str]],
    session: AsyncSession | None = None,
    user_id: str = "owner",
) -> None:
    watchlist = await data.list_artifacts(
        AgentType.LUXURY_ANALYST, artifact_type="watchlist", limit=8
    )
    prefs = await data.preference_profile(("luxury",))
    if prefs.get("luxury"):
        blocks.append("\n## Luxury Profile\n")
        for key, val in prefs["luxury"].items():
            blocks.append(f"- {key}: {val}")
    if watchlist:
        blocks.append("\n## Market Watchlist\n")
        for item in watchlist:
            alert = (item.metadata_ or {}).get("alert", "")
            blocks.append(f"- {item.title} [{alert}]: {item.content[:140]}")
            sources_used.append({"type": "watchlist", "title": item.title, "id": str(item.id)})
    if session:
        from rudra.domains.luxury_desk import LuxuryDeskService

        trends = await LuxuryDeskService(session, user_id).desk_trends()
        if trends["count"]:
            blocks.append(f"\n## Luxury Desk\n- {trends['count']} snapshots · exclusivity {trends['avg_exclusivity']:.2f}")


async def _enrich_travel(
    data: AgentDataService,
    memory: MemoryService,
    blocks: list[str],
    sources_used: list[dict[str, str]],
    session: AsyncSession | None = None,
    user_id: str = "owner",
) -> None:
    prefs = await data.preference_profile(("travel",))
    if prefs.get("travel"):
        blocks.append("\n## Travel Preferences\n")
        for key, val in prefs["travel"].items():
            blocks.append(f"- {key}: {val}")

    if session:
        from rudra.domains.travel import TripService

        brief = await TripService(session, user_id).travel_brief()
        if brief["trips"]:
            blocks.append("\n## Structured Trips\n")
            for t in brief["trips"]:
                blocks.append(f"- {t['title']} ({t['status']})")
        if brief["upcoming_legs"]:
            blocks.append("\n## Upcoming Legs\n")
            for leg in brief["upcoming_legs"]:
                blocks.append(f"- {leg['destination']} @ {leg.get('starts_at', 'TBD')}")

    itineraries = await data.list_artifacts(AgentType.TRAVEL, artifact_type="itinerary", limit=5)
    if itineraries:
        blocks.append("\n## Active Itineraries\n")
        for itin in itineraries:
            meta = itin.metadata_ or {}
            blocks.append(f"- {itin.title} ({meta.get('status', 'active')}): {itin.content[:160]}")
            sources_used.append({"type": "itinerary", "title": itin.title, "id": str(itin.id)})

    travel_mem = await memory.search_by_tags(["travel", "itinerary", "visa"], limit=5)
    if travel_mem:
        blocks.append("\n## Travel Knowledge\n")
        for mem in travel_mem:
            blocks.append(f"- {mem.title}: {mem.content[:160]}")


async def _enrich_librarian(
    session: AsyncSession,
    user_id: str,
    query: str,
    blocks: list[str],
    sources_used: list[dict[str, str]],
) -> None:
    graph = GraphService(session, user_id)
    entities = await graph.list_entities(query=query[:80] if query else None, limit=6)
    if entities:
        blocks.append("\n## Knowledge Graph Matches\n")
        for ent in entities:
            blocks.append(f"- [{ent.entity_type}] {ent.name}: {(ent.description or '')[:120]}")
            sources_used.append({"type": "entity", "title": ent.name, "id": str(ent.id)})
            neighbors = await graph.get_neighbors(ent.id, limit=4)
            for n in neighbors:
                blocks.append(f"  ↳ {n['relation']} → {n['name']} ({n['type']})")

    if query:
        from rudra.domains.librarian import LibrarianRetrievalService

        hits = await LibrarianRetrievalService(session, user_id).unified_search(query, limit=4)
        if hits:
            blocks.append("\n## Unified Retrieval\n")
            for h in hits:
                blocks.append(f"- [{h['type']}] {h['title']} (score={h['score']})")
                sources_used.append({"type": h["type"], "title": h["title"]})

        try:
            from rudra.documents.service import DocumentService

            doc_svc = DocumentService(session, user_id)
            hits = await doc_svc.search(query, limit=3)
            if hits:
                blocks.append("\n## Document Passages\n")
                for chunk, doc, score in hits:
                    blocks.append(f"- ({doc.filename}, {score:.2f}) {chunk.content[:160]}")
                    sources_used.append({"type": "document", "title": doc.filename})
        except Exception:
            pass


async def _enrich_writing(
    data: AgentDataService,
    blocks: list[str],
    sources_used: list[dict[str, str]],
    session: AsyncSession | None = None,
    user_id: str = "owner",
) -> None:
    style = await data.preference_profile(("writing",))
    if style.get("writing"):
        blocks.append("\n## Writing Voice Profile\n")
        for key, val in style["writing"].items():
            blocks.append(f"- {key}: {val}")

    if session:
        from rudra.domains.writing import DraftService

        drafts = await DraftService(session, user_id).list_drafts(limit=5)
        if drafts:
            blocks.append("\n## Draft Queue\n")
            for d in drafts:
                blocks.append(f"- [{d.status}] {d.title} (v{d.current_version})")
                sources_used.append({"type": "draft", "title": d.title, "id": str(d.id)})
            return

    drafts = await data.list_artifacts(AgentType.WRITING, artifact_type="draft", limit=5)
    if drafts:
        blocks.append("\n## Draft Queue\n")
        for d in drafts:
            meta = d.metadata_ or {}
            blocks.append(f"- [{meta.get('format', 'draft')}] {d.title}: {d.content[:140]}")
            sources_used.append({"type": "draft", "title": d.title, "id": str(d.id)})


async def _enrich_presentation(
    session: AsyncSession,
    user_id: str,
    data: AgentDataService,
    blocks: list[str],
    sources_used: list[dict[str, str]],
) -> None:
    decks = await data.list_artifacts(AgentType.PRESENTATION, artifact_type="deck_outline", limit=4)
    if decks:
        blocks.append("\n## Deck Outlines\n")
        for deck in decks:
            meta = deck.metadata_ or {}
            blocks.append(
                f"- {deck.title} ({meta.get('slides', '?')} slides): {deck.content[:180]}"
            )
            sources_used.append({"type": "deck", "title": deck.title, "id": str(deck.id)})

    reports = await ResearchReportService(session, user_id).list_recent(limit=3)
    if reports:
        blocks.append("\n## Source Research for Slides\n")
        for r in reports:
            blocks.append(f"- {r.title} (confidence {r.confidence_score:.2f})")
            sources_used.append({"type": "research_report", "title": r.title})


async def _enrich_operations(
    data: AgentDataService,
    blocks: list[str],
    sources_used: list[dict[str, str]],
    session: AsyncSession | None = None,
    user_id: str = "owner",
) -> None:
    vendors = await data.list_artifacts(AgentType.OPERATIONS, artifact_type="vendor", limit=8)
    if vendors:
        blocks.append("\n## Vendor Roster\n")
        for v in vendors:
            meta = v.metadata_ or {}
            blocks.append(f"- [{meta.get('category', 'vendor')}] {v.title}: {v.content[:120]}")
            sources_used.append({"type": "vendor", "title": v.title, "id": str(v.id)})

    if session:
        from rudra.domains.operations import OpsRunbookService

        brief = await OpsRunbookService(session, user_id).runbook_brief()
        if brief["maintenance_due"]:
            blocks.append("\n## Maintenance Due\n")
            for m in brief["maintenance_due"][:5]:
                blocks.append(f"- {m['title']} (due {m['next_due']})")
        if brief["open_sla"]:
            blocks.append("\n## Open SLA Events\n")
            for e in brief["open_sla"][:5]:
                blocks.append(f"- {e['vendor']}: {e['type']}")
        if brief["maintenance_due"] or brief["open_sla"]:
            return

    maintenance = await data.list_artifacts(
        AgentType.OPERATIONS, artifact_type="maintenance", limit=8
    )
    if maintenance:
        blocks.append("\n## Maintenance Schedule\n")
        for m in maintenance:
            meta = m.metadata_ or {}
            blocks.append(
                f"- [{m.status}] {m.title} — next due {meta.get('next_due', 'TBD')}: {m.content[:100]}"
            )
            sources_used.append({"type": "maintenance", "title": m.title, "id": str(m.id)})
