# Running Rudra at $0 — The Complete Zero-Cost Guide

Rudra is designed to run **fully free and fully private**. This guide documents every
cost center, the free replacement now wired into the code, and a long list of
suggestions to keep Rudra successful for years without spending a rupee.

---

## TL;DR — The free stack

| Layer | Paid option (avoided) | Free option (active) | Cost |
|-------|----------------------|----------------------|------|
| Database | Supabase Pro, RDS | **Local Postgres + pgvector (Docker)** | $0 |
| Vectors | Pinecone, Qdrant Cloud | **pgvector in local Postgres** | $0 |
| LLM (reasoning) | OpenAI, Anthropic | **Ollama (local)** or **Gemini free tier** | $0 |
| Embeddings | OpenAI text-embedding-3 | **Ollama nomic-embed-text** or **Gemini text-embedding-004** | $0 |
| Web research | Tavily, SerpAPI | **DuckDuckGo (ddgs) + Wikipedia API** | $0 |
| Hosting | Cloud VPS | **Your own machine (local-first)** | $0 |
| Cache/queue | Redis Cloud | **Local Redis (Docker)** or skip in Phase 1 | $0 |
| Voice (Phase 2) | ElevenLabs, Deepgram | **Browser Web Speech API + local Whisper** | $0 |

Everything above is already configured as the default. You only choose **one** LLM
option (Ollama *or* a free Gemini key).

---

## 1. Database — Local Postgres + pgvector (free, never pauses)

Already the active default in `.env`:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=rudra
POSTGRES_PASSWORD=rudra_dev_password
POSTGRES_DB=rudra
# DATABASE_URL_OVERRIDE left blank → uses the parts above
```

Start it and migrate:

```bash
cd /Users/laxman009/Rudra
docker compose up -d postgres
cd backend && source .venv/bin/activate
alembic upgrade head
```

**Why local over Supabase free tier?**
- Supabase free projects **auto-pause after ~7 days** of inactivity — bad for a
  "lifelong companion" that you might not touch every week.
- Local Postgres is **fully private** (aligns with Rudra's mission) and has no row/
  storage caps.
- Supabase remains available as a documented option (commented block in `.env`) if
  you ever want managed hosting or multi-device sync.

---

## 2. LLM Brain — pick ONE free path

The brain routes **free-first**: it tries Ollama, then Gemini, then any paid keys.

### Option A — Ollama (100% local, 100% private, no key)

```bash
brew install ollama
ollama serve            # runs in background (or just `ollama run` once)
ollama pull llama3.2            # chat / reasoning  (~2 GB)
ollama pull nomic-embed-text    # embeddings        (~275 MB)
```

That's it — Rudra will detect Ollama at `http://localhost:11434`. No `.env` changes
needed. Best for privacy; needs a few GB of disk and a reasonably modern machine.

### Option B — Google Gemini free tier (no install, generous limits)

1. Get a free key: https://aistudio.google.com/apikey
2. Put it in `.env`:

```env
GOOGLE_AI_API_KEY=your_free_key_here
```

Free tier (as of 2026) covers personal daily use comfortably. Used for both chat
(`gemini-2.0-flash`) and embeddings (`text-embedding-004`). Lightweight — no big
downloads — but requests leave your machine.

> Tip: configure **both**. Ollama handles private/offline work; Gemini is the cloud
> fallback when Ollama is off or you want a stronger answer.

### Other free LLM options you can add later
- **Groq** free tier — extremely fast Llama/Mixtral inference (add a provider like
  the Gemini one).
- **OpenRouter** — has several `:free` models behind one key.
- **Cloudflare Workers AI** — free daily allocation.

---

## 3. Embeddings — free 768-dim pipeline (now implemented)

`backend/rudra/brain/embeddings.py` generates vectors with, in order:
1. Ollama `nomic-embed-text` (local)
2. Gemini `text-embedding-004` (free tier)
3. OpenAI (only if a key is set)

Memories are auto-embedded on creation. If no embedding backend is available, the
memory is still stored (without a vector) so nothing breaks. Semantic search
(`search_by_text`) embeds the query for free and falls back to recent memories when
embeddings are unavailable.

Vector dimension is **768** (`EMBEDDING_DIM` in `.env`) to match the free models.

---

## 4. Research — free, no API keys

