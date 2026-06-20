"""Seed encoded domain data for all nine agent phases."""

from __future__ import annotations

from rudra.agents.data.service import AgentDataService
from rudra.agents.types import AgentType
from rudra.memory.models.memory import MemoryType
from rudra.memory.service import MemoryService
from rudra.research.reports import ResearchReportService

SEED_PREFERENCES: list[dict] = [
    {"category": "executive", "key": "deep_work_block", "value": "09:00–11:00 — no meetings", "source": "seed"},
    {"category": "executive", "key": "priority_framework", "value": "Rudra OS > Jobsflix > *Sphere ventures", "source": "seed"},
    {"category": "executive", "key": "briefing_time", "value": "07:30 local — scan calendar + project dashboard", "source": "seed"},
    {"category": "dining", "key": "cuisine", "value": "Japanese omakase, modern Indian, Mediterranean", "source": "seed"},
    {"category": "dining", "key": "seating", "value": "Quiet corner, minimal noise, chef's counter when available", "source": "seed"},
    {"category": "hotels", "key": "brand_tier", "value": "Aman, Four Seasons, Mandarin Oriental, boutique with character", "source": "seed"},
    {"category": "hotels", "key": "room", "value": "High floor, city or ocean view, late checkout when possible", "source": "seed"},
    {"category": "travel", "key": "cabin", "value": "Business or first on long-haul; aisle preferred", "source": "seed"},
    {"category": "travel", "key": "pace", "value": "Max 2 cities per week; buffer days between regions", "source": "seed"},
    {"category": "writing", "key": "tone_default", "value": "Direct, confident, warm — no corporate filler", "source": "seed"},
    {"category": "writing", "key": "email_signoff", "value": "Best,\nVikram", "source": "seed"},
    {"category": "writing", "key": "avoid", "value": "Synergy, leverage, circle back, hope this finds you well", "source": "seed"},
    {"category": "luxury", "key": "watch_interest", "value": "Patek Nautilus, AP Royal Oak, independent horology", "source": "seed"},
    {"category": "luxury", "key": "collectibles", "value": "Contemporary art, rare whisky, vintage aviation memorabilia", "source": "seed"},
]

SEED_EXPERIENCE_REQUESTS: list[dict] = [
    {
        "title": "Dinner at Zuma Dubai — 4 guests",
        "content": "Private corner table, Friday 20:30. Guest dietary: one pescatarian. Confirm champagne list.",
        "metadata": {"venue": "Zuma Dubai", "party_size": 4, "date": "2026-06-20"},
    },
    {
        "title": "Aman Tokyo — 3-night suite",
        "content": "Corner suite with city view. Airport transfer + spa slot on arrival day.",
        "metadata": {"property": "Aman Tokyo", "nights": 3, "status": "pending_confirmation"},
    },
]

SEED_WATCHLIST: list[dict] = [
    {
        "title": "Patek Philippe Nautilus 5711",
        "content": "Grey dial steel. Secondary market ~$120–140k. Watch Geneva auctions Q3.",
        "metadata": {"category": "watches", "alert": "price_drop_5pct"},
    },
    {
        "title": "Aman New York Residences",
        "content": "Track new inventory and off-market resales. UHNI buyer interest rising.",
        "metadata": {"category": "hotels", "alert": "new_listing"},
    },
    {
        "title": "Gulfstream G700 charter rates",
        "content": "Monitor Dubai–London route pricing vs NetJets membership.",
        "metadata": {"category": "private_aviation", "alert": "rate_change"},
    },
]

SEED_ITINERARIES: list[dict] = [
    {
        "title": "Tokyo → Kyoto — June 2026",
        "content": (
            "Leg 1: NRT arrival Jun 18, Aman Tokyo (3n). Leg 2: Shinkansen to Kyoto Jun 21, "
            "Aman Kyoto (2n). Visa: JP visa-free 90d. Backup: HND if NRT delays."
        ),
        "metadata": {"legs": 2, "start": "2026-06-18", "status": "planning"},
    },
    {
        "title": "Dubai board week — Q3",
        "content": "Mon–Wed meetings. Thu desert experience. Fri departure DXB→LHR business.",
        "metadata": {"legs": 1, "start": "2026-09-08", "status": "draft"},
    },
]

SEED_DRAFTS: list[dict] = [
    {
        "title": "Board update — Rudra OS milestone",
        "content": (
            "Team,\n\nRudra OS Phase 1–5 shipped: auth, knowledge graph, project dashboard, "
            "document brain, and daily briefing. Next: specialist agent depth.\n\nBest,\nVikram"
        ),
        "metadata": {"format": "email", "tone": "executive"},
    },
    {
        "title": "Investor note — Jobsflix traction",
        "content": "Draft: Q2 user growth + monetization pilots. Needs metrics from dashboard.",
        "metadata": {"format": "memo", "tone": "formal"},
    },
]

