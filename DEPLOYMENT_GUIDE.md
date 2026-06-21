# Rudra — Deployment Guide

Rudra is **local-first**: the backend (FastAPI + Ollama + Postgres + Redis +
Qdrant) and all your data stay on your machine. Only the frontend is hosted on
Vercel, and it reaches your local backend through a **Cloudflare Tunnel** —
nothing sensitive leaves your Mac except API traffic on port 8000.

```
[ Browser ] → [ Vercel: Next.js frontend ] → [ Cloudflare edge (HTTPS) ]
                                                      │  tunnel
                                                      ▼
                                       [ Your Mac: FastAPI :8000 ]
                                       [ Ollama · Postgres · Redis · Qdrant ]
```

---

## 1. Local startup

```bash
cd /Users/laxman009/Rudra
./scripts/start.sh          # infra + migrations + backend (:8000) + frontend (:3000)
./scripts/healthcheck.sh    # verify everything is UP
```

Prerequisites (one time): Docker, Python 3.11+, Node 18+, Ollama with
`llama3.2` + `nomic-embed-text` pulled. See `SETUP_GUIDE.md`.

## 2. Tunnel startup (expose the backend over HTTPS)

```bash
./scripts/start-tunnel.sh
```

Output (example):

```
✓ Tunnel is live:
   Public API:  https://honolulu-accomplished-technician-television.trycloudflare.com
   Health:      https://honolulu-accomplished-technician-television.trycloudflare.com/api/v1/health
```

- The public URL is also written to `.run/tunnel-url.txt`.
- Logs: `logs/cloudflared.log`.
- **The quick-tunnel URL changes every restart.** For a permanent URL, see
  "Stable URL (named tunnel)" below.

Stop the tunnel:

```bash
./scripts/stop.sh --tunnel        # stop tunnel only
./scripts/stop.sh --all           # stop backend + frontend + tunnel + Docker infra
# or: kill $(cat .run/cloudflared.pid)
```

## 3. Vercel deployment

**Canonical production URL (Trishula Cosmos theme):**  
https://rudra-kl5i.vercel.app  
Login: https://rudra-kl5i.vercel.app/login

The repo **https://github.com/lrathore009/Rudra** is connected to Vercel with
**Root Directory = `frontend`**. Every push to `main` triggers a deploy. To
deploy manually: push to `main`, or in the Vercel dashboard click **Redeploy**.

### Consolidate to one Vercel project (recommended)

Three Vercel projects were previously hooked to the same repo (`rudra`,
`rudra-1efy`, `rudra-kl5i`). Only **`rudra-kl5i`** serves the current theme.
To avoid triple deploys and stale URLs:

