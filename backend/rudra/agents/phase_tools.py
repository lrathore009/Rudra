"""Phase-specific tool handlers for all nine specialist agents."""

from __future__ import annotations

import json
from typing import Any

from rudra.agents.data.service import AgentDataService
from rudra.agents.tools import ToolContext
from rudra.agents.types import AgentType
from rudra.graph.service import GraphService
from rudra.integrations.service import BriefingService
from rudra.memory.models.memory import MemoryType
from rudra.memory.service import MemoryService
from rudra.projects.service import ProjectService
from rudra.research.reports import ResearchReportService


def _require_db(ctx: ToolContext):
    if ctx.db is None:
        raise RuntimeError("database unavailable")


# ─── Phase 1: Executive Assistant ───────────────────────────────────────────

async def get_daily_briefing(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    briefing = await BriefingService(ctx.db, ctx.user_id).generate_daily()
    return briefing.content


async def list_active_projects(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    dashboard = await ProjectService(ctx.db, ctx.user_id).dashboard()
    lines = [f"Stale: {dashboard['stale_count']} · Blocked: {dashboard['blocked_count']}", ""]
    for card in dashboard["projects"][:10]:
        lines.append(
            f"- P{card['priority']} {card['name']} ({card['progress_percent']}%): {card['next_action']}"
        )
    return "\n".join(lines) or "No active projects."


async def summarize_day(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    briefing = await get_daily_briefing({}, ctx)
    projects = await list_active_projects({}, ctx)
    return f"{briefing}\n\n---\n\n## Project Stack\n{projects}"


async def get_command_stack(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.integrations.executive import ExecutiveCommandService

    stack = await ExecutiveCommandService(ctx.db, ctx.user_id).get_command_stack()
    return json.dumps(stack, indent=2, default=str)[:8000]


async def sync_executive_sources(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.integrations.executive import ExecutiveCommandService

    counts = await ExecutiveCommandService(ctx.db, ctx.user_id).sync_all()
    return "Synced executive sources: " + ", ".join(f"{k}={v}" for k, v in counts.items())


async def list_commitments(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.integrations.executive import ExecutiveCommandService

    items = await ExecutiveCommandService(ctx.db, ctx.user_id).list_commitments(limit=15)
    if not items:
        return "No open commitments."
    return "\n".join(
        f"- {c['title']}" + (f" (due {c['due_at']})" if c.get("due_at") else "") for c in items
    )


async def list_connector_status(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.integrations.executive import ExecutiveCommandService

    rows = await ExecutiveCommandService(ctx.db, ctx.user_id).list_connector_status()
    return "\n".join(
        f"- {r['provider']} [{r.get('tier', '?')}]: {'connected' if r['connected'] else 'off'} — {r['detail']}"
        for r in rows
    )


# ─── Phase 2: Research Analyst ──────────────────────────────────────────────

async def save_research_report(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    title = str(args.get("title", "")).strip()
    query = str(args.get("query", "")).strip()
    content = str(args.get("content", "")).strip()
    if not title or not content:
        return 'Error: provide "title" and "content" (optional "query", "confidence").'
    confidence = float(args.get("confidence", 0.8))
    report = await ResearchReportService(ctx.db, ctx.user_id).save(
        title=title,
        query=query or title,
        content=content,
        confidence_score=confidence,
    )
    return f"Saved research report '{report.title}' (id={report.id}, confidence={confidence:.2f})."


async def search_research_library(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    query = str(args.get("query", "")).strip()
    svc = ResearchReportService(ctx.db, ctx.user_id)
    if query and args.get("hybrid", True):
        from rudra.research.hybrid import hybrid_search_reports

        hits = await hybrid_search_reports(svc, query, limit=8)
        if not hits:
            return "No research reports found."
        return "\n".join(
            f"[{i}] {r.title} (conf={r.confidence_score:.2f}, score={score:.3f}, id={r.id})\n    {r.content[:200]}"
            for i, (r, score) in enumerate(hits, 1)
        )
    reports = await svc.search(query, limit=8) if query else await svc.list_recent(limit=8)
    if not reports:
        return "No research reports found."
    return "\n".join(
        f"[{i}] {r.title} (conf={r.confidence_score:.2f}, id={r.id})\n    {r.content[:200]}"
        for i, r in enumerate(reports, 1)
    )


async def hybrid_search_library(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    query = str(args.get("query", "")).strip()
    if not query:
        return 'Error: provide "query" for hybrid search.'
    from rudra.research.hybrid import hybrid_search_reports

    svc = ResearchReportService(ctx.db, ctx.user_id)
    hits = await hybrid_search_reports(svc, query, limit=int(args.get("limit", 8)))
    if not hits:
        return "No hybrid matches."
    return "\n".join(
        f"[{i}] {r.title} (rrf={score:.3f}, conf={r.confidence_score:.2f})\n    {r.content[:180]}"
        for i, (r, score) in enumerate(hits, 1)
    )


async def add_research_watchlist(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    topic = str(args.get("topic", "")).strip()
    query_template = str(args.get("query_template", "")).strip() or topic
    if not topic:
        return 'Error: provide "topic" and optional "query_template", "ttl_days".'
    row = await ResearchReportService(ctx.db, ctx.user_id).add_watchlist(
        topic,
        query_template,
        ttl_days=int(args.get("ttl_days", 30)),
    )
    return f"Added research watchlist topic '{row.topic}' (id={row.id})."


async def research_library_trends(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    trends = await ResearchReportService(ctx.db, ctx.user_id).trends()
    watchlist = await ResearchReportService(ctx.db, ctx.user_id).list_watchlist()
    lines = [
        f"Reports: {trends['count']} · avg confidence {trends['avg_confidence']:.2f} · stale {trends['stale_count']}",
    ]
    for w in trends.get("weekly", [])[-4:]:
        lines.append(f"- Week {w['week']}: {w['count']} reports, avg {w['avg_confidence']:.2f}")
    if watchlist:
        lines.append("\nWatchlist:")
        for w in watchlist[:8]:
            lines.append(f"- {w.topic}: {w.query_template[:80]}")
    return "\n".join(lines)


# ─── Phase 3: Concierge ─────────────────────────────────────────────────────

async def search_preferences(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    query = str(args.get("query", "")).strip()
    category = str(args.get("category", "")).strip() or None
    prefs = await AgentDataService(ctx.db, ctx.user_id).list_preferences(
        category=category, query=query or None, limit=20
    )
    if not prefs:
        return "No matching preferences."
    return "\n".join(f"- [{p.category}] {p.key}: {p.value}" for p in prefs)


async def log_experience_request(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.concierge import ExperienceService

    title = str(args.get("title", "")).strip()
    details = str(args.get("details", "")).strip()
    if not title or not details:
        return 'Error: provide "title" and "details".'
    row = await ExperienceService(ctx.db, ctx.user_id).log_request(
        title,
        details,
        venue_name=str(args.get("venue", "")).strip() or None,
        party_size=int(args["party_size"]) if args.get("party_size") else None,
        scheduled_at=str(args.get("scheduled_at", "")).strip() or None,
    )
    return f"Logged experience request '{row.title}' (id={row.id}, status={row.status})."


async def update_request_status(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from uuid import UUID

    from rudra.domains.concierge import ExperienceService

    rid = str(args.get("request_id", "")).strip()
    status = str(args.get("status", "")).strip()
    if not rid or not status:
        return 'Error: provide "request_id" and "status".'
    row = await ExperienceService(ctx.db, ctx.user_id).update_status(UUID(rid), status)
    if not row:
        return "Request not found."
    return f"Updated '{row.title}' → {row.status}."


async def recommend_experiences(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.concierge import ExperienceService

    category = str(args.get("category", "dining")).strip()
    recs = await ExperienceService(ctx.db, ctx.user_id).recommend(category)
    if not recs:
        return "No preference-based recommendations."
    return "\n".join(f"- [{r['category']}] {r['preference']}: {r['value']}" for r in recs)


async def link_venue_entity(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from uuid import UUID

    from rudra.domains.concierge import ExperienceService

    rid = str(args.get("request_id", "")).strip()
    venue = str(args.get("venue_name", "")).strip()
    if not rid or not venue:
        return 'Error: provide "request_id" and "venue_name".'
    row = await ExperienceService(ctx.db, ctx.user_id).link_venue(UUID(rid), venue)
    if not row:
        return "Request not found."
    return f"Linked '{row.title}' to venue '{venue}' (entity={row.entity_id})."


# ─── Phase 4: Luxury Analyst ────────────────────────────────────────────────

async def luxury_market_brief(args: dict[str, Any], ctx: ToolContext) -> str:
    from rudra.knowledge.luxury import LuxuryCategory

    subject = str(args.get("subject", "")).strip() or "luxury market overview"
    category_raw = str(args.get("category", "wealth_lifestyle")).strip().lower()
    try:
        category = LuxuryCategory(category_raw)
    except ValueError:
        category = LuxuryCategory.LIFESTYLE
    if ctx.db:
        from rudra.domains.luxury_desk import LuxuryDeskService

        result = await LuxuryDeskService(ctx.db, ctx.user_id).brief_with_library(subject, category)
        tag = " (cached)" if result.get("from_library") else ""
        return result["briefing"][:2000] + tag
    from rudra.knowledge.luxury import LuxuryIntelligenceService

    intel = await LuxuryIntelligenceService().research(subject, category, depth="standard")
    return intel.briefing[:2000]


async def update_watchlist(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    title = str(args.get("title", "")).strip()
    notes = str(args.get("notes", "")).strip()
    category = str(args.get("category", "lifestyle")).strip()
    if not title:
        return 'Error: provide "title" and optional "notes", "category".'
    artifact = await AgentDataService(ctx.db, ctx.user_id).create_artifact(
        AgentType.LUXURY_ANALYST,
        "watchlist",
        title,
        notes or title,
        metadata={"category": category, "alert": "manual"},
    )
    return f"Added '{artifact.title}' to luxury watchlist (id={artifact.id})."


async def set_price_alert(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.luxury_desk import LuxuryDeskService

    title = str(args.get("title", "")).strip()
    if not title:
        return 'Error: provide watchlist "title".'
    alert = await LuxuryDeskService(ctx.db, ctx.user_id).set_alert(
        title,
        alert_type=str(args.get("alert_type", "price_change")),
        threshold=float(args["threshold"]) if args.get("threshold") else None,
    )
    return f"Price alert set for '{alert.watchlist_title}' (id={alert.id})."


async def luxury_desk_trends(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.luxury_desk import LuxuryDeskService

    trends = await LuxuryDeskService(ctx.db, ctx.user_id).desk_trends()
    lines = [
        f"Snapshots: {trends['count']} · avg exclusivity {trends['avg_exclusivity']:.2f} · watchlist {trends['watchlist_count']}"
    ]
    for r in trends.get("recent", []):
        lines.append(f"- {r['subject']} ({r['category']})")
    return "\n".join(lines)


# ─── Phase 5: Travel ────────────────────────────────────────────────────────

async def create_itinerary(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    title = str(args.get("title", "")).strip()
    plan = str(args.get("plan", "")).strip()
    if not title or not plan:
        return 'Error: provide "title" and "plan" (day-by-day itinerary text).'
    artifact = await AgentDataService(ctx.db, ctx.user_id).create_artifact(
        AgentType.TRAVEL,
        "itinerary",
        title,
        plan,
        metadata={"status": "planning", "source": "tool"},
    )
    await MemoryService(ctx.db, ctx.user_id).create(
        MemoryType.SEMANTIC,
        title=f"Itinerary: {title}",
        content=plan,
        tags=["travel", "itinerary"],
        source="travel_agent",
    )
    return f"Created itinerary '{artifact.title}' (id={artifact.id}) and linked travel memory."


async def search_travel_memories(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    query = str(args.get("query", "")).strip() or "travel"
    mem_svc = MemoryService(ctx.db, ctx.user_id)
    tagged = await mem_svc.search_by_tags(
        ["travel", "itinerary", "visa", "flight", "hotel"], limit=8
    )
    semantic = await mem_svc.search_by_text(query, limit=5)
    seen: set = set()
    lines: list[str] = []
    for mem_obj in tagged:
        if mem_obj.id in seen:
            continue
        seen.add(mem_obj.id)
        lines.append(f"- {mem_obj.title}: {mem_obj.content[:180]}")
    for mem_obj, score in semantic:
        if mem_obj.id in seen:
            continue
        seen.add(mem_obj.id)
        lines.append(f"- ({score:.2f}) {mem_obj.title}: {mem_obj.content[:180]}")
    itineraries = await AgentDataService(ctx.db, ctx.user_id).list_artifacts(
        AgentType.TRAVEL, artifact_type="itinerary", limit=5
    )
    for itin in itineraries:
        lines.append(f"- [itinerary] {itin.title}: {itin.content[:180]}")
    return "\n".join(lines) if lines else "No travel memories or itineraries found."


async def create_trip_project(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.travel import TripService

    title = str(args.get("title", "")).strip()
    destinations = str(args.get("destinations", "")).strip()
    if not title or not destinations:
        return 'Error: provide "title" and "destinations" (comma-separated).'
    legs = [{"destination": d.strip()} for d in destinations.split(",") if d.strip()]
    trip = await TripService(ctx.db, ctx.user_id).create_trip(title, legs)
    return f"Created trip '{trip.title}' (id={trip.id}, project={trip.project_id})."


async def visa_requirements(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.travel import TripService

    dest = str(args.get("destination", "")).strip()
    if not dest:
        return 'Error: provide "destination".'
    items = await TripService(ctx.db, ctx.user_id).visa_requirements(
        dest, passport=str(args.get("passport", "Indian"))
    )
    return "\n".join(f"- {i}" for i in items)


async def upcoming_travel_brief(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.travel import TripService

    brief = await TripService(ctx.db, ctx.user_id).travel_brief()
    lines = ["## Trips"] + [f"- {t['title']} ({t['status']})" for t in brief["trips"]]
    lines.append("\n## Upcoming legs")
    for leg in brief["upcoming_legs"]:
        lines.append(f"- {leg['destination']} @ {leg.get('starts_at', 'TBD')}")
    return "\n".join(lines)


# ─── Phase 6: Knowledge Librarian ───────────────────────────────────────────

async def graph_neighbors(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from uuid import UUID

    entity_name = str(args.get("entity_name", "")).strip()
    entity_id_raw = str(args.get("entity_id", "")).strip()
    graph = GraphService(ctx.db, ctx.user_id)
    entity = None
    if entity_id_raw:
        try:
            entity = await graph.get_entity(UUID(entity_id_raw))
        except ValueError:
            pass
    if entity is None and entity_name:
        entity = await graph.find_entity_by_name(entity_name)
    if entity is None:
        return 'Error: provide "entity_name" or "entity_id".'
    neighbors = await graph.get_neighbors(entity.id, limit=12)
    if not neighbors:
        return f"No graph neighbors for '{entity.name}'."
    return f"Neighbors of {entity.name}:\n" + "\n".join(
        f"- {n['relation']} → {n['name']} ({n['type']}, id={n['id']})" for n in neighbors
    )


async def connect_entities(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    source = str(args.get("source", "")).strip()
    target = str(args.get("target", "")).strip()
    relation = str(args.get("relation", "related_to")).strip()
    if not source or not target:
        return 'Error: provide "source", "target", optional "relation".'
    graph = GraphService(ctx.db, ctx.user_id)
    src = await graph.find_entity_by_name(source)
    tgt = await graph.find_entity_by_name(target)
    if not src:
        src = await graph.get_or_create_entity(source, "topic")
    if not tgt:
        tgt = await graph.get_or_create_entity(target, "topic")
    rel = await graph.create_relationship(src.id, tgt.id, relation)
    return f"Connected {src.name} —[{relation}]→ {tgt.name} (rel id={rel.id})."


async def unified_search(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.librarian import LibrarianRetrievalService

    query = str(args.get("query", "")).strip()
    if not query:
        return 'Error: provide "query".'
    hits = await LibrarianRetrievalService(ctx.db, ctx.user_id).unified_search(query, limit=8)
    if not hits:
        return "No unified matches."
    return "\n".join(
        f"[{i}] [{h['type']}] {h['title']} (score={h['score']})\n    {h['snippet'][:160]}"
        for i, h in enumerate(hits, 1)
    )


async def librarian_answer(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.librarian import LibrarianRetrievalService

    query = str(args.get("query", "")).strip()
    if not query:
        return 'Error: provide "query".'
    result = await LibrarianRetrievalService(ctx.db, ctx.user_id).answer(query)
    return result["answer"][:6000]


async def retrieval_trace(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.librarian import LibrarianRetrievalService

    traces = await LibrarianRetrievalService(ctx.db, ctx.user_id).recent_traces(limit=5)
    if not traces:
        return "No retrieval traces yet."
    return "\n".join(
        f"- {t.query[:80]} ({t.latency_ms}ms, {len(t.sources or [])} sources)" for t in traces
    )


# ─── Phase 7: Writing ───────────────────────────────────────────────────────

async def get_writing_style(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    profile = await AgentDataService(ctx.db, ctx.user_id).preference_profile(("writing",))
    writing = profile.get("writing", {})
    if not writing:
        return "No writing style preferences stored yet."
    return json.dumps(writing, indent=2)


async def save_draft(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.writing import DraftService

    title = str(args.get("title", "")).strip()
    content = str(args.get("content", "")).strip()
    fmt = str(args.get("format", "email")).strip()
    if not title or not content:
        return 'Error: provide "title" and "content".'
    draft = await DraftService(ctx.db, ctx.user_id).save(
        title, content, fmt=fmt, tone=str(args.get("tone", "")).strip() or None
    )
    return f"Saved draft '{draft.title}' (id={draft.id}, v{draft.current_version})."


async def refine_tone(args: dict[str, Any], ctx: ToolContext) -> str:
    style = await get_writing_style(args, ctx)
    text = str(args.get("text", "")).strip()
    tone = str(args.get("tone", "")).strip()
    if not text:
        return 'Error: provide "text" to refine.'
    return (
        f"Writing style profile:\n{style}\n\n"
        f"Requested tone: {tone or 'default'}\n\n"
        f"Draft to refine:\n{text}\n\n"
        "Apply the profile: remove filler, match sign-off and avoid-list, keep direct voice."
    )


async def rewrite_draft(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from uuid import UUID

    from rudra.domains.writing import DraftService

    did = str(args.get("draft_id", "")).strip()
    text = str(args.get("text", "")).strip()
    if not did or not text:
        return 'Error: provide "draft_id" and "text".'
    draft = await DraftService(ctx.db, ctx.user_id).rewrite(
        UUID(did), text, brain=ctx.brain, tone=str(args.get("tone", "")).strip() or None
    )
    if not draft:
        return "Draft not found."
    return f"Rewrote draft v{draft.current_version}: {draft.content[:1500]}"


async def list_drafts(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.writing import DraftService

    drafts = await DraftService(ctx.db, ctx.user_id).list_drafts(limit=10)
    if not drafts:
        return "No drafts in queue."
    return "\n".join(
        f"- [{d.status}] {d.title} (v{d.current_version}, id={d.id}): {d.content[:100]}"
        for d in drafts
    )


async def export_draft(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from uuid import UUID

    from rudra.domains.writing import DraftService

    did = str(args.get("draft_id", "")).strip()
    if not did:
        return 'Error: provide "draft_id".'
    md = await DraftService(ctx.db, ctx.user_id).export_markdown(UUID(did))
    return md or "Draft not found."


# ─── Phase 8: Presentation ──────────────────────────────────────────────────

async def create_deck_outline(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.presentation import DeckService

    title = str(args.get("title", "")).strip()
    outline = str(args.get("outline", "")).strip()
    slides = int(args.get("slides", 6))
    if not title or not outline:
        return 'Error: provide "title" and "outline" (slide bullets).'
    deck = await DeckService(ctx.db, ctx.user_id).create_outline(
        title, outline, audience=str(args.get("audience", "executive")), slides=slides
    )
    return f"Saved deck '{deck.title}' ({deck.slide_count} slides, id={deck.id})."


async def pull_research_slides(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    query = str(args.get("query", "")).strip()
    svc = ResearchReportService(ctx.db, ctx.user_id)
    if query:
        from rudra.research.hybrid import hybrid_search_reports

        hits = await hybrid_search_reports(svc, query, limit=5)
        reports = [r for r, _ in hits]
    else:
        reports = await svc.list_recent(limit=5)
    if not reports:
        return "No research reports available for slide sourcing."
    lines = ["Research sources for slides:"]
    for r in reports:
        lines.append(f"\n## {r.title} (confidence {r.confidence_score:.2f})")
        lines.append(r.content[:600])
    return "\n".join(lines)


async def build_deck_from_sources(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.presentation import DeckService

    title = str(args.get("title", "")).strip()
    query = str(args.get("query", "")).strip()
    if not title or not query:
        return 'Error: provide "title" and "query".'
    deck = await DeckService(ctx.db, ctx.user_id).build_from_sources(
        title, query, audience=str(args.get("audience", "executive")), slide_count=int(args.get("slides", 6))
    )
    return f"Built deck '{deck.title}' with {deck.slide_count} slides (id={deck.id})."


async def export_deck_markdown(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from uuid import UUID

    from rudra.domains.presentation import DeckService

    did = str(args.get("deck_id", "")).strip()
    if not did:
        return 'Error: provide "deck_id".'
    md = await DeckService(ctx.db, ctx.user_id).export_markdown(UUID(did))
    return md or "Deck not found."


async def deck_workspace_status(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.presentation import DeckService

    decks = await DeckService(ctx.db, ctx.user_id).list_decks(limit=8)
    if not decks:
        return "No decks in workspace."
    return "\n".join(
        f"- {d.title} ({d.slide_count} slides, {d.status}, id={d.id})" for d in decks
    )

async def list_vendors(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    vendors = await AgentDataService(ctx.db, ctx.user_id).list_artifacts(
        AgentType.OPERATIONS, artifact_type="vendor", limit=20
    )
    if not vendors:
        return "No vendors in roster."
    return "\n".join(
        f"- {v.title}: {v.content[:160]}" for v in vendors
    )


async def create_ops_task(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    title = str(args.get("title", "")).strip()
    details = str(args.get("details", "")).strip()
    project_name = str(args.get("project", "Household Operations")).strip()
    if not title:
        return 'Error: provide "title" and optional "details", "project".'
    projects = ProjectService(ctx.db, ctx.user_id)
    project = await projects.get_by_name(project_name)
    if project is None:
        project = await projects.create_project(
            {
                "name": project_name,
                "description": "Personal operations runbook",
                "status": "active",
                "priority": 3,
                "category": "operations",
            }
        )
    task = await projects.create_task(
        project.id,
        {"title": title, "description": details, "status": "todo", "priority": 2},
    )
    return f"Created ops task '{task.title}' in project '{project.name}' (task id={task.id})."


async def maintenance_schedule(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    items = await AgentDataService(ctx.db, ctx.user_id).list_artifacts(
        AgentType.OPERATIONS, artifact_type="maintenance", limit=20
    )
    if not items:
        return "No maintenance items scheduled."
    lines = []
    for item in items:
        meta = item.metadata_ or {}
        lines.append(
            f"- [{item.status}] {item.title} — due {meta.get('next_due', 'TBD')}: {item.content[:120]}"
        )
    return "\n".join(lines)


async def log_vendor_interaction(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.operations import OpsRunbookService

    vendor = str(args.get("vendor", "")).strip()
    notes = str(args.get("notes", "")).strip()
    if not vendor:
        return 'Error: provide "vendor" and "notes".'
    row = await OpsRunbookService(ctx.db, ctx.user_id).log_vendor_interaction(vendor, notes)
    return f"Logged {row.interaction_type} with {row.vendor_name} (id={row.id})."


async def sla_status(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.operations import OpsRunbookService

    brief = await OpsRunbookService(ctx.db, ctx.user_id).runbook_brief()
    lines = [f"Vendors tracked: {brief['vendor_count']}", "", "## Maintenance due"]
    for m in brief["maintenance_due"]:
        lines.append(f"- {m['title']} (due {m['next_due']})")
    lines.append("\n## Open SLA")
    for e in brief["open_sla"]:
        lines.append(f"- {e['vendor']}: {e['type']} due {e.get('due_at', 'TBD')}")
    return "\n".join(lines)


async def escalate_ops_issue(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.operations import OpsRunbookService

    vendor = str(args.get("vendor", "")).strip()
    issue = str(args.get("issue", "")).strip()
    if not vendor or not issue:
        return 'Error: provide "vendor" and "issue".'
    event = await OpsRunbookService(ctx.db, ctx.user_id).escalate(vendor, issue)
    return f"Escalated {vendor} (sla id={event.id})."


async def ops_runbook_brief(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.domains.operations import OpsRunbookService

    brief = await OpsRunbookService(ctx.db, ctx.user_id).runbook_brief()
    return json.dumps(brief, indent=2, default=str)[:4000]


async def sync_free_sources(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.agents.types import AgentType
    from rudra.integrations.executive import ExecutiveCommandService
    from rudra.jarvis.connectors.agent_free_sources.registry import AgentFreeSourcesRegistry

    agent_slug = str(args.get("agent", "research_analyst")).strip()
    try:
        agent_type = AgentType(agent_slug)
    except ValueError:
        return f'Error: unknown agent "{agent_slug}".'
    if agent_type == AgentType.EXECUTIVE_ASSISTANT:
        counts = await ExecutiveCommandService(ctx.db, ctx.user_id).sync_all()
        return "Synced executive sources: " + ", ".join(f"{k}={v}" for k, v in counts.items())
    registry = AgentFreeSourcesRegistry()
    result = await registry.sync(ctx.db, ctx.user_id, agent_type, str(args.get("query", "")))
    return f"Synced {result.get('synced', 0)} free intel items for {agent_type.value}."


async def list_free_source_status(args: dict[str, Any], ctx: ToolContext) -> str:
    _require_db(ctx)
    from rudra.agents.types import AgentType
    from rudra.integrations.executive import ExecutiveCommandService
    from rudra.jarvis.connectors.agent_free_sources.registry import AgentFreeSourcesRegistry

    agent_slug = args.get("agent")
    registry = AgentFreeSourcesRegistry()
    if agent_slug:
        try:
            at = AgentType(str(agent_slug))
        except ValueError:
            return f'Error: unknown agent "{agent_slug}".'
        if at == AgentType.EXECUTIVE_ASSISTANT:
            exec_rows = await ExecutiveCommandService(ctx.db, ctx.user_id).list_connector_status()
            rows = [
                {"agent": "executive_assistant", "source_id": r["provider"], "name": r["provider"], "connected": r["connected"]}
                for r in exec_rows
            ]
        else:
            rows = registry.list_status(at)
        return json.dumps(rows, indent=2)[:4000]

    rows = registry.list_status()
    exec_rows = await ExecutiveCommandService(ctx.db, ctx.user_id).list_connector_status()
    rows.extend(
        {"agent": "executive_assistant", "source_id": r["provider"], "name": r["provider"], "connected": r["connected"]}
        for r in exec_rows
    )
    return json.dumps(rows, indent=2)[:8000]