SEED_DECKS: list[dict] = [
    {
        "title": "Rudra OS — Founder Intelligence pitch",
        "content": (
            "Slide 1: Title — Rudra OS\nSlide 2: Problem — fragmented personal intelligence\n"
            "Slide 3: Solution — 9 agents + local-first memory\nSlide 4: Traction — Founder OS shipped\n"
            "Slide 5: Roadmap — agent phases 1–9\nSlide 6: Ask"
        ),
        "metadata": {"slides": 6, "audience": "investors"},
    },
]

SEED_VENDORS: list[dict] = [
    {
        "title": "Elite Aviation — charter broker",
        "content": "Primary for Gulfstream G650/G700. Contact: ops@eliteaviation.example. SLA: 4h quote.",
        "metadata": {"category": "aviation", "rating": 5},
    },
    {
        "title": "Home Systems Integrator — Mumbai",
        "content": "AV, lighting, security retainer. Quarterly maintenance included.",
        "metadata": {"category": "household", "rating": 4},
    },
]

SEED_MAINTENANCE: list[dict] = [
    {
        "title": "HVAC filter replacement",
        "content": "Every 90 days. Last done: 2026-03-01. Next due: 2026-06-01.",
        "metadata": {"frequency_days": 90, "next_due": "2026-06-01"},
        "status": "due",
    },
    {
        "title": "Vehicle service — Range Rover",
        "content": "Annual service + tyre rotation. Book 2 weeks ahead.",
        "metadata": {"frequency_days": 365, "next_due": "2026-08-15"},
        "status": "scheduled",
    },
]

SEED_RESEARCH_WATCHLIST: list[dict] = [
    {
        "topic": "Local-first AI",
        "query_template": "local-first personal AI operating systems privacy 2026",
        "ttl_days": 14,
    },
    {
        "topic": "UHNI hospitality",
        "query_template": "ultra luxury hotel openings pipeline 2026",
        "ttl_days": 30,
    },
    {
        "topic": "Agent orchestration",
        "query_template": "multi-agent routing ReAct tool use patterns",
        "ttl_days": 21,
    },
]

SEED_RESEARCH_REPORTS: list[dict] = [
    {
        "title": "Local-first AI assistants — market scan",
        "query": "local-first personal AI operating systems 2026",
        "content": (
            "Executive Summary: Privacy-first local AI is accelerating with Ollama, pgvector, "
            "and edge hardware.\nKey Findings: Single-owner OS pattern emerging; memory graphs "
            "differentiate.\nConfidence: 0.82"
        ),
        "confidence_score": 0.82,
        "citations": [{"title": "Ollama adoption trends", "url": "https://ollama.com"}],
    },
    {
        "title": "UHNI luxury hospitality — H1 2026",
        "query": "ultra luxury hotel openings 2026",
        "content": (
            "Executive Summary: Aman, Rosewood, and independent villas lead new supply.\n"
            "Key Findings: Japan and UAE highest net-new capacity.\nConfidence: 0.78"
        ),
        "confidence_score": 0.78,
        "citations": [{"title": "Luxury hotel pipeline", "url": "https://example.com/luxury"}],
    },
    {
        "title": "Agent orchestration patterns",
        "query": "multi-agent routing ReAct tool use",
        "content": (
            "Executive Summary: Router + specialist agents outperform monolithic prompts.\n"
            "Key Findings: Tool registries per domain reduce hallucination.\nConfidence: 0.85"
        ),
        "confidence_score": 0.85,
        "citations": [{"title": "ReAct paper", "url": "https://arxiv.org/abs/2210.03629"}],
    },
]

SEED_TRAVEL_MEMORIES: list[dict] = [
    {
        "title": "Tokyo visa note",
        "content": "Indian passport: visa-free tourist entry 90 days. Register Visit Japan Web before arrival.",
        "tags": ["travel", "visa", "japan"],
    },
    {
        "title": "Preferred Narita lounge",
        "content": "Star Alliance lounge Terminal 1 — quieter than ANA lounge during peak hours.",
        "tags": ["travel", "flight", "tokyo"],
    },
]

SEED_CONCIERGE_MEMORIES: list[dict] = [
    {
        "title": "Standing reservation preference",
        "content": "For Dubai: Zuma, La Petite Maison, Nusr-Et. Always request same server when possible.",
        "tags": ["concierge", "dining", "dubai"],
    },
]

