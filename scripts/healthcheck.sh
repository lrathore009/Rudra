#!/usr/bin/env bash
# Rudra — health check across all services and endpoints.
set -uo pipefail

API="${NEXT_PUBLIC_API_URL:-http://localhost:8000}"

green() { printf "\033[1;32m%s\033[0m" "$1"; }
red()   { printf "\033[1;31m%s\033[0m" "$1"; }

port_up() { lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1; }

check_port() {
  printf "  %-26s " "$1 (:$2)"
  if port_up "$2"; then echo "$(green UP)"; else echo "$(red DOWN)"; fi
}

echo "── Ports ─────────────────────────────"
check_port "Frontend"  3000
check_port "Backend"   8000
check_port "Postgres"  5432
check_port "Qdrant"    6333
check_port "Redis"     6379
check_port "Ollama"    11434

echo ""
echo "── Backend endpoints ─────────────────"
printf "  %-26s " "GET /api/v1/health"
if curl -fsS "$API/api/v1/health" >/dev/null 2>&1; then echo "$(green OK)"; else echo "$(red FAIL)"; fi

echo ""
echo "── Deep service health ───────────────"
if command -v python3 >/dev/null 2>&1; then
  curl -fsS "$API/api/v1/health/services" 2>/dev/null | python3 -m json.tool 2>/dev/null \
    || echo "  $(red 'backend not reachable')"
else
  curl -fsS "$API/api/v1/health/services" 2>/dev/null || echo "  $(red 'backend not reachable')"
fi
