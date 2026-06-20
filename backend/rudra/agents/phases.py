"""Agent maturity phases — one dedicated upgrade track per specialist agent.

Phases 1–9 continue after the Founder OS upgrade (auth, graph, projects,
documents, integrations). Each phase deepens a single agent with domain tools,
context wiring, and HUD affordances.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from rudra.agents.types import AgentType


class PhaseStatus(str, Enum):
    """Lifecycle of an agent phase."""

    FOUNDATION = "foundation"  # routing, prompt, basic context — shipped
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


@dataclass(frozen=True)
class AgentPhase:
    number: int
    title: str
    goal: str
    status: PhaseStatus
    deliverables: tuple[str, ...]
    tools: tuple[str, ...]
    hud: str
    depends_on: tuple[str, ...] = ()


AGENT_PHASES: dict[AgentType, AgentPhase] = {
    AgentType.EXECUTIVE_ASSISTANT: AgentPhase(
        number=1,
        title="Executive Command Center",
        goal="Turn the EA into a daily command hub wired to briefing, calendar, and project priorities.",
        status=PhaseStatus.COMPLETE,
        deliverables=(
            "Inject daily briefing + active projects into EA context",
            "Tools: get_daily_briefing, list_active_projects, summarize_day",
            "HUD: priority stack + today's commitments strip",
        ),
        tools=(
            "get_daily_briefing",
            "list_active_projects",
            "summarize_day",
            "get_command_stack",
            "sync_executive_sources",
            "list_commitments",
            "list_connector_status",
        ),
        hud="Priority stack · today's commitments",
        depends_on=("Integrations (Phase 5)", "Project OS (Phase 3)"),
    ),
    AgentType.RESEARCH_ANALYST: AgentPhase(
        number=2,
        title="Research Library",
        goal="Persist, retrieve, and cite past research reports as a personal intelligence archive.",
        status=PhaseStatus.COMPLETE,
        deliverables=(
            "Unified pipeline: /research auto-saves to library with cache",
            "Hybrid retrieval: keyword + vector RRF on reports",
            "Watchlist operators + Jarvis spoken research brief",
            "Connectors: arXiv, RSS, EDGAR, documents, licensed feeds",
            "HUD: ResearchLibraryPanel with trends and watchlist",
            "Cross-agent: EA briefing, presentation slides, graph linking",
            "Telemetry jobs + federation sync for reports",
            "Tools: save, search, hybrid, watchlist, trends",
        ),
        tools=(
            "save_research_report",
            "search_research_library",
            "hybrid_search_library",
            "add_research_watchlist",
            "research_library_trends",
            "sync_free_sources",
            "list_free_source_status",
        ),
        hud="Research history · confidence trends · watchlist",
        depends_on=("Research engine", "Knowledge graph"),
    ),
    AgentType.CONCIERGE: AgentPhase(
        number=3,
        title="Experience Concierge",
        goal="Track reservations, preferences, and luxury experiences via the knowledge graph.",
        status=PhaseStatus.COMPLETE,
        deliverables=(
            "Unified ExperienceService pipeline with graph-linked venues",
            "Hybrid preference + request retrieval",
            "Operators: monitor_concierge_requests + spoken brief",
            "Connectors: Gmail/Notion intake scaffolds",
            "HUD: ExperienceConciergePanel",
            "Cross-agent: EA briefing, Travel legs, Luxury venues",
            "Federation sync for concierge requests",
            "Tools: log, status, recommend, link_venue",
        ),
        tools=(
            "search_preferences",
            "log_experience_request",
            "update_request_status",
            "recommend_experiences",
            "link_venue_entity",
            "sync_free_sources",
            "list_free_source_status",
        ),
        hud="Open requests · preference picks · venue links",
        depends_on=("Knowledge graph", "Unified retrieval (Phase 6)"),
    ),
    AgentType.LUXURY_ANALYST: AgentPhase(
        number=4,
        title="Luxury Market Desk",
        goal="Deliver entity-linked market briefings, watchlists, and category alerts for UHNI intel.",
        status=PhaseStatus.COMPLETE,
        deliverables=(
            "LuxuryDeskService with library cache + snapshots",
            "Price alerts and watchlist operators",
            "Licensed feed scaffolds (Bloomberg, Chrono24, Artsy)",
            "HUD: LuxuryMarketPanel",
            "Cross-agent: Concierge venues, Research library",
            "Federation export for snapshots",
            "Jarvis spoken luxury brief",
            "Tools: brief, watchlist, alerts, trends",
        ),
        tools=(
            "luxury_market_brief",
            "update_watchlist",
            "set_price_alert",
            "luxury_desk_trends",
            "sync_free_sources",
            "list_free_source_status",
        ),
        hud="Market ticker · watchlist alerts · exclusivity",
        depends_on=("Research library", "Knowledge graph"),
    ),
    AgentType.TRAVEL: AgentPhase(
        number=5,
        title="Itinerary Engine",
        goal="Plan multi-leg trips as project templates with graph-linked destinations and visa checklists.",
        status=PhaseStatus.COMPLETE,
        deliverables=(
            "TripService: trips, legs, project templates",
            "Visa checklist generator",
            "Operators: monitor_upcoming_legs + spoken brief",
            "HUD: ItineraryEnginePanel",
            "Cross-agent: Concierge dining, EA travel tier",
            "Federation sync for itineraries",
            "Licensed TripIt/Amadeus scaffolds",
            "Tools: create_trip, visa, upcoming brief",
        ),
        tools=(
            "create_itinerary",
            "search_travel_memories",
            "create_trip_project",
            "visa_requirements",
            "upcoming_travel_brief",
            "sync_free_sources",
            "list_free_source_status",
        ),
        hud="Active trips · leg status · visa checks",
        depends_on=("Project OS", "Knowledge graph"),
    ),
    AgentType.KNOWLEDGE_LIBRARIAN: AgentPhase(
        number=6,
        title="Unified Retrieval",
        goal="Fuse memories, documents, and graph traversal into one librarian retrieval stack.",
        status=PhaseStatus.COMPLETE,
        deliverables=(
            "Four-source RRF unified search",
            "LibrarianRetrievalService with traces",
            "Operators: knowledge digest spoken",
            "HUD: UnifiedRetrievalPanel",
            "Cross-agent: all specialists use librarian_answer",
            "Telemetry: retrieval_traces table",
            "Federation export for traces",
            "Tools: unified_search, librarian_answer, retrieval_trace",
        ),
        tools=(
            "search_documents",
            "graph_neighbors",
            "connect_entities",
            "unified_search",
            "librarian_answer",
            "retrieval_trace",
            "sync_free_sources",
            "list_free_source_status",
        ),
        hud="Retrieval trace · unified search · citations",
        depends_on=("Document brain", "Research library", "Knowledge graph"),
    ),
    AgentType.WRITING: AgentPhase(
        number=7,
        title="Voice & Draft Studio",
        goal="Learn tone from preferences, store drafts, and export polished communications.",
        status=PhaseStatus.COMPLETE,
        deliverables=(
            "DraftService with version history",
            "Brain-powered rewrite_draft",
            "Operators: monitor_draft_queue",
            "HUD: DraftStudioPanel",
            "Cross-agent: EA follow-ups, Presentation tone",
            "Federation export for drafts",
            "Jarvis spoken writing brief",
            "Tools: style, save, rewrite, export",
        ),
        tools=(
            "get_writing_style",
            "save_draft",
            "refine_tone",
            "rewrite_draft",
            "list_drafts",
            "export_draft",
            "sync_free_sources",
            "list_free_source_status",
        ),
        hud="Draft queue · tone selector · versions",
        depends_on=("Preferences", "Unified retrieval"),
    ),
    AgentType.PRESENTATION: AgentPhase(
        number=8,
        title="Deck Builder",
        goal="Generate executive slide outlines from research, documents, and writing outputs.",
        status=PhaseStatus.COMPLETE,
        deliverables=(
            "DeckService: structured slides + build_from_sources",
            "Markdown export with speaker notes",
            "Operators: deck_rehearsal_spoken",
            "HUD: DeckBuilderPanel",
            "Cross-agent: Research, Librarian, Writing",
            "Federation export for decks",
            "Licensed slide API scaffold",
            "Tools: outline, build, export, workspace status",
        ),
        tools=(
            "create_deck_outline",
            "pull_research_slides",
            "build_deck_from_sources",
            "export_deck_markdown",
            "deck_workspace_status",
            "sync_free_sources",
            "list_free_source_status",
        ),
        hud="Deck workspace · slide preview · export",
        depends_on=("Research library", "Unified retrieval"),
    ),
    AgentType.OPERATIONS: AgentPhase(
        number=9,
        title="Operations Runbook",
        goal="Orchestrate vendors, maintenance schedules, and recurring ops via Project OS.",
        status=PhaseStatus.COMPLETE,
        deliverables=(
            "OpsRunbookService: SLA events, vendor interactions",
            "Maintenance due operator sync",
            "HUD: OperationsRunbookPanel",
            "Cross-agent: EA commitments escalation",
            "Federation export for vendors",
            "Jarvis spoken ops brief",
            "Licensed home/service desk scaffolds",
            "Tools: vendors, SLA, escalate, runbook brief",
        ),
        tools=(
            "list_vendors",
            "create_ops_task",
            "maintenance_schedule",
            "log_vendor_interaction",
            "sla_status",
            "escalate_ops_issue",
            "ops_runbook_brief",
            "sync_free_sources",
            "list_free_source_status",
        ),
        hud="Runbook checklist · vendor roster · SLA",
        depends_on=("Project OS", "Knowledge graph"),
    ),
}


def phase_for(agent_type: AgentType) -> AgentPhase:
    return AGENT_PHASES[agent_type]


def phase_to_dict(agent_type: AgentType) -> dict:
    """Serialize phase metadata for API responses."""
    p = phase_for(agent_type)
    return {
        "number": p.number,
        "title": p.title,
        "goal": p.goal,
        "status": p.status.value,
        "foundation_complete": True,
        "deliverables": list(p.deliverables),
        "tools": list(p.tools),
        "hud": p.hud,
        "depends_on": list(p.depends_on),
    }
