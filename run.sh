#!/usr/bin/env bash
#
# run.sh — launch the full PenguWave stack (FastAPI backend + React/Vite frontend).
#
# Usage:
#   ./run.sh            # start backend (:3001) and frontend (:5173)
#   ./run.sh --no-seed  # skip the database seed step
#
# Stops both processes cleanly on Ctrl-C.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
BACKEND_PORT=3001
FRONTEND_PORT=5173

SEED=1
[[ "${1:-}" == "--no-seed" ]] && SEED=0

log() { printf '\033[1;36m[run]\033[0m %s\n' "$*"; }
err() { printf '\033[1;31m[run]\033[0m %s\n' "$*" >&2; }

# --- Preflight ---------------------------------------------------------------
if [[ ! -f "$BACKEND/.env" ]]; then
  err "backend/.env is missing. Copy backend/.env.example to backend/.env and fill it in."
  exit 1
fi

if [[ ! -x "$BACKEND/.venv/bin/python" ]]; then
  log "Creating backend virtualenv..."
  python3 -m venv "$BACKEND/.venv"
  "$BACKEND/.venv/bin/pip" install -q -r "$BACKEND/requirements.txt" -r "$BACKEND/requirements-dev.txt"
fi
PY="$BACKEND/.venv/bin/python"

if [[ ! -d "$FRONTEND/node_modules" ]]; then
  log "Installing frontend dependencies..."
  (cd "$FRONTEND" && npm install)
fi

# Fail clearly if a port is already taken (otherwise a server dies silently).
check_port() {
  local port="$1" name="$2"
  if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    err "Port $port ($name) is already in use — is the project already running?"
    err "Free it first, e.g.:  lsof -ti tcp:$port | xargs kill"
    exit 1
  fi
}
check_port "$BACKEND_PORT" backend
check_port "$FRONTEND_PORT" frontend

# --- Cleanup on exit ---------------------------------------------------------
PIDS=()
cleanup() {
  log "Shutting down..."
  for pid in "${PIDS[@]:-}"; do
    [[ -n "$pid" ]] && kill "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# --- Seed the database -------------------------------------------------------
if [[ "$SEED" -eq 1 ]]; then
  log "Seeding database (use --no-seed to skip)..."
  (cd "$BACKEND" && "$PY" -m app.seed) || {
    err "Seed failed. Is PostgreSQL running and DATABASE_URL correct?"
    exit 1
  }
fi

# --- Start backend -----------------------------------------------------------
log "Starting backend on http://localhost:$BACKEND_PORT ..."
(cd "$BACKEND" && exec "$PY" -m uvicorn app.main:app --reload --port "$BACKEND_PORT") &
PIDS+=("$!")

# --- Start frontend ----------------------------------------------------------
log "Starting frontend on http://localhost:$FRONTEND_PORT ..."
(cd "$FRONTEND" && exec npm run dev -- --port "$FRONTEND_PORT") &
PIDS+=("$!")

log "Both services starting. Press Ctrl-C to stop."
log "  Backend:  http://localhost:$BACKEND_PORT  (health: /health)"
log "  Frontend: http://localhost:$FRONTEND_PORT"

# Wait for either process to exit; cleanup trap stops the other.
# (Portable to Bash 3.2, which ships on macOS and lacks `wait -n`.)
while true; do
  for pid in "${PIDS[@]}"; do
    kill -0 "$pid" 2>/dev/null || exit 0
  done
  sleep 1
done
