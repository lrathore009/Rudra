# Rudra

**Personal Intelligence Operating System / Founder OS**

Rudra is not a chatbot. It is a lifelong personal intelligence companion designed for a single user — understanding deeply, learning continuously, and protecting privacy above all else.

Inspired by JARVIS, Rudra operates as an executive command center with auth,
knowledge graph, project OS, document brain, and daily briefing — presented in a
**Rudraksha-themed sovereign tablet** UI (centered slate, realm navigation,
streaming decree dialogue).

> **Handing off to a developer?** Start with [`LAXMAN_HANDOFF.md`](LAXMAN_HANDOFF.md).

**Production (Vercel):** https://rudra-kl5i.vercel.app — see [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) for tunnel + env setup.

## Founder OS capabilities

| Module | Description |
|--------|-------------|
| **Auth** | JWT login, rate limits, audit log — [docs/SECURITY.md](docs/SECURITY.md) |
| **Knowledge Graph** | Entities, relationships, memory links — [docs/KNOWLEDGE_GRAPH.md](docs/KNOWLEDGE_GRAPH.md) |
| **Project OS** | Portfolio dashboard, tasks, agent context — [docs/PROJECT_OS.md](docs/PROJECT_OS.md) |
| **Document Brain** | Upload, chunk, search, Q&A — [docs/DOCUMENT_BRAIN.md](docs/DOCUMENT_BRAIN.md) |
| **Integrations** | Mock calendar/email + daily briefing — [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) |

Open **http://localhost:3000/login** first (default owner credentials in `.env.example`).

## Quick Start

> **Runs at $0.** Rudra defaults to a fully free, local-first stack. See
> [docs/ZERO_COST.md](docs/ZERO_COST.md) for the complete free-stack guide.

### Prerequisites

- Docker & Docker Compose (free local Postgres + pgvector)
- Python 3.11+
- Node.js 20+
- **One free LLM option** (pick either):
  - **Ollama** (local, private): `brew install ollama && ollama pull llama3.2 && ollama pull nomic-embed-text`
  - **Gemini free tier**: get a free key at https://aistudio.google.com/apikey → set `GOOGLE_AI_API_KEY` in `.env`
- Research uses **DuckDuckGo + Wikipedia** (no keys). OpenAI/Anthropic/Tavily are optional.

### Setup

```bash
# Clone and configure
cp .env.example .env
# Edit .env with your API keys

# Run setup script
chmod +x scripts/dev-setup.sh
./scripts/dev-setup.sh

# Start backend (Terminal 1)
cd backend
source .venv/bin/activate
uvicorn rudra.main:app --reload --port 8000

# Start frontend (Terminal 2)
cd frontend
npm run dev
```

Open **http://localhost:3000** — the Command Center.

API documentation: **http://localhost:8000/docs**

### Docker (All Services)

```bash
docker compose up
```

## Architecture

Eleven layers forming a modular intelligence platform:

| Layer | Purpose |
|-------|---------|
| Brain | Multi-model AI orchestration |
| Memory | 6-type long-term memory system |
| Agents | 9 specialized intelligence modules |
| Research | Multi-source research with credibility scoring |
| Knowledge | Luxury intelligence + knowledge graph |
| Workflow | Human-in-the-loop task orchestration |
| Voice | Wake word and conversation (Phase 2) |
| Security | E2E encryption, audit logs, zero-trust |
| Web | Next.js command center |
| Desktop | Tauri app (Phase 3) |
| Mobile | React Native (Phase 3) |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full system design.

## Agents

| Agent | Domain |
|-------|--------|
| Executive Assistant | Priorities, calendar, briefings |
| Research Analyst | Deep research with citations |
| Concierge Specialist | Luxury lifestyle coordination |
| Luxury Intelligence Analyst | UHNI market intelligence |
| Travel Specialist | Complex itinerary planning |
| Knowledge Librarian | Personal knowledge management |
| Writing Assistant | Professional communication |
| Presentation Builder | Executive presentations |
| Operations Manager | Household and vendor ops |

## API

```bash
# Execute a command
curl -X POST http://localhost:8000/api/v1/command \
  -H "Content-Type: application/json" \
  -d '{"command": "Prepare my daily briefing"}'

# Research
curl -X POST http://localhost:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Latest developments in quantum computing"}'

# Luxury intelligence
curl -X POST http://localhost:8000/api/v1/luxury/research \
  -H "Content-Type: application/json" \
  -d '{"subject": "Aman Tokyo", "category": "luxury_hotels"}'
```

## Privacy Principles

1. **You own all data** — stored locally, encrypted at rest
2. **Zero-trust** — every access is audited
3. **Local-first** — cloud is optional, never required
4. **User-controlled deletion** — hard delete with audit trail
5. **No telemetry** — no usage tracking, no analytics

## Development Roadmap

| Phase | Timeline | Focus |
|-------|----------|-------|
| 1 — MVP | Months 1–3 | Command center, agents, memory, research |
| 2 — Beta | Months 4–6 | Voice, auth, semantic search, K8s |
| 3 — Production | Months 7–12 | Desktop, mobile, integrations, briefings |
| 4 — Automation | Months 13–18 | Autonomous workflows, proactive intelligence |
| 5 — Ecosystem | Months 19–36 | Plugins, SDK, federation, fine-tuning |

See [docs/ROADMAP.md](docs/ROADMAP.md) for detailed phase specifications.

## Project Structure

```
Rudra/
├── backend/                 # Python FastAPI
│   ├── rudra/
│   │   ├── brain/           # Multi-model orchestrator
│   │   ├── memory/          # Memory layer
│   │   ├── agents/          # Agent system
│   │   ├── research/        # Research engine
│   │   ├── knowledge/       # Luxury intelligence
│   │   ├── workflows/       # Workflow engine
│   │   ├── voice/           # Voice layer
│   │   ├── security/        # Encryption + audit
│   │   └── api/             # REST + WebSocket
│   └── alembic/             # Database migrations
├── frontend/                # Next.js command center
├── infrastructure/          # Docker, K8s
├── docs/                    # Architecture + roadmap
└── scripts/                 # Dev tooling
```

## License

Private — single-user personal intelligence system.
