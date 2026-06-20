# Rudra — Setup Guide (Local Development)

Rudra runs **fully local and free** ($0): local Postgres + pgvector, local
Ollama for chat and embeddings, and free web research (DuckDuckGo + Wikipedia).
No cloud API keys are required.

## 1. Prerequisites

| Tool | Install (macOS) | Why |
|---|---|---|
| Docker Desktop | https://docker.com | Postgres, Qdrant, Redis |
| Python 3.11+ | `brew install python` | Backend |
| Node.js 18+ | `brew install node` | Frontend |
| Ollama | `brew install ollama` | Local LLM + embeddings |

Pull the local models (one time):

```bash
ollama pull llama3.2          # chat model
ollama pull nomic-embed-text  # embeddings (768-dim)
```

> Want better quality (still free)? `ollama pull qwen2.5:7b` then set
> `OLLAMA_CHAT_MODEL=qwen2.5:7b` in `.env`.

## 2. Configure environment

A working `.env` already exists at the repo root with safe local defaults.
If starting fresh:

```bash
cp .env.example .env
```

Key variables (all have safe defaults):

```
OLLAMA_CHAT_MODEL=llama3.2          # local chat model (env-driven)
EMBEDDING_PROVIDER=auto             # ollama → gemini → openai
POSTGRES_HOST=localhost             # local Postgres via Docker
REDIS_URL=redis://localhost:6379/0
QDRANT_HOST=localhost
# Optional cloud (leave blank for $0): GOOGLE_AI_API_KEY / OPENAI_API_KEY / ANTHROPIC_API_KEY / TAVILY_API_KEY
```

> The two secret values (`RUDRA_SECRET_KEY`, `RUDRA_ENCRYPTION_KEY`) are
> generated strong by default. Regenerate any time with:
> `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`.

## 3. One-command startup

```bash
./scripts/start.sh
```

This starts Docker infra (Postgres/Qdrant/Redis), waits for Postgres, installs
backend + frontend deps, runs migrations, and launches both servers.

- Frontend: http://localhost:3000
- Backend:  http://localhost:8000  (API docs: http://localhost:8000/docs)
- Logs:     `logs/backend.log`, `logs/frontend.log`

## 4. Verify

```bash
./scripts/healthcheck.sh
```

Expect all ports UP and `status: operational`.

## 5. Stop

```bash
./scripts/stop.sh           # stops backend + frontend
./scripts/stop.sh --infra   # also stops Docker containers
```

## Manual startup (alternative)

```bash
# Infra
docker compose up -d postgres qdrant redis

# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn rudra.main:app --reload   # :8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev                        # :3000
```

## Running tests

```bash
cd backend && source .venv/bin/activate
python -m pytest -q
```

DB-backed tests auto-skip if Postgres is not running; the LLM and embeddings
are stubbed, so tests never require Ollama or cloud keys.
