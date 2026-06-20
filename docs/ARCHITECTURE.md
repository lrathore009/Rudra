# Rudra Architecture

> Personal Intelligence Operating System — designed for decades of continuous learning.

## System Overview

Rudra is a modular, privacy-first intelligence platform built around eleven architectural layers. It is designed for a single user, accumulating knowledge and capability over a lifetime.

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYERS                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   Web    │  │ Desktop  │  │  Mobile  │  │  Voice   │       │
│  │ Next.js  │  │  Tauri   │  │React Nat.│  │  Wake    │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       └──────────────┴──────────────┴──────────────┘              │
│                          │ WebSocket / REST                      │
├──────────────────────────┼──────────────────────────────────────┤
│                    SECURITY LAYER                               │
│  E2E Encryption │ Zero-Trust │ Audit Logs │ Secret Vault        │
├──────────────────────────┼──────────────────────────────────────┤
│                    WORKFLOW LAYER                               │
│  Human-in-the-Loop │ Task Orchestration │ Approval Gates        │
├──────────────────────────┼──────────────────────────────────────┤
│                     AGENT LAYER                                 │
│  EA │ Research │ Concierge │ Luxury │ Travel │ Librarian │ ...  │
├──────────────────────────┼──────────────────────────────────────┤
│                     BRAIN LAYER                                 │
│  Multi-Model Router │ OpenAI │ Anthropic │ Gemini │ Ollama     │
├──────────┬───────────────┼───────────────┬─────────────────────┤
│ RESEARCH │   KNOWLEDGE   │    MEMORY     │                     │
│  Engine  │ Luxury Intel  │  6 Memory     │                     │
│          │  Graph        │  Types        │                     │
├──────────┴───────────────┴───────────────┴─────────────────────┤
│                     DATA LAYER                                  │
│  PostgreSQL + pgvector │ Qdrant │ Redis │ Knowledge Graph       │
└─────────────────────────────────────────────────────────────────┘
```

## Layer Specifications

### 1. Brain Layer (`backend/rudra/brain/`)

Central intelligence orchestrator with multi-model failover.

| Component | Responsibility |
|-----------|---------------|
| `orchestrator.py` | Model routing, failover, streaming |
| Model tiers | `default`, `reasoning`, `fast` |
| Providers | OpenAI, Anthropic, Google Gemini, Ollama (local) |

**Routing logic:** Privacy-sensitive operations prefer local models. Reasoning tasks use highest-capability models. Fast classification uses lightweight models.

### 2. Memory Layer (`backend/rudra/memory/`)

Six memory types forming Rudra's long-term intelligence:

| Type | Purpose | Example |
|------|---------|---------|
| Episodic | Interaction history | "User asked about Tokyo trip" |
| Semantic | Facts and knowledge | "User prefers aisle seats" |
| Project | Active work context | "Q3 board presentation" |
| Preference | Learned preferences | "Favorite hotel: Aman Tokyo" |
| Relationship | People and connections | "CFO Sarah — quarterly check-ins" |
| Research | Investigation results | "Luxury watch market analysis" |

Storage: PostgreSQL with pgvector embeddings + Qdrant for large-scale vector search + knowledge graph via `memory_links`.

### 3. Agent Layer (`backend/rudra/agents/`)

Nine specialized agents, each with domain-specific system prompts and context injection:

1. **Executive Assistant** — priorities, calendar, briefings
2. **Research Analyst** — deep research with citations
3. **Concierge Specialist** — luxury lifestyle coordination
4. **Luxury Intelligence Analyst** — UHNI market intelligence
5. **Travel Specialist** — complex itinerary planning
6. **Knowledge Librarian** — personal knowledge management
7. **Writing Assistant** — professional communication
8. **Presentation Builder** — executive presentations
9. **Personal Operations Manager** — household and vendor ops

Auto-routing uses fast model classification. Direct invocation available via API.

### 4. Research Layer (`backend/rudra/research/`)

Multi-source intelligence gathering:

- Web search (Tavily/SERP)
- News aggregation
- Academic papers (Phase 2)
- User knowledge base
- Credibility scoring per source
- Confidence-weighted synthesis

### 5. Knowledge Layer (`backend/rudra/knowledge/`)

- **Luxury Intelligence Module** — dedicated UHNI research across 10 categories
- **Knowledge Graph** — entity relationships via memory links
- Continuous knowledge base growth through automated research memory storage

### 6. Workflow Layer (`backend/rudra/workflows/`)

Human-in-the-loop task orchestration with approval gates for sensitive actions (financial, communication, booking).

### 7. Voice Layer (`backend/rudra/voice/`)

Phase 2+: wake word ("Rudra"), continuous conversation, natural TTS/STT with context retention.

### 8. Security Layer (`backend/rudra/security/`)

- AES-256 encryption at rest (Fernet)
- JWT session management
- Immutable audit logs
- PBKDF2 key derivation
- Zero-trust: every memory access logged

### 9–11. Client Layers

| Layer | Technology | Phase |
|-------|-----------|-------|
| Web | Next.js + ShadCN | Phase 1 (MVP) |
| Desktop | Tauri (Rust + WebView) | Phase 3 |
| Mobile | React Native / Expo | Phase 3 |

## Data Flow

```
User Command → Command API → Agent Orchestrator
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              Memory Recall    Brain (LLM)    Research Engine
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
                              Agent Response
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              Episodic Memory   Audit Log      WebSocket Push
```

## API Design

Base URL: `/api/v1`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/command` | POST | Primary command interface |
| `/agents` | GET | List available agents |
| `/agents/invoke` | POST | Direct agent invocation |
| `/memories` | CRUD | Memory management |
| `/research` | POST | Multi-source research |
| `/luxury/research` | POST | Luxury intelligence |
| `/luxury/trends` | GET | UHNI trend briefing |
| `/health` | GET | System status |
| `/ws` | WebSocket | Real-time command stream |

