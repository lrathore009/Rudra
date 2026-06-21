#!/usr/bin/env bash
# Sync live Cloudflare tunnel URL → Vercel RUDRA_BACKEND_URL + redeploy frontend.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
URL_FILE="$ROOT/.run/tunnel-url.txt"

TUNNEL_URL=""
if [ -f "$URL_FILE" ]; then
  TUNNEL_URL="$(tr -d '[:space:]' < "$URL_FILE")"
elif [ -f "$ROOT/.env" ]; then
  # Named tunnel: stable URL persisted in .env by setup-named-tunnel.sh
  TUNNEL_URL="$(grep -E '^RUDRA_PUBLIC_API_URL=' "$ROOT/.env" 2>/dev/null | cut -d= -f2- | tr -d '[:space:]' || true)"
fi

if [ -z "$TUNNEL_URL" ]; then
  echo "No tunnel URL found. Run: ./scripts/start-tunnel.sh"
  echo "  or (stable): ./scripts/setup-named-tunnel.sh api.yourdomain.com && ./scripts/start-named-tunnel.sh"
  exit 1
fi
if ! curl -fsS "${TUNNEL_URL}/api/v1/health" >/dev/null 2>&1; then
  echo "Tunnel URL not healthy: $TUNNEL_URL"
  echo "Run: ./scripts/start.sh && ./scripts/start-tunnel.sh"
  exit 1
fi

echo "→ Tunnel healthy: $TUNNEL_URL"
echo "→ Updating Vercel env RUDRA_BACKEND_URL (production)..."

cd "$ROOT/frontend"

if ! command -v vercel >/dev/null 2>&1; then
  NPM_VERCEL="npx --yes vercel"
else
  NPM_VERCEL="vercel"
fi

# Link once if this machine has never connected to rudra-kl5i.
if [ ! -f .vercel/project.json ]; then
  echo "→ Linking to Vercel project rudra-kl5i..."
  $NPM_VERCEL link --project rudra-kl5i --yes
fi

# Update existing vars (rm fails when missing; add fails when present).
upsert_env() {
  local name="$1" value="$2"
  if $NPM_VERCEL env ls production 2>/dev/null | grep -q " $name "; then
    printf '%s' "$value" | $NPM_VERCEL env update "$name" production --yes
  else
    printf '%s' "$value" | $NPM_VERCEL env add "$name" production
  fi
}

upsert_env RUDRA_BACKEND_URL "$TUNNEL_URL"
upsert_env NEXT_PUBLIC_API_URL "$TUNNEL_URL"

echo "→ Deploying frontend to production..."
$NPM_VERCEL deploy --prod --yes

echo "✓ Done. Test: curl https://rudra-kl5i.vercel.app/api/rudra/v1/health"
