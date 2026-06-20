# Rudra — Handoff Guide

You're receiving the complete **Rudra Personal Intelligence Operating System**.
This document captures **every resource, process, and installation step** needed
to run and continue developing Rudra on a fresh machine.

> **Recipient (Laxman):** read **`LAXMAN_HANDOFF.md`** first — current features,
> repo URLs, UI map, and deployment. Then this file for machine setup.
>
> **You have Claude Code / Cursor** — read `CLAUDE.md` for AI assistant context.

---

## 1. What Rudra is

A privacy-first, **local-first, $0** personal AI OS (think a private JARVIS):
- **Backend:** FastAPI (Python) — 9 specialized agents, SSE streaming, memory
  with vector search, research engine, multi-model brain, Founder OS.
- **Frontend:** Next.js 15 — **Rudraksha theme** + **sovereign tablet UI**
  (centered slate, realm rim, decree scroll).
- **Data:** PostgreSQL + pgvector (active vector store), Redis, Qdrant — all
  local via Docker.
- **AI:** Ollama (local `llama3.2` + `nomic-embed-text`); optional cloud
  fallback (Gemini → OpenAI → Anthropic) if API keys are added.
- **Cost:** $0. Nothing leaves the machine unless you add cloud keys or a tunnel.

**Primary repo:** https://github.com/lrathore009/Rudra (`main`)  
**Production frontend:** https://rudra-kl5i.vercel.app

---

## 2. Exact environment manifest (source machine)

| Component | Version | Notes |
|---|---|---|
| OS | macOS 26.5.1 (build 25F80) | Apple Silicon (`arm64`) |
| Homebrew | 6.0.1 | package manager |
| Node.js | 26.3.0 | via Homebrew |
| npm | 11.16.0 | bundled with Node |
| Python | 3.14.2 | project requires ≥ 3.11 |
| pip | 25.3 | |
| Docker | 29.5.3 | Docker Desktop |
| Docker Compose | v5.1.4 | `docker compose` (v2 syntax) |
| Ollama | 0.30.8 | local LLM runtime |
| gh (GitHub CLI) | 2.94.0 | for git auth + repo ops |
| cloudflared | 2026.6.0 | optional, for remote access tunnel |

**Ollama models (required):**
| Model | Size | Purpose |
|---|---|---|
| `llama3.2:latest` | 2.0 GB | chat / agents |
| `nomic-embed-text:latest` | 274 MB | embeddings (768-dim) |

**Docker images (pulled automatically by compose):**
| Image | Size | Service |
|---|---|---|
| `pgvector/pgvector:pg16` | 640 MB | Postgres + pgvector |
| `qdrant/qdrant:v1.12.1` | 291 MB | vector DB (optional) |
| `redis:7-alpine` | 58.7 MB | cache/queue (optional) |

**Ports used:** 3000 (frontend), 8000 (backend), 5432 (Postgres), 6333/6334
(Qdrant), 6379 (Redis), 11434 (Ollama).

---

## 3. Fresh-machine setup (from zero)

### 3a. Install system tools

**macOS (matches source machine):**
```bash
# Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Core tools
brew install node python git gh cloudflared ollama
brew install --cask docker        # then launch Docker Desktop once

# Start Ollama and pull models
brew services start ollama         # or: ollama serve
ollama pull llama3.2
ollama pull nomic-embed-text
```

**Linux (if not on macOS):** install Docker Engine + Compose, Node ≥ 18,
Python ≥ 3.11, then install Ollama from https://ollama.com/download and
`ollama pull llama3.2 nomic-embed-text`. Everything else is identical.

### 3b. Configure environment

`.env` lives at the repo root and is **gitignored** (it holds secrets). If you
received the folder directly it may already be present; otherwise create it:

```bash
cp .env.example .env
```

Then **rotate the secrets** (recommended on handoff — see Security below):
```bash
python3 -c "import secrets;print('RUDRA_SECRET_KEY='+secrets.token_urlsafe(48))"
python3 -c "import secrets;print('RUDRA_ENCRYPTION_KEY='+secrets.token_urlsafe(48))"
# paste the two values into .env
```

Defaults are zero-cost and work out of the box (local Postgres + Ollama). All
keys (`GOOGLE_AI_API_KEY`, `OPENAI_API_KEY`, etc.) are optional — leave blank.

### 3c. One-command startup

```bash
cd Rudra
./scripts/start.sh          # Docker infra + migrations + backend + frontend
./scripts/healthcheck.sh    # verify all services UP
```

Open http://localhost:3000 (API docs: http://localhost:8000/docs).

Stop: `./scripts/stop.sh --all`

---

## 4. Manual setup (if you prefer step-by-step)

```bash
# Infrastructure
docker compose up -d postgres qdrant redis

# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # or requirements.lock.txt for exact pins
alembic upgrade head                      # create DB schema
uvicorn rudra.main:app --reload           # http://localhost:8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev                               # http://localhost:3000
```

- `backend/requirements.txt` — loose version ranges (normal install).
- `backend/requirements.lock.txt` — **exact** frozen versions (108 pkgs) from the
  source machine, for byte-identical reproducibility.

---

## 5. Running tests