## Database Schema

See `backend/alembic/versions/001_initial_schema.py` for full DDL.

Core tables: `memories`, `memory_tags`, `memory_links`, `projects`, `preferences`, `relationships`, `research_reports`, `audit_logs`.

## Deployment Topology

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Ingress   │────▶│  Frontend   │     │   Backend   │
│   (nginx)   │     │  (Next.js)  │────▶│  (FastAPI)  │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                    ┌───────────────┬───────────┼───────────┐
                    ▼               ▼           ▼           ▼
              PostgreSQL        Qdrant       Redis      Ollama
              + pgvector                                   (local)
```

Kubernetes-ready via `infrastructure/k8s/` (Phase 2+).

## Security Architecture

1. **Encryption at rest** — all sensitive memory content encrypted with user-derived keys
2. **Encryption in transit** — TLS 1.3 everywhere
3. **Zero-trust** — no implicit trust between services; audit every access
4. **Local-first** — core intelligence runs on user hardware; cloud optional
5. **User-controlled deletion** — hard delete with audit trail
6. **Secret vault** — API keys encrypted, never logged

## Scalability Design

- **Horizontal:** stateless backend pods behind load balancer
- **Vertical:** PostgreSQL read replicas for memory queries
- **Vector:** Qdrant clustering for embedding search at scale
- **Decades:** schema versioning via Alembic; backward-compatible API versions

## Founder OS modules (2026-06)

| Module | Path | API prefix |
|--------|------|------------|
| Auth | `rudra/auth/` | `/api/v1/auth/*` |
| Knowledge graph | `rudra/graph/` | `/api/v1/graph/*` |
| Project OS | `rudra/projects/` | `/api/v1/projects/*` |
| Document brain | `rudra/documents/` | `/api/v1/documents/*` |
| Integrations | `rudra/integrations/` | `/api/v1/integrations`, `/calendar`, `/email`, `/briefing` |

Database migrations `001`–`006`. Run `alembic upgrade head` after deploy.