`backend/rudra/research/engine.py` now uses:
- **DuckDuckGo** via the `ddgs` package (no key, no quota)
- **Wikipedia** via the public MediaWiki API (no key)

Tavily/SerpAPI remain optional fallbacks if you ever add a (free-tier) key. The
research engine still does credibility scoring and confidence-weighted synthesis —
just on free sources.

### More free research sources to add later
- **arXiv API** — academic papers (free, no key)
- **Semantic Scholar API** — free tier
- **Hacker News Algolia API** — free
- **RSS feeds** — free news ingestion
- **PubMed E-utilities** — free

---

## 5. Hosting — local-first ($0)

Run everything on your own machine:

```bash
# Terminal 1 — database (Docker)
docker compose up -d postgres

# Terminal 2 — backend
cd backend && source .venv/bin/activate
uvicorn rudra.main:app --reload --port 8000

# Terminal 3 — frontend
cd frontend && npm run dev
```

Open http://localhost:3000.

### Free remote access (when you want it)
- **Cloudflare Tunnel** (`cloudflared`) — free, exposes localhost securely with HTTPS.
- **Tailscale** — free tier; reach Rudra from your phone/laptop over a private VPN.
- **ngrok** free tier — quick temporary tunnels.

### Free deployment targets (if you ever leave your machine)
- **Oracle Cloud Always Free** — 4 ARM cores + 24 GB RAM, genuinely free forever.
  Big enough to run Ollama + Postgres + Rudra.
- **Fly.io / Render free tiers** — small apps.
- **Hugging Face Spaces** — free CPU for the frontend/demo.

---

## 6. Redis — optional in Phase 1

Phase 1 doesn't require Redis. When you reach Phase 2 background tasks, run it free
locally:

```bash
docker compose up -d redis
```

---

## 7. Voice (Phase 2) — free path

- **Speech-to-text:** browser **Web Speech API** (free, built into Chrome) or local
  **Whisper** (`whisper.cpp` / `faster-whisper`) — free, private.
- **Text-to-speech:** browser **SpeechSynthesis API** (free) or **Piper** (free,
  local, high quality).
- **Wake word:** **openWakeWord** (free, open source).

No ElevenLabs/Deepgram needed.

---

## 8. Cost-control habits (keep it free forever)

1. **Default to Ollama** for routine tasks; reserve cloud free tiers for hard queries.
2. **Cache aggressively** — store research results as memories so you never re-query.
3. **Batch + summarize** before sending to any cloud model to minimize tokens.
4. **Set `EMBEDDING_PROVIDER=ollama`** to keep all embeddings local and unmetered.
5. **Prune low-importance memories** periodically (Rudra supports soft/hard delete).
6. **Watch free-tier limits** — Gemini/Groq have daily caps; Ollama has none.
7. **Use `model_tier="fast"`** for routing/classification to stay light.

---

## 9. What changed in the code for zero-cost

| File | Change |
|------|--------|
| `.env` | Local Postgres default; free LLM/embedding/research config; Supabase commented |
| `core/config.py` | Added `embedding_provider`, `embedding_dim`, free-first settings |
| `brain/orchestrator.py` | Added **GeminiProvider**; free-first model order; lazy provider init (no crash without paid keys) |
| `brain/embeddings.py` | **New** free embedding service (Ollama → Gemini → OpenAI) |
| `memory/service.py` | Auto-embeds memories; added `search_by_text` |
| `memory/models/memory.py` | Vector dimension 768 (free models) |
| `research/engine.py` | **DuckDuckGo + Wikipedia** free providers; Tavily optional |
| `requirements.txt` | Added `ddgs` (free search) |
| `alembic/.../001_*.py` | Vector(768) |

---

## 10. Verified working (zero-cost)

- Local Postgres + pgvector: **8 tables created, `vector` extension active**
- Backend: **operational**, 9 agents online, DB reads/writes working
- Frontend: **HTTP 200**, command center live
- All paid dependencies removed from the default path
- Backend starts cleanly with **no API keys at all** (add one free LLM option to get
  actual agent responses)

### The only thing left for full AI responses
Pick one (both free):
- `brew install ollama && ollama pull llama3.2 && ollama pull nomic-embed-text`, **or**
- add a free `GOOGLE_AI_API_KEY` from https://aistudio.google.com/apikey

Then commands in the UI will produce real answers — at $0.
