#!/usr/bin/env bash
# Rudra — expose the local backend (:8000) over HTTPS via a Cloudflare Quick Tunnel.
#
# Keeps Rudra local-first: only the API port is proxied through Cloudflare's edge.
# Your data, Ollama models, and databases never leave this machine.
#
# Quick tunnel = no Cloudflare account, free, instant. The public URL is RANDOM
# and CHANGES every restart. For a stable URL, use a named tunnel (see
# DEPLOYMENT_GUIDE.md → "Stable URL").
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PORT="${RUDRA_BACKEND_PORT:-8000}"
LOG_DIR="$ROOT/logs"
RUN_DIR="$ROOT/.run"
LOG="$LOG_DIR/cloudflared.log"
URL_FILE="$RUN_DIR/tunnel-url.txt"
mkdir -p "$LOG_DIR" "$RUN_DIR"

say() { printf "\033[1;36m→ %s\033[0m\n" "$1"; }
ok()  { printf "\033[1;32m✓ %s\033[0m\n" "$1"; }
err() { printf "\033[1;31m✗ %s\033[0m\n" "$1"; }

command -v cloudflared >/dev/null 2>&1 || { err "cloudflared not installed. Run: brew install cloudflared"; exit 1; }

# Warn (don't block) if the backend isn't up yet.
if ! curl -fsS "http://localhost:${PORT}/api/v1/health" >/dev/null 2>&1; then
  say "Backend not detected on :${PORT} yet — start it first with ./scripts/start.sh"
fi

say "Starting Cloudflare Quick Tunnel → http://localhost:${PORT} ..."
: > "$LOG"
nohup cloudflared tunnel --no-autoupdate --url "http://localhost:${PORT}" \
  > "$LOG" 2>&1 &
echo $! > "$RUN_DIR/cloudflared.pid"

# Wait for the public URL to appear in the log (up to ~30s).
PUBLIC_URL=""
for _ in $(seq 1 30); do
  PUBLIC_URL="$(grep -Eo 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' "$LOG" | head -1 || true)"
  [ -n "$PUBLIC_URL" ] && break
  sleep 1
done

if [ -z "$PUBLIC_URL" ]; then
  err "Could not obtain tunnel URL. Check $LOG"
  exit 1
fi

# Verify the tunnel actually reaches the backend before saving.
HEALTH_OK=false
for _ in $(seq 1 15); do
  if curl -fsS "${PUBLIC_URL}/api/v1/health" >/dev/null 2>&1; then
    HEALTH_OK=true
    break
  fi
  sleep 1
done

if [ "$HEALTH_OK" != true ]; then
  err "Tunnel URL obtained but backend health check failed. Is uvicorn running on :${PORT}?"
  err "URL was: $PUBLIC_URL"
  exit 1
fi

echo "$PUBLIC_URL" > "$URL_FILE"
echo ""
ok "Tunnel is live:"
echo "   Public API:  $PUBLIC_URL"
echo "   Health:      $PUBLIC_URL/api/v1/health"
echo "   URL saved:   $URL_FILE"
echo "   Logs:        $LOG"
echo ""
echo "Next: set NEXT_PUBLIC_API_URL=$PUBLIC_URL in Vercel → Settings → Environment"
echo "Stop: ./scripts/stop.sh --tunnel   (or kill \$(cat $RUN_DIR/cloudflared.pid))"
