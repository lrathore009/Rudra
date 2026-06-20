"""P1 — Tool layer: a model-agnostic tool registry the ReAct loop can call.

Tools are plain async callables described by a name + natural-language description +
a lightweight parameter spec. They are invoked from ``agents/react.py`` via a
prompt-based ReAct protocol, so they work with ANY model (including small local Ollama
models) without provider-level function-calling support.

All built-in tools are $0 and local-first. ``search_memory`` needs a DB session; the
optional ``run_python`` (P4) is added only when ``ENABLE_CODE_EXECUTION`` is set.
"""

from __future__ import annotations

import ast
import operator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from rudra.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ToolContext:
    """Per-request resources a tool may need (db session, user, brain)."""

    user_id: str = "owner"
    db: Any = None  # sqlalchemy AsyncSession | None
    brain: Any = None  # rudra.brain.orchestrator.Brain | None
    extra: dict[str, Any] = field(default_factory=dict)


ToolHandler = Callable[[dict[str, Any], ToolContext], Awaitable[str]]


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, str]  # arg name -> human description (lightweight schema)
    handler: ToolHandler
    safe: bool = True  # safe tools run without confirmation
    requires_db: bool = False


class ToolRegistry:
    """Holds the tools available to an agent and runs them by name."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools)

    def list(self) -> list[dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
                "safe": t.safe,
            }
            for t in self._tools.values()
        ]

    def describe_for_prompt(self) -> str:
        lines = []
        for t in self._tools.values():
            params = ", ".join(f"{k} ({v})" for k, v in t.parameters.items()) or "none"
            lines.append(f"- {t.name}: {t.description} | args: {params}")
        return "\n".join(lines)

    async def execute(self, name: str, args: dict[str, Any], ctx: ToolContext) -> str:
        tool = self.get(name)
        if tool is None:
            return f"Error: unknown tool '{name}'. Available: {', '.join(self.names())}"
        if tool.requires_db and ctx.db is None:
            return f"Error: tool '{name}' needs database access, which is unavailable here."
        try:
            return await tool.handler(args, ctx)
        except Exception as e:  # noqa: BLE001
            logger.warning("tool_failed", tool=name, error=str(e)[:160])
            return f"Error running tool '{name}': {e}"


# ---------------------------------------------------------------------------
# Built-in tools (all $0, local-first, safe)
# ---------------------------------------------------------------------------

async def _current_time(args: dict[str, Any], ctx: ToolContext) -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


# Safe arithmetic evaluator (no eval()).
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("unsupported expression")


async def _calculator(args: dict[str, Any], ctx: ToolContext) -> str:
    expr = str(args.get("expression", "")).strip()
    if not expr:
        return 'Error: provide an "expression", e.g. {"expression": "2*(3+4)"}'
    try:
        tree = ast.parse(expr, mode="eval")
        value = _eval_node(tree.body)
    except Exception:
        return f"Error: could not evaluate '{expr}'"
    # Render whole floats as ints for cleanliness (14.0 -> 14).
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value)


async def _web_search(args: dict[str, Any], ctx: ToolContext) -> str:
    from rudra.research.engine import WebSearchProvider, WikipediaProvider

    query = str(args.get("query", "")).strip()
    if not query:
        return "Error: provide a 'query'."
    results = await WebSearchProvider().search(query, max_results=5)
    if not results:
        results = await WikipediaProvider().search(query, max_results=5)
    if not results:
        return f"No results found for '{query}'."
    return "\n".join(
        f"[{i}] {s.title}\n    {s.snippet[:240]}\n    {s.url}"
        for i, s in enumerate(results[:5], 1)
    )


async def _search_documents(args: dict[str, Any], ctx: ToolContext) -> str:
    from rudra.documents.service import DocumentService

    query = str(args.get("query", "")).strip()
    if not query:
        return "Error: provide a 'query'."
    svc = DocumentService(ctx.db, ctx.user_id)
    hits = await svc.search(query, limit=5)
    if not hits:
        return "No relevant document passages found."
    return "\n".join(
        f"[{i}] ({doc.filename}, score={score:.2f}) {chunk.content[:220]}"
        for i, (chunk, doc, score) in enumerate(hits, 1)
    )


async def _summarize_document(args: dict[str, Any], ctx: ToolContext) -> str:
    from uuid import UUID

    from rudra.documents.service import DocumentService

    raw_id = str(args.get("document_id", "")).strip()
    if not raw_id:
        return "Error: provide 'document_id'."
    svc = DocumentService(ctx.db, ctx.user_id)
    try:
        return await svc.summarize(UUID(raw_id))
    except ValueError:
        return f"Error: document '{raw_id}' not found."


async def _search_memory(args: dict[str, Any], ctx: ToolContext) -> str:
    from rudra.memory.service import MemoryService

    query = str(args.get("query", "")).strip()
    if not query:
        return "Error: provide a 'query'."
    svc = MemoryService(ctx.db, ctx.user_id)
    hits = await svc.search_by_text(query, limit=5)
    if not hits:
        return "No relevant memories found."
    return "\n".join(
        f"[{i}] ({mem.memory_type}, sim={score:.2f}) {mem.title}: {mem.content[:200]}"
        for i, (mem, score) in enumerate(hits, 1)
    )


async def _use_skill(args: dict[str, Any], ctx: ToolContext) -> str:
    """P2 bridge: discover skills (no name) or activate one (load its SKILL.md body)."""
    from rudra.skills.loader import get_skill_registry

    reg = get_skill_registry()
    name = str(args.get("name", "")).strip()
    if not name:
        listing = reg.list()
        if not listing:
            return "No skills installed."
        return "Available skills (call use_skill with a 'name' to load one):\n" + "\n".join(
            f"- {s['name']}: {s['description']}" for s in listing
        )
    skill = reg.get(name)
    if skill is None:
        avail = ", ".join(s["name"] for s in reg.list()) or "(none)"
        return f"Unknown skill '{name}'. Available: {avail}"
    return skill.load_body()


def build_default_registry(*, include_code: bool | None = None) -> ToolRegistry:
    """Construct the standard tool set. ``include_code`` overrides the config flag."""
    reg = ToolRegistry()
    reg.register(Tool("current_time", "Get the current local date and time.", {}, _current_time))
    reg.register(
        Tool(
            "calculator",
            "Evaluate an arithmetic expression precisely.",
            {"expression": "math expression, e.g. 2*(3+4)"},
            _calculator,
        )
    )
    reg.register(
        Tool(
            "web_search",
            "Search the web (DuckDuckGo, falling back to Wikipedia) for up-to-date facts.",
            {"query": "what to search for"},
            _web_search,
        )
    )
    reg.register(
        Tool(
            "search_documents",
            "Search uploaded documents semantically for relevant passages.",
            {"query": "what to find in documents"},
            _search_documents,
            requires_db=True,
        )
    )
    reg.register(
        Tool(
            "summarize_document",
            "Summarize an uploaded document by id.",
            {"document_id": "UUID of the document"},
            _summarize_document,
            requires_db=True,
        )
    )
    reg.register(
        Tool(
            "search_memory",
            "Search the owner's private memory for relevant past notes and context.",
            {"query": "what to recall"},
            _search_memory,
            requires_db=True,
        )
    )
    reg.register(
        Tool(
            "use_skill",
            "List installed skills (no args) or load a skill's instructions by name.",
            {"name": "skill name (omit to list all)"},
            _use_skill,
        )
    )

    from rudra.core.config import get_settings

    enabled = get_settings().enable_code_execution if include_code is None else include_code
    if enabled:
        from rudra.autonomy.code_exec import code_exec_tool

        reg.register(code_exec_tool())
    return reg


def build_registry_for_agent(agent_type) -> ToolRegistry:
    """Default tools plus phase-specific tools for a specialist agent."""
    from rudra.agents import phase_tools as pt
    from rudra.agents.phases import AGENT_PHASES
    from rudra.agents.types import AgentType

    reg = build_default_registry()
    at = agent_type if isinstance(agent_type, AgentType) else AgentType(agent_type)
    phase = AGENT_PHASES[at]

    _PHASE_TOOL_DEFS: dict[str, tuple[str, str, dict[str, str], Any, bool]] = {
        "get_daily_briefing": (
            "get_daily_briefing",
            "Generate or fetch today's executive daily briefing.",
            {},
            pt.get_daily_briefing,
            True,
        ),
        "list_active_projects": (
            "list_active_projects",
            "List active founder projects with progress and next actions.",
            {},
            pt.list_active_projects,
            True,
        ),
        "summarize_day": (
            "summarize_day",
            "Combine daily briefing and project stack into one executive summary.",
            {},
            pt.summarize_day,
            True,
        ),
        "get_command_stack": (
            "get_command_stack",
            "Fetch full executive command stack across all five data tiers.",
            {},
            pt.get_command_stack,
            True,
        ),
        "sync_executive_sources": (
            "sync_executive_sources",
            "Sync calendar, email, tasks, contacts, travel, finance, and health feeds.",
            {},
            pt.sync_executive_sources,
            True,
        ),
        "list_commitments": (
            "list_commitments",
            "List open follow-ups and commitments extracted from inbox and tasks.",
            {},
            pt.list_commitments,
            True,
        ),
        "list_connector_status": (
            "list_connector_status",
            "Show connected data sources for the executive command center.",
            {},
            pt.list_connector_status,
            True,
        ),
        "save_research_report": (
            "save_research_report",
            "Persist a research report to the personal library.",
            {
                "title": "report title",
                "content": "full report body",
                "query": "original research query (optional)",
                "confidence": "0-1 confidence score (optional)",
            },
            pt.save_research_report,
            True,
        ),
        "search_research_library": (
            "search_research_library",
            "Search saved research reports (hybrid keyword + vector when query provided).",
            {"query": "search terms (omit for recent)", "hybrid": "use hybrid RRF search (default true)"},
            pt.search_research_library,
            True,
        ),
        "hybrid_search_library": (
            "hybrid_search_library",
            "Hybrid RRF search across the research library (keyword + embeddings).",
            {"query": "search terms", "limit": "max results (optional)"},
            pt.hybrid_search_library,
            True,
        ),
        "add_research_watchlist": (
            "add_research_watchlist",
            "Add a topic to the proactive research watchlist.",
            {"topic": "short label", "query_template": "research query", "ttl_days": "refresh interval"},
            pt.add_research_watchlist,
            True,
        ),
        "research_library_trends": (
            "research_library_trends",
            "Show research library stats, confidence trends, and watchlist topics.",
            {},
            pt.research_library_trends,
            True,
        ),
        "search_preferences": (
            "search_preferences",
            "Search owner preferences for dining, hotels, travel, writing, luxury.",
            {"query": "optional filter", "category": "optional category"},
            pt.search_preferences,
            True,
        ),
        "log_experience_request": (
            "log_experience_request",
            "Log a concierge experience or reservation request.",
            {"title": "short title", "details": "full request details", "venue": "optional", "party_size": "optional"},
            pt.log_experience_request,
            True,
        ),
        "update_request_status": (
            "update_request_status",
            "Update concierge request status (requested/pending/confirmed/completed).",
            {"request_id": "UUID", "status": "new status"},
            pt.update_request_status,
            True,
        ),
        "recommend_experiences": (
            "recommend_experiences",
            "Recommend experiences from owner preferences.",
            {"category": "dining|hotels"},
            pt.recommend_experiences,
            True,
        ),
        "link_venue_entity": (
            "link_venue_entity",
            "Link a concierge request to a knowledge graph venue entity.",
            {"request_id": "UUID", "venue_name": "venue name"},
            pt.link_venue_entity,
            True,
        ),
        "luxury_market_brief": (
            "luxury_market_brief",
            "Generate a luxury market intelligence briefing.",
            {"subject": "topic", "category": "luxury category slug"},
            pt.luxury_market_brief,
            True,
        ),
        "update_watchlist": (
            "update_watchlist",
            "Add an item to the luxury market watchlist.",
            {"title": "item name", "notes": "notes", "category": "category"},
            pt.update_watchlist,
            True,
        ),
        "set_price_alert": (
            "set_price_alert",
            "Set a price or market alert on a luxury watchlist item.",
            {"title": "watchlist title", "threshold": "optional numeric threshold"},
            pt.set_price_alert,
            True,
        ),
        "luxury_desk_trends": (
            "luxury_desk_trends",
            "Luxury desk stats: snapshots, exclusivity, watchlist count.",
            {},
            pt.luxury_desk_trends,
            True,
        ),
        "create_itinerary": (
            "create_itinerary",
            "Create a multi-leg travel itinerary.",
            {"title": "trip name", "plan": "day-by-day plan text"},
            pt.create_itinerary,
            True,
        ),
        "search_travel_memories": (
            "search_travel_memories",
            "Search travel memories and saved itineraries.",
            {"query": "optional search query"},
            pt.search_travel_memories,
            True,
        ),
        "create_trip_project": (
            "create_trip_project",
            "Create a structured trip with project template and legs.",
            {"title": "trip name", "destinations": "comma-separated cities"},
            pt.create_trip_project,
            True,
        ),
        "visa_requirements": (
            "visa_requirements",
            "Visa checklist for a destination and passport nationality.",
            {"destination": "country/city", "passport": "optional nationality"},
            pt.visa_requirements,
            True,
        ),
        "upcoming_travel_brief": (
            "upcoming_travel_brief",
            "Upcoming trips, legs, and travel memory summary.",
            {},
            pt.upcoming_travel_brief,
            True,
        ),
        "graph_neighbors": (
            "graph_neighbors",
            "List knowledge graph neighbors of an entity.",
            {"entity_name": "entity name", "entity_id": "UUID (optional)"},
            pt.graph_neighbors,
            True,
        ),
        "connect_entities": (
            "connect_entities",
            "Create a relationship between two knowledge graph entities.",
            {"source": "source name", "target": "target name", "relation": "relation type"},
            pt.connect_entities,
            True,
        ),
        "unified_search": (
            "unified_search",
            "Four-source RRF search: memories, documents, research, graph.",
            {"query": "search terms"},
            pt.unified_search,
            True,
        ),
        "librarian_answer": (
            "librarian_answer",
            "Unified librarian answer with cited sources and trace.",
            {"query": "question"},
            pt.librarian_answer,
            True,
        ),
        "retrieval_trace": (
            "retrieval_trace",
            "Recent unified retrieval traces and latency.",
            {},
            pt.retrieval_trace,
            True,
        ),
        "get_writing_style": (
            "get_writing_style",
            "Load the owner's writing voice profile.",
            {},
            pt.get_writing_style,
            True,
        ),
        "save_draft": (
            "save_draft",
            "Save a writing draft.",
            {"title": "draft title", "content": "body", "format": "email|memo|letter"},
            pt.save_draft,
            True,
        ),
        "refine_tone": (
            "refine_tone",
            "Prepare tone refinement guidance for a draft using the voice profile.",
            {"text": "draft text", "tone": "optional target tone"},
            pt.refine_tone,
            True,
        ),
        "rewrite_draft": (
            "rewrite_draft",
            "Rewrite a draft using the owner voice profile.",
            {"draft_id": "UUID", "text": "text to rewrite", "tone": "optional"},
            pt.rewrite_draft,
            True,
        ),
        "list_drafts": (
            "list_drafts",
            "List writing drafts in the queue.",
            {},
            pt.list_drafts,
            True,
        ),
        "export_draft": (
            "export_draft",
            "Export a draft as markdown.",
            {"draft_id": "UUID"},
            pt.export_draft,
            True,
        ),
        "create_deck_outline": (
            "create_deck_outline",
            "Save an executive presentation deck outline.",
            {"title": "deck title", "outline": "slide bullets", "slides": "slide count"},
            pt.create_deck_outline,
            True,
        ),
        "pull_research_slides": (
            "pull_research_slides",
            "Pull research report content for slide building.",
            {"query": "optional filter"},
            pt.pull_research_slides,
            True,
        ),
        "build_deck_from_sources": (
            "build_deck_from_sources",
            "Build a deck from unified librarian + research sources.",
            {"title": "deck title", "query": "topic query", "slides": "count"},
            pt.build_deck_from_sources,
            True,
        ),
        "export_deck_markdown": (
            "export_deck_markdown",
            "Export deck as markdown with speaker notes.",
            {"deck_id": "UUID"},
            pt.export_deck_markdown,
            True,
        ),
        "deck_workspace_status": (
            "deck_workspace_status",
            "List decks in the presentation workspace.",
            {},
            pt.deck_workspace_status,
            True,
        ),
        "list_vendors": (
            "list_vendors",
            "List household and operations vendors.",
            {},
            pt.list_vendors,
            True,
        ),
        "create_ops_task": (
            "create_ops_task",
            "Create an operations task in the project runbook.",
            {"title": "task title", "details": "optional details", "project": "project name"},
            pt.create_ops_task,
            True,
        ),
        "maintenance_schedule": (
            "maintenance_schedule",
            "Show scheduled maintenance items and due dates.",
            {},
            pt.maintenance_schedule,
            True,
        ),
        "log_vendor_interaction": (
            "log_vendor_interaction",
            "Log an interaction with a household vendor.",
            {"vendor": "vendor name", "notes": "interaction notes"},
            pt.log_vendor_interaction,
            True,
        ),
        "sla_status": (
            "sla_status",
            "Operations SLA status: maintenance due and open events.",
            {},
            pt.sla_status,
            True,
        ),
        "escalate_ops_issue": (
            "escalate_ops_issue",
            "Escalate a vendor issue to ops project and SLA tracker.",
            {"vendor": "vendor name", "issue": "issue description"},
            pt.escalate_ops_issue,
            True,
        ),
        "ops_runbook_brief": (
            "ops_runbook_brief",
            "Full operations runbook brief as JSON summary.",
            {},
            pt.ops_runbook_brief,
            True,
        ),
        "sync_free_sources": (
            "sync_free_sources",
            "Sync free intelligence feeds for this specialist (or executive stack for EA).",
            {"agent": "agent slug (optional)", "query": "optional focus query"},
            pt.sync_free_sources,
            True,
        ),
        "list_free_source_status": (
            "list_free_source_status",
            "List connected free data sources for one or all specialist agents.",
            {"agent": "optional agent slug; omit for all agents"},
            pt.list_free_source_status,
            True,
        ),
    }

    for tool_name in phase.tools:
        if tool_name in ("search_documents", "summarize_document"):
            continue  # already in default registry
        spec = _PHASE_TOOL_DEFS.get(tool_name)
        if spec is None:
            continue
        name, desc, params, handler, safe = spec
        reg.register(
            Tool(
                name,
                desc,
                params,
                handler,
                safe=safe,
                requires_db=name not in ("luxury_market_brief", "refine_tone"),
            )
        )
    return reg
