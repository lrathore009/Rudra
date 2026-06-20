# Agent Phases — Nine Specialist Upgrade Tracks

After the **Founder OS** upgrade (auth, knowledge graph, project OS, document brain,
integrations), Rudra evolves one specialist agent at a time. Each of the nine agents
has a dedicated phase with tools, context wiring, and HUD affordances.

**Foundation (shipped):** All nine agents route, execute with domain prompts, enrich
context from memories/research/skills, and appear in the command center HUD.

**Phases 1–9 (planned):** Domain-specific depth — one phase per agent, in priority order.

| Phase | Agent | HUD tag | Title | Status |
|-------|-------|---------|-------|--------|
| 1 | Executive Assistant | EA | Executive Command Center | ✅ Complete |
| 2 | Research Analyst | RA | Research Library | ✅ Complete |
| 3 | Concierge Specialist | CG | Experience Concierge | ✅ Complete |
| 4 | Luxury Intelligence Analyst | LX | Luxury Market Desk | ✅ Complete |
| 5 | Travel Specialist | TR | Itinerary Engine | ✅ Complete |
| 6 | Knowledge Librarian | KL | Unified Retrieval | ✅ Complete |
| 7 | Writing Assistant | WR | Voice & Draft Studio | ✅ Complete |
| 8 | Presentation Builder | PR | Deck Builder | ✅ Complete |
| 9 | Personal Operations Manager | OP | Operations Runbook | ✅ Complete |

Phase metadata lives in `backend/rudra/agents/phases.py` and is exposed on
`GET /api/v1/agents` under each agent's `phase` field.

---

## Phase 1 — Executive Assistant · Executive Command Center

**Goal:** Turn the EA into a daily command hub wired to briefing, calendar, and project priorities.

**Deliverables**

- Inject daily briefing + active projects into EA context (`AgentContextBuilder`)
- ReAct tools: `get_daily_briefing`, `list_active_projects`, `summarize_day`
- HUD: priority stack + today's commitments strip

**Depends on:** Integrations (Founder Phase 5), Project OS (Founder Phase 3)

---

## Phase 2 — Research Analyst · Research Library

**Goal:** Persist, retrieve, and cite past research reports as a personal intelligence archive.

**Deliverables**

- Save research reports to Postgres with citations and confidence scores
- Tools: `save_research_report`, `search_research_library`
- HUD: research history + confidence trend panel

**Depends on:** Research engine (shipped)

---

## Phase 3 — Concierge Specialist · Experience Concierge

**Goal:** Track reservations, preferences, and luxury experiences via the knowledge graph.

**Deliverables**

- Link concierge memories to experience entities in the graph
- Tools: `search_preferences`, `log_experience_request`
- HUD: open requests + preference quick-picks

**Depends on:** Knowledge graph (Founder Phase 2), Luxury intel module

---

## Phase 4 — Luxury Intelligence Analyst · Luxury Market Desk

**Goal:** Deliver entity-linked market briefings, watchlists, and category alerts for UHNI intel.

**Deliverables**

- Graph-linked luxury entities with category watchlists
- Tools: `luxury_market_brief`, `update_watchlist`
- HUD: market ticker + watchlist alerts

**Depends on:** Knowledge graph (Founder Phase 2), Luxury intel module

---

## Phase 5 — Travel Specialist · Itinerary Engine

**Goal:** Plan multi-leg trips as project templates with graph-linked destinations and visa checklists.

**Deliverables**

- Trip project templates + itinerary memory type
- Tools: `create_itinerary`, `search_travel_memories`
- HUD: active trips + leg status board

**Depends on:** Project OS (Founder Phase 3), Knowledge graph (Founder Phase 2)

---

## Phase 6 — Knowledge Librarian · Unified Retrieval

**Goal:** Fuse memories, documents, and graph traversal into one librarian retrieval stack.

**Deliverables**

- Document + graph context in `AgentContextBuilder`
- Tools: `search_documents`, `graph_neighbors`, `connect_entities`
- HUD: retrieval trace + entity cluster view

**Depends on:** Document brain (Founder Phase 4), Knowledge graph (Founder Phase 2)

---

## Phase 7 — Writing Assistant · Voice & Draft Studio

**Goal:** Learn tone from preferences, store drafts, and export polished communications.

**Deliverables**

- Writing-style profile from preferences + past drafts
- Tools: `get_writing_style`, `save_draft`, `refine_tone`
- HUD: draft queue + tone selector

**Depends on:** Memories, Preferences tables

---

## Phase 8 — Presentation Builder · Deck Builder

**Goal:** Generate executive slide outlines from research, documents, and writing outputs.

**Deliverables**

- Structured deck outlines with speaker notes
- Tools: `create_deck_outline`, `pull_research_slides`
- HUD: deck workspace + slide preview

**Depends on:** Research library (Phase 2), Document brain (Founder Phase 4)

---

## Phase 9 — Personal Operations Manager · Operations Runbook

**Goal:** Orchestrate vendors, maintenance schedules, and recurring ops via Project OS.

**Deliverables**

- Vendor entities + ops task templates in projects
- Tools: `list_vendors`, `create_ops_task`, `maintenance_schedule`
- HUD: runbook checklist + vendor roster

**Depends on:** Project OS (Founder Phase 3), Knowledge graph (Founder Phase 2)

---

## Implementation notes

- Update `PhaseStatus` in `phases.py` as work lands (`planned` → `in_progress` → `complete`).
- Add agent-specific tools in `agents/tools.py` and register them in `react.py` per phase.
- Extend `AgentContextBuilder.enrich()` with domain blocks before flipping status to complete.
- HUD panels can live under `frontend/src/components/hud/` following existing Founder OS panels.
- Each phase should ship with pytest coverage and pass `npm run build`.

## API shape

```json
{
  "type": "executive_assistant",
  "name": "Executive Assistant",
  "description": "...",
  "phase": {
    "number": 1,
    "title": "Executive Command Center",
    "goal": "...",
    "status": "planned",
    "foundation_complete": true,
    "deliverables": ["..."],
    "tools": ["get_daily_briefing", "list_active_projects", "summarize_day"],
    "hud": "Priority stack · today's commitments",
    "depends_on": ["Integrations (Phase 5)", "Project OS (Phase 3)"]
  }
}
```
