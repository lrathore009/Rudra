# Rudra — System Status

_Last verified: 2026-06-15 (local development environment)_

## Overview

Rudra is **production-ready for local development** and **deployed on Vercel**
(frontend) with a local backend exposed via Cloudflare tunnel. Core paths —
command execution (REST + SSE stream), agent routing, memory, research, auth —
are implemented and covered by **124 passing tests**.

| Capability | Status | Notes |
|---|---|---|
| Command center API | ✅ Working | `/api/v1/command` + `/api/v1/command/stream` (SSE) |
| SSE streaming + Stop | ✅ Working | Frontend streams tokens; Esc / stop button cancels |
| Single-voice Rudra | ✅ Working | Orchestrator strips sub-agent intros from user-facing text |
| 9 specialized agents | ✅ Working | All registered; robust auto-routing |
| Free source enrichment | ✅ Working | Per-agent free intelligence hubs wired |
| Multi-model brain | ✅ Working | Fallback: Gemini → OpenAI → Anthropic → Ollama |
| Local LLM (Ollama) | ✅ Working | `llama3.2`, env-driven via `OLLAMA_CHAT_MODEL` |
| Embeddings | ✅ Working | `nomic-embed-text` (768-dim), free/local |
| Memory CRUD + search | ✅ Working | pgvector cosine search |
| Research engine | ✅ Working | DuckDuckGo + Wikipedia (free), Tavily optional |
| Security | ✅ Working | JWT login, bcrypt, rate limits, audit log |
| Knowledge graph | ✅ Working | Entities, relationships, HUD panel in archive realm |
| Founder OS | ✅ Working | Projects, tasks — dominions realm drawer |
| Document brain | ✅ Working | Upload, chunk, embed, search — scriptorium realm |
| Daily briefing | ✅ Working | Mock calendar/email, scheduler job |
| **Rudraksha theme** | ✅ Shipped | Warm palette, living bead core, ambient audio, mala arc |
| **Sovereign tablet UI** | ✅ Shipped | Centered slate P1–P6: world strip, realm rim, decree scroll |
| Frontend | ✅ Working | Next.js 15; `npm run build` passes |
| Health checks | ✅ Working | `/api/v1/health/services` deep check |
| DevOps scripts | ✅ Working | `start.sh` / `stop.sh` / `healthcheck.sh` / `package-handoff.sh` |
| Tests | ✅ 124 passing | `backend/tests/` |
| Vercel production | ✅ Live | https://rudra-os-ashen.vercel.app |

## Live infrastructure (last check)

```
Frontend (:3000)   UP (local dev)
Backend  (:8000)   UP
Postgres (:5432)   UP   (pgvector enabled, migrations @ head)
Qdrant   (:6333)   UP   (optional — pgvector is the active vector store)
Redis    (:6379)   UP   (optional — not wired in app code yet)
Ollama   (:11434)  UP   (llama3.2, nomic-embed-text)
Tunnel             UP   (quick tunnel — URL in .run/tunnel-url.txt)
```

## Recent UI architecture

The command center is no longer a 3-column Bloomberg layout. It is a **sovereign
tablet** (`frontend/src/components/tablet/`):

- **P1** `SovereignTablet` — slate frame, bezel, vignette
- **P2** `WorldStrip` — greeting, status, gem vitals
- **P3** `RealmRim` + `RealmDrawer` — six realms (dominions, archive, council, …)
- **P4** `SutraField` + `DecreeScroll` — decree input and dialogue feed
- **P5** `GemGauge` — embedded success/subsystem vitals
- **P6** `InkText` — ink-unfold streaming answers

State and streaming logic remain in `frontend/src/app/page.tsx`.

## LLM configuration

- **Active provider:** Ollama (local, free, private) — `llama3.2`.
- **Cloud providers:** optional — keys blank → treated as unset.
- **Fallback order:** Gemini → OpenAI → Anthropic → Ollama.

## Production readiness

**Local development: ~95/100.** **Internet-facing:** requires stable tunnel (or
hosted backend), secret rotation on handoff, and review of `KNOWN_ISSUES.md`.

## Handoff

Recipient documentation: **`LAXMAN_HANDOFF.md`**. Package for transfer:
`./scripts/package-handoff.sh`.
