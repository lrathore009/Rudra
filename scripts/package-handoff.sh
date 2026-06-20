#!/usr/bin/env bash
# Package Rudra for folder transfer (e.g. to Laxman).
# Excludes venv, node_modules, caches, logs, and runtime artifacts.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

STAMP="$(date +%Y%m%d)"
OUT="${1:-$HOME/Desktop/Rudra-handoff-$STAMP.tgz}"
BASENAME="$(basename "$OUT" .tgz)"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

echo "→ Packaging from: $ROOT"
echo "→ Output: $OUT"

# Copy tree into temp dir with exclusions (portable tar approach)
rsync -a \
  --exclude='backend/.venv' \
  --exclude='frontend/node_modules' \
  --exclude='frontend/.next' \
  --exclude='logs' \
  --exclude='.run' \
  --exclude='.data' \
  --exclude='**/__pycache__' \
  --exclude='backend/.pytest_cache' \
  --exclude='.git' \
  --exclude='backend/*.txt' \
  --exclude='backend/*_brief.txt' \
  --exclude='backend/*_chunk.txt' \
  --exclude='backend/*_chem.txt' \
  --exclude='backend/*_nexus.txt' \
  --exclude='.DS_Store' \
  --exclude='.vercel' \
  "$ROOT/" "$TMPDIR/$BASENAME/"

# Include handoff doc at top of archive
cp "$ROOT/LAXMAN_HANDOFF.md" "$TMPDIR/$BASENAME/START_HERE_LAXMAN.md"

tar -czf "$OUT" -C "$TMPDIR" "$BASENAME"

SIZE="$(du -h "$OUT" | cut -f1)"
echo ""
echo "✓ Created $OUT ($SIZE)"
echo ""
echo "Transfer checklist:"
echo "  1. Send the .tgz (AirDrop, Drive, USB, etc.)"
echo "  2. Send .env separately on a secure channel (NOT inside the archive unless encrypted)"
echo "  3. Recipient: tar -xzf $(basename "$OUT") && read START_HERE_LAXMAN.md"
echo ""
echo "Alternative (preferred): git clone https://github.com/lrathore009/Rudra.git"
