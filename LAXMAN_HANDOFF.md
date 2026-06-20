# Rudra — Handoff for Laxman

You are receiving the **Rudra Personal Intelligence OS** at its current development
state (June 2026). This file is your starting point for setup, feature work, and
deployment.

**Read order:** this file → `HANDOFF.md` (machine setup) → `CLAUDE.md` (AI assistant
context) → `KNOWN_ISSUES.md` (what to improve next).

---

## 1. What you are getting

A **privacy-first, local-first, $0** personal AI command center:

| Layer | Stack |
|---|---|
| Backend | FastAPI, 9 agents, SSE streaming, memory + pgvector, research, Founder OS |
| Frontend | Next.js 15 — **Rudraksha theme** + **sovereign tablet UI** |
| Data | Postgres + pgvector, Redis + Qdrant (provisioned, mostly unused) |
| AI | Ollama local (`llama3.2` + `nomic-embed-text`); optional cloud fallback |
| Deploy | Frontend on **Vercel**; backend stays local via **Cloudflare tunnel** |

**Production URL:** https://rudra-kl5i.vercel.app  
**Git (canonical):** https://github.com/lrathore009/Rudra (`main`)

---

## 2. What was built (recent commits)

| Commit | Summary |
|---|---|
| `9992116` | **Sovereign tablet UI (P1–P6)** — centered slate, world strip, realm rim drawers, decree scroll, sutra field, ink streaming, gem gauges |
| `9d72e83` | **Rudraksha theme** — living bead core, warm palette, ambient audio, mala arc, streaming thread |
| `cd3045c` | Single-voice Rudra orchestrator + bounded stream enrichment |
| `ba30cbd` | SSE command streaming with Stop / Esc cancel |
| `20b8c56` | Free intelligence sources wired for all nine specialist agents |

**Tests:** `124 passed` (`cd backend && python -m pytest -q`)  
**Frontend build:** `cd frontend && npm run build` (required before every push)

---

## 3. Frontend architecture (where to edit features)

The old 3-column “ops desk” is gone. The main UI is a **single centered tablet**.

```
frontend/src/
├── app/
│   ├── page.tsx              # State, streaming, auth — wires SovereignView
│   ├── login/page.tsx        # Login inside sovereign tablet frame
│   └── globals.css           # Rudraksha + sovereign tablet CSS
├── components/
│   ├── tablet/               # ★ PRIMARY UI — start here for layout/features
│   │   ├── SovereignView.tsx # Composes all tablet sections
│   │   ├── SovereignTablet.tsx
│   │   ├── WorldStrip.tsx    # P2 world-first greeting + gem vitals
│   │   ├── RealmRim.tsx      # P3 six realm navigation beads
│   │   ├── RealmDrawer.tsx   # Slide-up panels per realm
│   │   ├── SutraField.tsx    # P4 decree input (voice, stamp send)
│   │   ├── DecreeScroll.tsx  # Dialogue feed
│   │   ├── InkText.tsx       # P6 streaming ink text
│   │   └── GemGauge.tsx      # P5 vitals
│   └── hud/                  # Panels pulled into realm drawers
│       ├── RudrakshaCore.tsx # Central bead + facet ring
│       ├── DailyBriefingPanel.tsx, FounderOSPanel.tsx, …
├── lib/
│   ├── api.ts                # All API calls (API_BASE from env)
│   ├── rudra-theme.ts        # Theme mode, haptics, greetings, facet colors
│   └── sound.ts              # Ambient audio, facet chimes
```

### Realm → panel mapping (`SovereignView.tsx`)

| Realm | Contents |
|---|---|
| **dominions** | Daily briefing + Founder OS |
| **archive** | Knowledge graph + research library |
| **council** | Nine facets + skills list |
| **scriptorium** | Specialist hub + document brain |
| **horizon** | Specialist hub |
| **engine** | Process stream, service vitals, scheduler jobs |

### Theme modes

Auto / Sandhya (day) / Nisha (night) — cycle via header control; persisted in
`localStorage` key `rudra-theme-mode`.

---

## 4. Backend architecture (where to edit features)

```
backend/rudra/
├── api/routes/          # REST endpoints (command, memory, research, …)
├── agents/base.py       # 9 agents + routing
├── brain/orchestrator.py
├── command/             # RudraCommandService — single voice + SSE stream
├── memory/              # CRUD + semantic search (pgvector)
├── core/config.py       # ★ ALL settings — never hardcode elsewhere
└── tests/               # 124 tests; LLM/embeddings stubbed in conftest
```