1. Open [Vercel dashboard](https://vercel.com/laxman-singh-rathore-s-projects) → project **`rudra-kl5i`**.
2. **Settings → Domains** — add your preferred hostname:
   - Keep `rudra-kl5i.vercel.app` (default), or
   - Move **`rudra-os-ashen.vercel.app`** here if you still use that link (remove it from the old project first).
3. **Settings → Environment Variables** — set `NEXT_PUBLIC_API_URL` (tunnel URL) and optionally:
   - `NEXT_PUBLIC_APP_URL` = `https://rudra-kl5i.vercel.app` (for Open Graph / metadata).
4. **Redeploy** `rudra-kl5i` after env changes.
5. On projects **`rudra`** and **`rudra-1efy`** (and any duplicate): **Settings → Git → Disconnect** (or delete the project if unused).

> **Do not use** https://rudra-os-ashen.vercel.app unless you re-point that domain to `rudra-kl5i` — it may still show an older build.

Build settings (auto-detected, for reference):
- Framework: **Next.js**
- Root Directory: **frontend**
- Build command: `next build`
- Install command: `npm install`

## 4. Environment variables

### Vercel → Settings → Environment Variables

| Name | Value | Environments |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | the tunnel URL from step 2, e.g. `https://<random>.trycloudflare.com` | Production, Preview, Development |
| `NEXT_PUBLIC_APP_URL` | `https://rudra-kl5i.vercel.app` (canonical frontend URL) | Production |

Steps:
1. Run `./scripts/start-tunnel.sh` and copy the **Public API** URL.
2. Vercel → your project → **Settings → Environment Variables**.
3. Add `NEXT_PUBLIC_API_URL` = the tunnel URL. **No trailing slash.**
4. **Redeploy** (env vars only apply to new builds): Deployments → ⋯ → Redeploy.

> Because `NEXT_PUBLIC_` vars are baked in at **build time**, you must redeploy
> whenever the tunnel URL changes. This is the main reason to use a stable named
> tunnel for anything beyond quick testing.

### Backend `.env` (local) — CORS

Already configured to accept Vercel origins:

```
CORS_ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CORS_ALLOW_ORIGIN_REGEX=https://.*\.vercel\.app
```

If you use a **custom domain** on Vercel, add it to `CORS_ALLOW_ORIGINS`
(comma-separated) and restart the backend.

### Frontend `.env.local` (local dev only)

```bash
cp frontend/.env.example frontend/.env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000   (default; only needed to override)
```

## 5. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Frontend shows "offline" / API errors | `NEXT_PUBLIC_API_URL` not set or stale on Vercel | Set it to the current tunnel URL, then **redeploy** |
| CORS error in browser console | Origin not allowed by backend | Ensure Vercel domain matches `CORS_ALLOW_ORIGIN_REGEX` or add it to `CORS_ALLOW_ORIGINS`; restart backend |
| Tunnel URL stopped working | Quick tunnel restarted → new URL | Re-run `start-tunnel.sh`, update Vercel env, redeploy |
| `cloudflared not installed` | Missing binary | `brew install cloudflared` |
| Tunnel up but 502/empty | Backend not running | `./scripts/start.sh`, confirm `curl localhost:8000/api/v1/health` |
| Vercel build fails | Type error in `next build` | Reproduce locally: `cd frontend && npm run build` |
| "No AI model connected" in responses | Ollama not running | `ollama serve` / `brew services start ollama`; `ollama list` |

Verify external reachability any time:

```bash
curl "$(cat .run/tunnel-url.txt)/api/v1/health"
```

## 6. Security notes

- **Quick-tunnel URLs are public and unauthenticated.** Anyone with the URL can
  reach your API. Rudra runs in single-user mode (`owner`) with no login yet, so
  treat the URL as a secret and stop the tunnel when not in use.
- For real protection, put **Cloudflare Access** (free, email/OTP) in front of a
  **named tunnel**, or keep the tunnel off except during active use.
- Secrets (`.env`, rotated `RUDRA_SECRET_KEY` / `RUDRA_ENCRYPTION_KEY`) are
  gitignored and never leave the machine.
- The tunnel only proxies port 8000 — Postgres/Redis/Qdrant/Ollama are **not**
  exposed.
- Do not commit `.run/tunnel-url.txt` or `logs/` (already gitignored).

## Stable URL (named tunnel) — recommended for production

Quick tunnels (`*.trycloudflare.com`) are ephemeral and sometimes fail DNS
registration (NXDOMAIN). For a **permanent** API URL use a **named tunnel** with
your own domain on Cloudflare DNS.

### Prerequisites

1. [Free Cloudflare account](https://dash.cloudflare.com/sign-up)
2. A domain on Cloudflare DNS — register in [Cloudflare Registrar](https://dash.cloudflare.com/?to=/:account/domains/register) or transfer/add an existing domain
3. Pick a hostname, e.g. `api.yourdomain.com`

### One-time setup

```bash
./scripts/setup-named-tunnel.sh api.yourdomain.com
```

This logs in to Cloudflare (browser), creates tunnel `rudra`, routes DNS, and
writes `infrastructure/cloudflared/config.yml`.

### Start + sync Vercel (once)

```bash
./scripts/start.sh                    # backend on :8000
./scripts/start-named-tunnel.sh       # stable HTTPS URL
./scripts/sync-vercel-backend.sh      # push URL to Vercel + prod deploy
```

After that, `NEXT_PUBLIC_API_URL` stays fixed — no updates when you restart the
tunnel. Keep `cloudflared` and the backend running on your Mac while using
production.

Stop: `./scripts/stop.sh --tunnel`
