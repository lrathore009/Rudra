#!/usr/bin/env bash
set -euo pipefail

echo "╔══════════════════════════════════════╗"
echo "║         RUDRA — Initializing         ║"
echo "╚══════════════════════════════════════╝"

# Copy env if missing
if [ ! -f .env ]; then
  cp .env.example .env
  echo "→ Created .env from template. Configure API keys before production use."
fi

# Start infrastructure
echo "→ Starting PostgreSQL, Qdrant, Redis..."
docker compose up -d postgres qdrant redis

echo "→ Waiting for PostgreSQL..."
until docker compose exec -T postgres pg_isready -U rudra > /dev/null 2>&1; do
  sleep 1
done

# Backend setup
echo "→ Setting up Python backend..."
cd backend
python -m venv .venv 2>/dev/null || true
source .venv/bin/activate
pip install -r requirements.txt -q
alembic upgrade head
cd ..

# Frontend setup
echo "→ Setting up Next.js frontend..."
cd frontend
npm install -q
cd ..

echo ""
echo "╔══════════════════════════════════════╗"
echo "║           RUDRA — Ready              ║"
echo "╠══════════════════════════════════════╣"
echo "║  Backend:  http://localhost:8000     ║"
echo "║  Frontend: http://localhost:3000     ║"
echo "║  API Docs: http://localhost:8000/docs║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Start services:"
echo "  Terminal 1: cd backend && source .venv/bin/activate && uvicorn rudra.main:app --reload"
echo "  Terminal 2: cd frontend && npm run dev"
echo ""
echo "Or: docker compose up"
