#!/usr/bin/env bash
# Rudra — one-command local startup.
# Starts infra (Postgres/Qdrant/Redis via Docker), runs migrations, then boots
# the FastAPI backend and Next.js frontend as background processes.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RUN_DIR="$ROOT/.run"
LOG_DIR="$ROOT/logs"
mkdir -p "$RUN_DIR" "$LOG_DIR"

say() { printf "\033[1;36m→ %s\033[0m\n" "$1"; }
ok()  { printf "\033[1;32m✓ %s\033[0m\n" "$1"; }
warn(){ printf "\033[1;33m! %s\033[0m\n" "$1"; }

# --- 0. Pick docker compose command -----------------------------------------
if docker compose version >/dev/null 2>&1; then
  DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  DC="docker-compose"
else
  DC=""
  warn "Docker Compose not found — skipping container infra (assuming local services)."
fi

# --- 1. Ensure .env -----------------------------------------------------------
if [ ! -f .env ]; then
  cp .env.example .env
  say "Created .env from template."
fi

# --- 2. Infrastructure --------------------------------------------------------
if [ -n "$DC" ]; then
  say "Starting PostgreSQL, Qdrant, Redis..."
  $DC up -d postgres qdrant redis
  say "Waiting for PostgreSQL..."
  for _ in $(seq 1 30); do
    if $DC exec -T postgres pg_isready -U "${POSTGRES_USER:-rudra}" >/dev/null 2>&1; then
      ok "PostgreSQL ready."; break
    fi
    sleep 1
  done
fi

# --- 3. Backend ---------------------------------------------------------------
cd "$ROOT/backend"
if [ ! -d .venv ]; then
  say "Creating Python virtualenv..."
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
say "Installing backend dependencies..."
pip install -r requirements.txt -q
say "Running database migrations..."
alembic upgrade head || warn "Migrations failed (is Postgres up?)."

say "Starting backend (uvicorn) on :8000..."
nohup uvicorn rudra.main:app --host 0.0.0.0 --port 8000 --reload \
  > "$LOG_DIR/backend.log" 2>&1 &
echo $! > "$RUN_DIR/backend.pid"
deactivate || true

# --- 4. Frontend --------------------------------------------------------------
cd "$ROOT/frontend"
if [ ! -d node_modules ]; then
  say "Installing frontend dependencies..."
  npm install --silent
fi
say "Starting frontend (next dev) on :3000..."
nohup npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
echo $! > "$RUN_DIR/frontend.pid"

cd "$ROOT"
echo ""
ok "Rudra is starting up."
echo "   Backend:  http://localhost:8000  (docs: /docs)"
echo "   Frontend: http://localhost:3000"
echo "   Logs:     logs/backend.log, logs/frontend.log"
echo "   Health:   ./scripts/healthcheck.sh"
echo "   Stop:     ./scripts/stop.sh"
