#!/usr/bin/env bash
# Sync live Cloudflare tunnel URL → Vercel RUDRA_BACKEND_URL + redeploy frontend.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
URL_FILE="$ROOT/.run/tunnel-url.txt"

if [ ! -f "$URL_FILE" ]; then
  echo "No tunnel URL found. Run: ./scripts/start-tunnel.sh"
  exit 1
fi

TUNNEL_URL="$(tr -d '[:space:]' < "$URL_FILE")"
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

# Remove old value if present (ignore failure)
$NPM_VERCEL env rm RUDRA_BACKEND_URL production --yes 2>/dev/null || true
printf '%s' "$TUNNEL_URL" | $NPM_VERCEL env add RUDRA_BACKEND_URL production

# Also keep NEXT_PUBLIC_API_URL in sync for any client-side fallbacks
$NPM_VERCEL env rm NEXT_PUBLIC_API_URL production --yes 2>/dev/null || true
printf '%s' "$TUNNEL_URL" | $NPM_VERCEL env add NEXT_PUBLIC_API_URL production

echo "→ Deploying frontend to production..."
$NPM_VERCEL deploy --prod --yes

echo "✓ Done. Test: curl https://rudra-kl5i.vercel.app/api/rudra/v1/health"