```bash
cd backend && source .venv/bin/activate
python -m pytest -q          # 20 integration tests; LLM/embeddings stubbed
```
DB-backed tests auto-skip if Postgres is down. No Ollama/cloud needed.

---

## 6. Transferring the folder (read before you copy)

The local folder contains large, **machine-specific** directories that should
**NOT** be copied (they're rebuilt on the new machine):

| Exclude | Why |
|---|---|
| `backend/.venv/` | Python venv is tied to OS/arch |
| `frontend/node_modules/` | native binaries, platform-specific |
| `frontend/.next/` | build cache |
| `logs/`, `.run/` | runtime artifacts |
| `backend/*.txt` | runtime fetch/cache files (UUID names) |
| `backend/**/__pycache__`, `.pytest_cache` | caches |

**Recommended — use the packaging script:**
```bash
chmod +x scripts/package-handoff.sh
./scripts/package-handoff.sh                    # → ~/Desktop/Rudra-handoff-YYYYMMDD.tgz
./scripts/package-handoff.sh /path/to/out.tgz   # custom output path
```

**Manual tar (from repo parent directory):**
```bash
tar --exclude='Rudra M4/Rudra M4/backend/.venv' \
    --exclude='Rudra M4/Rudra M4/frontend/node_modules' \
    --exclude='Rudra M4/Rudra M4/frontend/.next' \
    --exclude='Rudra M4/Rudra M4/logs' --exclude='Rudra M4/Rudra M4/.run' \
    --exclude='Rudra M4/Rudra M4/backend/*.txt' \
    --exclude='Rudra M4/Rudra M4/**/__pycache__' \
    -czf Rudra-handoff.tgz "Rudra M4/Rudra M4"
```

**Alternative (cleaner): use Git.** Code is on GitHub:
```bash
git clone https://github.com/lrathore009/Rudra.git
```
Send `.env` separately (secure channel) since it's gitignored.

> Whichever way you transfer, the recipient must run `pip install` and
> `npm install` and `ollama pull` on their own machine (Section 3).

---

## 7. Security notes (important for handoff)

- **`.env` contains secrets** (`RUDRA_SECRET_KEY`, `RUDRA_ENCRYPTION_KEY`). If
  you copy the folder as-is, those secrets travel with it. The recipient should
  **rotate them** (Section 3b) so they own fresh keys.
- `RUDRA_ENCRYPTION_KEY` decrypts any encrypted data. If the DB has encrypted
  rows, changing the key makes them unreadable — but Rudra currently stores
  memories in plaintext, so rotating now is safe.
- JWT auth enabled (`AUTH_REQUIRED=true`, login at `/login`). Rotate `OWNER_PASSWORD` on handoff.
- No cloud API keys are set (zero-cost). If you add any, never commit `.env`.
- The GitHub token used for pushing is stored in **your** macOS keychain, not in
  the repo — the recipient authenticates with their own `gh auth login`.

---

## 8. Remote access (optional)

The frontend is on Vercel; the backend stays local and is reached via a free
Cloudflare tunnel. Full instructions in **`DEPLOYMENT_GUIDE.md`**:
```bash
./scripts/start-tunnel.sh    # prints a public HTTPS URL for the backend
```
Set that URL as `NEXT_PUBLIC_API_URL` in Vercel and redeploy.

---

## 9. Documentation map

| File | What it covers |
|---|---|
| **`LAXMAN_HANDOFF.md`** | **Recipient start here** — current state, UI map, deploy, feature backlog |
| `CLAUDE.md` | Context for Claude Code / Cursor AI assistants |
| `HANDOFF.md` | This file — environment + transfer |
| `SETUP_GUIDE.md` | Detailed local setup |
| `DEPLOYMENT_GUIDE.md` | Vercel + Cloudflare tunnel |
| `SYSTEM_STATUS.md` | Current capability status |
| `KNOWN_ISSUES.md` | Gaps, limitations, roadmap to production |
| `README.md` | Project overview |
| `docs/ARCHITECTURE.md` | 11-layer architecture deep dive |
| `docs/ROADMAP.md` | 5-phase development roadmap |
| `docs/SECURITY.md` | Auth, rate limits, audit |
| `docs/KNOWLEDGE_GRAPH.md` | Entity graph |
| `docs/PROJECT_OS.md` | Founder project dashboard |
| `docs/DOCUMENT_BRAIN.md` | Document upload/search |
| `docs/INTEGRATIONS.md` | Calendar/email/briefing stubs |
| `docs/ZERO_COST.md` | How every cost center is made free |

---

## 10. Quick sanity checklist for the new owner

```bash
# 1. Tools present
node -v && python3 --version && docker --version && ollama --version

# 2. Models present
ollama list                       # expect llama3.2 + nomic-embed-text

# 3. Start everything
./scripts/start.sh && ./scripts/healthcheck.sh   # expect status: operational

# 4. Tests pass
cd backend && source .venv/bin/activate && python -m pytest -q   # 124 passed

# 5. Try it (login first)
open http://localhost:3000/login
```

If all five pass, you're ready to start improving Rudra. Ask Claude Code to read
`CLAUDE.md` and `KNOWN_ISSUES.md` for the best next steps.
