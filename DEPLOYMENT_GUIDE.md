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

The repo is already connected to Vercel with **Root Directory = `frontend`**.
Every push to `main` triggers a deploy. To deploy manually: push to `main`, or
in the Vercel dashboard click **Redeploy**.

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

## Stable URL (named tunnel) — optional upgrade

Quick tunnels are great for testing but change on restart. For a permanent URL
(requires a free Cloudflare account + a domain on Cloudflare):

```bash
cloudflared tunnel login
cloudflared tunnel create rudra
# Map a hostname (e.g. api.yourdomain.com) to the tunnel:
cloudflared tunnel route dns rudra api.yourdomain.com
# Run it (ingress → http://localhost:8000):
cloudflared tunnel run --url http://localhost:8000 rudra
```

Then set `NEXT_PUBLIC_API_URL=https://api.yourdomain.com` in Vercel once — no
more per-restart updates.
