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

# Only one quick tunnel at a time (metrics port + connector conflicts).
if [ -f "$RUN_DIR/cloudflared.pid" ]; then
  old_pid="$(cat "$RUN_DIR/cloudflared.pid" 2>/dev/null || true)"
  if [ -n "$old_pid" ] && kill -0 "$old_pid" >/dev/null 2>&1; then
    say "Stopping previous cloudflared (pid $old_pid)..."
    kill "$old_pid" >/dev/null 2>&1 || true
    sleep 1
  fi
  rm -f "$RUN_DIR/cloudflared.pid"
fi
pkill -f 'cloudflared tunnel --no-autoupdate --url' >/dev/null 2>&1 || true
sleep 1

# Warn (don't block) if the backend isn't up yet.
if ! curl -fsS "http://localhost:${PORT}/api/v1/health" >/dev/null 2>&1; then
  say "Backend not detected on :${PORT} yet — start it first with ./scripts/start.sh"
fi

say "Starting Cloudflare Quick Tunnel → http://localhost:${PORT} ..."
: > "$LOG"
METRICS_PORT="${CLOUDFLARED_METRICS_PORT:-0}"
nohup cloudflared tunnel --no-autoupdate --metrics "127.0.0.1:${METRICS_PORT}" \
  --url "http://localhost:${PORT}" > "$LOG" 2>&1 &
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

# Verify the tunnel actually reaches the backend (up to ~60s — CF edge can be slow).
HEALTH_OK=false
for _ in $(seq 1 60); do
  if curl -fsS "${PUBLIC_URL}/api/v1/health" >/dev/null 2>&1; then
    HEALTH_OK=true
    break
  fi
  sleep 1
done

if [ "$HEALTH_OK" != true ]; then
  err "Tunnel URL obtained but backend health check failed after 60s."
  err "URL: $PUBLIC_URL — cloudflared may still be starting; check $LOG"
  err "If backend is up, wait 30s and run: curl ${PUBLIC_URL}/api/v1/health"
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
echo "Next: ./scripts/sync-vercel-backend.sh   (or set RUDRA_BACKEND_URL=$PUBLIC_URL in Vercel)"
echo "Stop: ./scripts/stop.sh --tunnel   (or kill \$(cat $RUN_DIR/cloudflared.pid))"