SEED_OPERATIONS_MEMORIES: list[dict] = [
    {
        "title": "Household vendor SLA",
        "content": "Critical repairs: 4h response. Non-critical: 48h. Escalate via EA if breached.",
        "tags": ["operations", "vendor", "household"],
    },
]


async def seed_agent_phase_data(
    session,
    user_id: str = "owner",
) -> dict[str, int]:
    """Idempotent seed of preferences, artifacts, reports, and tagged memories."""
    data = AgentDataService(session, user_id)
    memory = MemoryService(session, user_id)
    reports = ResearchReportService(session, user_id)
    counts: dict[str, int] = {}

    for pref in SEED_PREFERENCES:
        await data.upsert_preference(**pref)
    counts["preferences"] = len(SEED_PREFERENCES)

    async def _seed_artifacts(agent: AgentType, artifact_type: str, items: list[dict]) -> int:
        existing = await data.list_artifacts(agent, artifact_type=artifact_type, limit=1)
        if existing:
            return 0
        for item in items:
            await data.create_artifact(
                agent,
                artifact_type,
                item["title"],
                item["content"],
                metadata=item.get("metadata"),
                status=item.get("status", "active"),
            )
        return len(items)

    counts["experience_requests"] = await _seed_artifacts(
        AgentType.CONCIERGE, "experience_request", SEED_EXPERIENCE_REQUESTS
    )
    counts["watchlist"] = await _seed_artifacts(
        AgentType.LUXURY_ANALYST, "watchlist", SEED_WATCHLIST
    )
    counts["itineraries"] = await _seed_artifacts(
        AgentType.TRAVEL, "itinerary", SEED_ITINERARIES
    )
    counts["drafts"] = await _seed_artifacts(
        AgentType.WRITING, "draft", SEED_DRAFTS
    )
    counts["decks"] = await _seed_artifacts(
        AgentType.PRESENTATION, "deck_outline", SEED_DECKS
    )
    counts["vendors"] = await _seed_artifacts(
        AgentType.OPERATIONS, "vendor", SEED_VENDORS
    )
    counts["maintenance"] = await _seed_artifacts(
        AgentType.OPERATIONS, "maintenance", SEED_MAINTENANCE
    )

    recent_reports = await reports.list_recent(limit=1)
    if not recent_reports:
        for item in SEED_RESEARCH_REPORTS:
            await reports.save(**item)
        counts["research_reports"] = len(SEED_RESEARCH_REPORTS)
    else:
        counts["research_reports"] = 0

    existing_watchlist = await reports.list_watchlist()
    if not existing_watchlist:
        for item in SEED_RESEARCH_WATCHLIST:
            await reports.add_watchlist(
                item["topic"],
                item["query_template"],
                ttl_days=item.get("ttl_days", 30),
            )
        counts["research_watchlist"] = len(SEED_RESEARCH_WATCHLIST)
    else:
        counts["research_watchlist"] = 0

    async def _seed_memories(items: list[dict]) -> int:
        seeded = 0
        for item in items:
            recent = await memory.list_recent(limit=50)
            if any(m.title == item["title"] for m in recent):
                continue
            await memory.create(
                MemoryType.SEMANTIC,
                title=item["title"],
                content=item["content"],
                tags=item.get("tags", []),
                source="agent_seed",
                importance=0.7,
            )
            seeded += 1
        return seeded

    counts["travel_memories"] = await _seed_memories(SEED_TRAVEL_MEMORIES)
    counts["concierge_memories"] = await _seed_memories(SEED_CONCIERGE_MEMORIES)
    counts["operations_memories"] = await _seed_memories(SEED_OPERATIONS_MEMORIES)

    from rudra.domains.concierge import ExperienceService
    from rudra.domains.travel import TripService

    existing_cg = await ExperienceService(session, user_id).list_recent(limit=1)
    if not existing_cg:
        await ExperienceService(session, user_id).log_request(
            "Friday omakase — 4 guests",
            "Private counter, one pescatarian. Confirm champagne list.",
            venue_name="Zuma Dubai",
            party_size=4,
            scheduled_at="2026-06-20T20:30",
        )
        counts["concierge_requests"] = 1
    else:
        counts["concierge_requests"] = 0

    existing_trips = await TripService(session, user_id).list_trips(limit=1)
    if not existing_trips:
        await TripService(session, user_id).create_trip(
            "Tokyo → Kyoto — June 2026",
            [{"destination": "Tokyo", "starts_at": "2026-06-18"}, {"destination": "Kyoto", "starts_at": "2026-06-21"}],
        )
        counts["travel_trips"] = 1
    else:
        counts["travel_trips"] = 0

    return counts
