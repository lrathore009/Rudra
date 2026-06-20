# Rudra Security

Rudra is a **local-first, single-owner** system. Security defaults assume one trusted operator on private infrastructure.

## Authentication

- JWT login at `POST /api/v1/auth/login`
- Owner account bootstrapped on startup from `OWNER_USERNAME` / `OWNER_PASSWORD`
- `AUTH_REQUIRED=true` by default — APIs require `Authorization: Bearer <token>`
- Frontend stores token in **sessionStorage** (cleared when tab closes)
- Login UI: `/login` (HUD-themed)

## API hardening

- Rate limiting via `RateLimitMiddleware` (`RATE_LIMIT_PER_MINUTE`, stricter on command/memory/research/upload)
- Security headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, HSTS in production
- CORS: env-driven `CORS_ALLOW_ORIGINS` + `CORS_ALLOW_ORIGIN_REGEX` (Vercel)

## Audit logging

Immutable `audit_logs` table records:

- Login success/failure, logout, auth denied
- Command execution, memory writes, document uploads

## Secrets

Never commit `.env`. Rotate `RUDRA_SECRET_KEY` and `RUDRA_ENCRYPTION_KEY` after handoff.

## Production checklist

1. Set strong `OWNER_PASSWORD`
2. Set `RUDRA_ENV=production`
3. Restrict CORS to your domains only
4. Run behind HTTPS (tunnel or reverse proxy)
5. Keep Postgres off the public internet
