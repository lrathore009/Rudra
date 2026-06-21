#!/usr/bin/env bash
# Start the stable Cloudflare Named Tunnel (requires setup-named-tunnel.sh first).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PORT="${RUDRA_BACKEND_PORT:-8000}"
CF_DIR="$ROOT/infrastructure/cloudflared"
CONFIG="$CF_DIR/config.yml"
LOG_DIR="$ROOT/logs"
RUN_DIR="$ROOT/.run"
LOG="$LOG_DIR/cloudflared-named.log"
URL_FILE="$RUN_DIR/tunnel-url.txt"

say() { printf "\033[1;36m→ %s\033[0m\n" "$1"; }
ok()  { printf "\033[1;32m✓ %s\033[0m\n" "$1"; }
err() { printf "\033[1;31m✗ %s\033[0m\n" "$1"; }

command -v cloudflared >/dev/null 2>&1 || { err "brew install cloudflared"; exit 1; }

if [ ! -f "$CONFIG" ]; then
  err "No named tunnel config at $CONFIG"
  echo "Run: ./scripts/setup-named-tunnel.sh api.yourdomain.com"
  exit 1
fi

# Stop quick-tunnel and any previous named tunnel instance.
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
pkill -f 'cloudflared tunnel run' >/dev/null 2>&1 || true
sleep 1

if ! curl -fsS "http://localhost:${PORT}/api/v1/health" >/dev/null 2>&1; then
  say "Backend not on :${PORT} — start with ./scripts/start.sh"
fi

HOSTNAME="$(grep -E '^\s*-\s*hostname:' "$CONFIG" | head -1 | awk '{print $3}')"
PUBLIC_URL="https://${HOSTNAME}"

say "Starting named tunnel → http://localhost:${PORT} ($HOSTNAME) ..."
mkdir -p "$LOG_DIR" "$RUN_DIR"
: > "$LOG"
nohup cloudflared tunnel --no-autoupdate --config "$CONFIG" run > "$LOG" 2>&1 &
echo $! > "$RUN_DIR/cloudflared.pid"

HEALTH_OK=false
for _ in $(seq 1 90); do
  if curl -fsS "${PUBLIC_URL}/api/v1/health" >/dev/null 2>&1; then
    HEALTH_OK=true
    break
  fi
  sleep 2
done

if [ "$HEALTH_OK" != true ]; then
  err "Named tunnel started but health check failed after ~3 min."
  err "URL: $PUBLIC_URL — check $LOG"
  exit 1
fi

printf '%s\n' "$PUBLIC_URL" > "$URL_FILE"
echo ""
ok "Named tunnel is live:"
echo "   Public API:  $PUBLIC_URL"
echo "   Health:      ${PUBLIC_URL}/api/v1/health"
echo "   URL saved:   $URL_FILE"
echo "   Logs:        $LOG"
echo ""
echo "Next: ./scripts/sync-vercel-backend.sh   (one-time; URL is stable after this)"
