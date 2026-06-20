#!/usr/bin/env bash
# #15 — Rudra doctor: health check for Jarvis stack
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Rudra Doctor ==="

check() {
  if eval "$2" >/dev/null 2>&1; then
    echo "  OK  $1"
  else
    echo "  FAIL $1"
  fi
}

check "Docker" "docker info"
check "Postgres" "docker compose ps postgres 2>/dev/null | grep -q Up || pg_isready -h localhost -p 5432"
check "Redis" "docker compose ps redis 2>/dev/null | grep -q Up || redis-cli ping"
check "Ollama" "curl -sf http://localhost:11434/api/tags"
check "Backend" "curl -sf http://localhost:8000/api/v1/health"
check "Frontend" "curl -sf http://localhost:3000 >/dev/null"

if [ -f backend/.venv/bin/activate ]; then
  source backend/.venv/bin/activate
  check "Alembic head" "cd backend && alembic current 2>/dev/null | grep -q 008"
  check "Pytest import" "python -c 'import rudra.jarvis'"
fi

echo ""
echo "Jarvis layer endpoints (auth may be required):"
echo "  POST /api/v1/jarvis/digest/spoken"
echo "  GET  /api/v1/jarvis/connectors"
echo "  POST /api/chat/completions  (OpenAI-compatible)"
echo ""
echo "Done."
