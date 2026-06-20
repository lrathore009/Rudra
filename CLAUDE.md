# CLAUDE.md — Project Context for Rudra

This file orients an AI coding assistant (Claude Code, Cursor, etc.) working on
Rudra. Read it first, then `HANDOFF.md` (setup) and `KNOWN_ISSUES.md` (what to
improve next).

## What this project is

Rudra is a **privacy-first, local-first, $0** personal intelligence OS for a
single owner. Backend = FastAPI (Python), Frontend = Next.js 15. All data and AI
run locally (Postgres+pgvector, Ollama). Cloud LLMs are optional fallbacks.

## Repository layout

```
Rudra/
├── backend/                    # FastAPI app (Python ≥ 3.11)
│   ├── rudra/
│   │   ├── main.py             # FastAPI entry, CORS, websocket
│   │   ├── core/
│   │   │   ├── config.py       # Settings (pydantic-settings); ALL config here
│   │   │   ├── database.py     # async SQLAlchemy engine/session, lifespan
│   │   │   ├── health.py       # deep service health checks
│   │   │   └── logging.py
│   │   ├── brain/
│   │   │   ├── orchestrator.py # multi-model brain + provider failover
│   │   │   └── embeddings.py   # free-first embedding service
│   │   ├── agents/base.py      # 9 agents + AgentOrchestrator (routing)
│   │   ├── memory/             # models + service (CRUD, semantic search)
│   │   ├── research/engine.py  # web (DuckDuckGo/Wikipedia) + synthesis
│   │   ├── auth/               # JWT login, owner bootstrap
│   │   ├── graph/              # knowledge graph
│   │   ├── projects/           # Founder OS
│   │   ├── documents/          # document brain
│   │   ├── integrations/       # calendar/email/briefing stubs
│   │   ├── security/           # encryption (Fernet), JWT, audit log
│   │   └── api/                # routes + deps (auth required)
│   ├── alembic/                # migrations 001–006
│   ├── tests/                  # pytest — 124 tests; conftest stubs LLM+embeddings
│   ├── requirements.txt        # loose deps
│   └── requirements.lock.txt   # exact pinned deps (reproducible)
├── frontend/                   # Next.js 15 + React 19 + Tailwind + shadcn
│   └── src/
│       ├── app/page.tsx        # state + streaming; renders SovereignView
│       ├── components/tablet/  # sovereign tablet UI (P1–P6)
│       ├── lib/api.ts          # centralized API client (API_BASE)
│       └── components/hud/     # Rudraksha core, realm panels, streaming thread
├── scripts/                    # start.sh, stop.sh, healthcheck.sh, package-handoff.sh
├── infrastructure/docker/      # init-db.sql (extensions, audit immutability)
├── docker-compose.yml          # postgres, qdrant, redis, backend, frontend
└── *.md                        # docs (see HANDOFF.md §9)
```

## Key commands

```bash
# Run everything
./scripts/start.sh            # infra + migrations + backend + frontend
./scripts/healthcheck.sh      # check all services
./scripts/stop.sh --all       # stop everything

# Backend dev
cd backend && source .venv/bin/activate
uvicorn rudra.main:app --reload
python -m pytest -q           # 124 tests; do not require Ollama/cloud
alembic upgrade head          # apply migrations
alembic revision --autogenerate -m "msg"   # new migration

# Frontend dev
cd frontend && npm run dev
npm run build                 # ALWAYS run before pushing — Vercel type-checks here
```

## Architecture notes / conventions

- **All configuration goes through `backend/rudra/core/config.py`** (env-driven,
  `pydantic-settings`). Never hardcode model names, URLs, or secrets. The Ollama
  chat model comes from `settings.ollama_chat_model` (`OLLAMA_CHAT_MODEL` env).
- **LLM fallback order:** Gemini → OpenAI → Anthropic → Ollama. Cloud providers
  are tried only if their keys exist; Ollama is the always-available local
  fallback. Empty env keys are normalized to `None`.
- **Vector store is pgvector** (inside Postgres), 768-dim, matching
  `nomic-embed-text`. Qdrant is provisioned but not yet used. Changing embedding
  model dimension requires a new Alembic migration (the column is `vector(768)`).
- **Memory semantic search** uses raw SQL with `CAST(:embedding AS vector)` —
  do NOT use `:embedding::vector` (SQLAlchemy won't bind a param before `::`).
- **Frontend API base:** `API_BASE = process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000"` in `src/lib/api.ts`. All calls route through it.
- **CORS** is env-driven (`CORS_ALLOW_ORIGINS` + `CORS_ALLOW_ORIGIN_REGEX` for
  `*.vercel.app`). Add custom domains there.
- **Agents** all prepend `OPERATING_PRINCIPLES` (in `agents/base.py`) to prevent
  small local models from inventing refusals. Routing is parsed robustly via
  `AgentOrchestrator._parse_agent_type`.

## Gotchas

- `next build` type-checks (Vercel runs it); `next dev` does not. Always run
  `npm run build` locally before pushing frontend changes.
- Background processes started with `nohup` from some sandboxes die on exit; the
  `scripts/*.sh` use `nohup` for real terminals — run them in a normal shell.
- The repo uses Python 3.14 on the source machine but supports ≥ 3.11.
- `.env` is gitignored (secrets). After handoff, rotate `RUDRA_SECRET_KEY` and
  `RUDRA_ENCRYPTION_KEY`.

## Good first improvements (see KNOWN_ISSUES.md and LAXMAN_HANDOFF.md)

1. ~~Real authentication~~ — JWT login + `/login` screen ✅
2. ~~Streaming responses in the UI~~ — SSE stream + ink text ✅
3. Wire Redis for caching / a Celery task queue (provisioned, unused).
4. Optional Qdrant adapter as an alternative vector backend.
5. Upgrade local model: `ollama pull qwen2.5:7b` + set `OLLAMA_CHAT_MODEL`.
6. Stable named Cloudflare tunnel for Vercel `NEXT_PUBLIC_API_URL`.
7. Sovereign tablet mobile polish (realm drawers, gestures).

## Definition of done for changes

- Backend: `python -m pytest -q` passes (124 tests; add tests for new behavior).
- Frontend: `npm run build` succeeds (no type errors).
- No secrets committed; config stays env-driven.
