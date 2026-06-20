# Rudra — Known Issues & Limitations

Status as of the sovereign tablet + Rudraksha theme pass (June 2026). Nothing
here blocks local development; these are gaps before *polished* production or
large-scale feature expansion.

## Security / Auth

1. **Single-owner model.** JWT login works (`/login`, `OWNER_USERNAME` /
   `OWNER_PASSWORD`), but there is no multi-user or role-based access. Fine for
   a private instance; expand before broader sharing.
2. **Secrets live in `.env`.** Rotate `RUDRA_SECRET_KEY`, `RUDRA_ENCRYPTION_KEY`,
   and `OWNER_PASSWORD` when handing off to a new developer machine.
3. **Rate limiting** exists on auth routes; review before high-traffic exposure.
4. **CORS** allows `*.vercel.app` via regex. Add custom domains to
   `CORS_ALLOW_ORIGINS` if needed.

## Deployment / Tunnel

5. **Quick Cloudflare tunnel URL changes on restart.** Update
   `NEXT_PUBLIC_API_URL` in Vercel and redeploy after each `start-tunnel.sh`
   restart. Use a **named tunnel** for a stable URL (`DEPLOYMENT_GUIDE.md`).
6. **Backend must stay running** on the owner's Mac for production Vercel UI to
   reach the API.

## Model quality

7. **`llama3.2` (3B) hallucinates** on complex factual prompts. For better local
   quality: `ollama pull qwen2.5:7b` + `OLLAMA_CHAT_MODEL=qwen2.5:7b`, or add
   `GOOGLE_AI_API_KEY` (Gemini free tier).

## Vector storage

8. **Qdrant is running but unused.** Active store is **pgvector** in Postgres.
9. **Embedding dimension fixed at 768** (`nomic-embed-text`). New model =
   new Alembic migration.

## Infrastructure

10. **Redis is provisioned but not used** by application code (reserved for
    caching / Celery).
11. **`start.sh` uses `nohup`** — if a process dies, re-run `start.sh`.

## Frontend

12. **Sovereign tablet is v1.** Realm drawers work but mobile polish (swipe,
    keyboard overlap, landscape) can be improved.
13. **Theme modes** (Sandhya / Nisha / Auto) are CSS-driven; no system
    `prefers-color-scheme` sync beyond Auto heuristic.
14. **`StarletteDeprecationWarning`** in tests is harmless.

## Tests

15. **DB-backed tests require local Postgres**; they skip if down. LLM and
    embeddings are stubbed — no Ollama/network needed for `pytest -q`.

## Suggested next features (for Laxman)

See **`LAXMAN_HANDOFF.md` §8** for a prioritized backlog.
