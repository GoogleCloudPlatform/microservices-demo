#!/usr/bin/env bash
# start_platform.sh — Local development launcher
# Starts: FastAPI backend (port 8001) + React dashboard dev server (port 5173)
#
# Usage:   bash infra/start_platform.sh
# Stop:    bash infra/stop_platform.sh
# Logs:    tail -f pipeline/logs/api.log
#          tail -f pipeline/logs/dashboard.log

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$REPO_ROOT/pipeline/logs"
mkdir -p "$LOG_DIR"

API_PID_FILE="$LOG_DIR/api.pid"
DASH_PID_FILE="$LOG_DIR/dashboard.pid"

echo "============================================================"
echo "  AEGIS local development mode"
echo "============================================================"

# ── Guard: API already running ────────────────────────────────
if [ -f "$API_PID_FILE" ]; then
    EXISTING=$(cat "$API_PID_FILE")
    if kill -0 "$EXISTING" 2>/dev/null; then
        echo "API already running (PID $EXISTING)"
    else
        rm -f "$API_PID_FILE"
    fi
fi

# ── 1. Install backend deps ───────────────────────────────────
echo ""
echo "[1/3] Installing backend dependencies..."
pip3 install -r "$REPO_ROOT/backend/requirements.txt" --quiet

# ── 2. Start FastAPI ──────────────────────────────────────────
echo "[2/3] Starting FastAPI backend in development mode on port 8001..."
cd "$REPO_ROOT"
nohup python3 -m uvicorn backend.anomaly_api.main:app \
    --host 0.0.0.0 \
    --port 8001 \
    --reload \
    >> "$LOG_DIR/api.log" 2>&1 &
API_PID=$!
echo $API_PID > "$API_PID_FILE"
echo "      Backend PID: $API_PID"

# Wait for API to be ready
echo "      Waiting for API..."
for i in $(seq 1 15); do
    if curl -s http://localhost:8001/health >/dev/null 2>&1; then
        echo "      API is ready!"
        break
    fi
    sleep 1
done

# ── 3. Start React dashboard ──────────────────────────────────
echo "[3/3] Starting React dashboard dev server on port 5173..."
cd "$REPO_ROOT/dashboard"
if [ ! -d node_modules ]; then
    echo "      Installing npm packages..."
    npm install --silent
fi
nohup npm run dev >> "$LOG_DIR/dashboard.log" 2>&1 &
DASH_PID=$!
echo $DASH_PID > "$DASH_PID_FILE"
echo "      Dashboard PID: $DASH_PID"

# ── Summary ───────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "  Platform started!"
echo ""
echo "  API:        http://localhost:8001"
echo "  API docs:   http://localhost:8001/docs"
echo "  Dashboard:  http://localhost:5173"
echo ""
echo "  Logs:"
echo "    tail -f $LOG_DIR/api.log"
echo "    tail -f $LOG_DIR/dashboard.log"
echo ""
echo "  Stop:"
echo "    bash $REPO_ROOT/infra/stop_platform.sh"
echo "============================================================"
