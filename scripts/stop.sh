#!/usr/bin/env bash
# Rudra — stop backend, frontend, tunnel, and (optionally) infra.
# Usage:
#   ./scripts/stop.sh            stop backend + frontend
#   ./scripts/stop.sh --tunnel   also stop the Cloudflare tunnel
#   ./scripts/stop.sh --infra    also stop Docker containers
#   ./scripts/stop.sh --all      stop everything (backend, frontend, tunnel, infra)
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
RUN_DIR="$ROOT/.run"

say() { printf "\033[1;36m→ %s\033[0m\n" "$1"; }
ok()  { printf "\033[1;32m✓ %s\033[0m\n" "$1"; }

stop_pid() {
  local name="$1" file="$RUN_DIR/$1.pid"
  if [ -f "$file" ]; then
    local pid; pid="$(cat "$file")"
    if kill -0 "$pid" >/dev/null 2>&1; then
      say "Stopping $name (pid $pid)..."
      # Kill the process group so child workers (uvicorn reloader, next) die too.
      kill -- -"$pid" >/dev/null 2>&1 || kill "$pid" >/dev/null 2>&1 || true
      sleep 1
      kill -9 "$pid" >/dev/null 2>&1 || true
    fi
    rm -f "$file"
  fi
}

stop_pid backend
stop_pid frontend

# Tunnel: stop on --tunnel or --all (cloudflared is otherwise left running).
if [ "${1:-}" = "--tunnel" ] || [ "${1:-}" = "--all" ]; then
  stop_pid cloudflared
  rm -f "$RUN_DIR/tunnel-url.txt"
fi

# Fallback: kill anything still bound to our ports.
for port in 8000 3000; do
  pid="$(lsof -nP -tiTCP:$port -sTCP:LISTEN 2>/dev/null || true)"
  [ -n "$pid" ] && { say "Freeing port $port..."; kill -9 $pid >/dev/null 2>&1 || true; }
done

if [ "${1:-}" = "--infra" ] || [ "${1:-}" = "--all" ]; then
  if docker compose version >/dev/null 2>&1; then
    say "Stopping Docker infra..."
    docker compose stop postgres qdrant redis
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose stop postgres qdrant redis
  fi
fi

ok "Rudra stopped."