**Streaming:** `POST /api/v1/command/stream` (SSE). Frontend uses this from
`page.tsx` via `streamCommand()` in `lib/api.ts`.

**Auth:** JWT login at `/api/v1/auth/login`. UI at `/login`. Credentials from
`OWNER_USERNAME` / `OWNER_PASSWORD` in root `.env`.

---

## 5. Setup on your machine

### Option A — Git clone (recommended)

```bash
git clone https://github.com/lrathore009/Rudra.git
cd Rudra-OS
cp .env.example .env          # then edit secrets (see §7)
./scripts/start.sh
./scripts/healthcheck.sh
```

Open http://localhost:3000/login

### Option B — Folder transfer (zip/tar from Vikram)

If you received `Rudra-handoff.tgz` instead of cloning:

```bash
tar -xzf Rudra-handoff.tgz
cd "Rudra M4/Rudra M4"    # or whatever folder name was used
cp .env.example .env      # or use the .env Vikram sent separately
./scripts/start.sh
```

Then run installs (venv + npm) as in `HANDOFF.md` §3–4 if `start.sh` has not
already done them.

### Prerequisites

Docker, Python ≥ 3.11, Node ≥ 18, Ollama with `llama3.2` + `nomic-embed-text`.
Full install steps: `HANDOFF.md` §3.

---

## 6. Deployment (Vercel + tunnel)

Backend **never** goes to Vercel — only the Next.js frontend.

```bash
# 1. Start local backend
./scripts/start.sh

# 2. Expose backend over HTTPS
./scripts/start-tunnel.sh
# URL saved to .run/tunnel-url.txt

# 3. Set Vercel env on project **rudra-kl5i** (one-time per tunnel URL change)
#    NEXT_PUBLIC_API_URL = <tunnel URL, no trailing slash>
#    NEXT_PUBLIC_APP_URL = https://rudra-kl5i.vercel.app

# 4. Deploy — push to main (auto-deploy) or Vercel dashboard → Redeploy
git push origin main
# Live: https://rudra-kl5i.vercel.app
```

Details: `DEPLOYMENT_GUIDE.md`

**Current tunnel (may change on restart):** check `.run/tunnel-url.txt` on the
machine running the backend.

---

## 7. Secrets & security on handoff

- `.env` is **gitignored**. Vikram may send it separately (secure channel).
- **Rotate on your machine** (recommended):
  - `RUDRA_SECRET_KEY`, `RUDRA_ENCRYPTION_KEY` — generate new values
  - `OWNER_PASSWORD` — set your own login password
- Never commit `.env`, API keys, or tunnel tokens.

---

## 8. Suggested feature work (open items)

Prioritized gaps — pick what the product owner wants next:

1. **Stable tunnel** — named Cloudflare tunnel so Vercel `NEXT_PUBLIC_API_URL`
   does not change every restart (`DEPLOYMENT_GUIDE.md` § stable URL).
2. **Redis / task queue** — provisioned in Docker, not wired in app code.
3. **Qdrant adapter** — optional alternative to pgvector.
4. **Model upgrade** — `ollama pull qwen2.5:7b` + `OLLAMA_CHAT_MODEL=qwen2.5:7b`
   for better answers on local hardware.
5. **Realm drawer polish** — mobile layout, swipe gestures, realm-specific empty states.
6. **Real integrations** — replace mock calendar/email in daily briefing.
7. **Multi-user** — today is single-owner JWT; see `docs/SECURITY.md`.

Full list: `KNOWN_ISSUES.md`

---

## 9. Definition of done (for your PRs)

```bash
cd backend && source .venv/bin/activate && python -m pytest -q   # all pass
cd frontend && npm run build                                    # no type errors
```

- Conventional commits: `feat:`, `fix:`, `chore:`, etc.
- No secrets in git.
- Run `npm run build` before pushing frontend — Vercel type-checks on build.

---

## 10. Quick sanity checklist

```bash
node -v && python3 --version && docker --version && ollama --version
ollama list                                    # llama3.2 + nomic-embed-text
./scripts/start.sh && ./scripts/healthcheck.sh # all UP
cd backend && source .venv/bin/activate && python -m pytest -q
open http://localhost:3000/login
```

If all pass, you are ready to ship features. Use Claude Code / Cursor with
`CLAUDE.md` loaded for fastest onboarding.

---

## 11. Contact / repo workflow

- **Push to:** `origin` → `lrathore009/Rudra` (`main` — triggers Vercel deploy to **rudra-kl5i**)
- **Vercel project:** `rudra-os` under `rathorevikram0620-5183s-projects`

Questions about product direction → ask Vikram before large UI rewrites.
