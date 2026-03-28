#!/usr/bin/env bash
# start_platform.sh — Local platform launcher
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
echo "  AEGIS local platform mode"
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
echo "[2/3] Starting FastAPI backend on port 8001..."
cd "$REPO_ROOT"
nohup sh -c "cd '$REPO_ROOT' && exec python3 -m uvicorn backend.anomaly_api.main:app --host 0.0.0.0 --port 8001" \
    >> "$LOG_DIR/api.log" 2>&1 &
BOOT_API_PID=$!
echo "      Backend bootstrap PID: $BOOT_API_PID"

# Wait for API to be ready
echo "      Waiting for API..."
for i in $(seq 1 30); do
    if curl -s http://localhost:8001/health >/dev/null 2>&1; then
        API_PID=$(lsof -t -iTCP:8001 -sTCP:LISTEN | head -n 1)
        if [ -n "$API_PID" ]; then
            echo "$API_PID" > "$API_PID_FILE"
            echo "      Backend PID: $API_PID"
        fi
        echo "      API is ready!"
        break
    fi
    sleep 1
done

if ! curl -s http://localhost:8001/health >/dev/null 2>&1; then
    echo "      API failed to start. Check: tail -f $LOG_DIR/api.log"
    exit 1
fi

# ── 3. Start React dashboard ──────────────────────────────────
echo "[3/3] Starting React dashboard dev server on port 5173..."
cd "$REPO_ROOT/dashboard"
if [ ! -d node_modules ]; then
    echo "      Installing npm packages..."
    npm install --silent
fi
nohup sh -c "cd '$REPO_ROOT/dashboard' && exec npm run dev -- --host 0.0.0.0 --port 5173" >> "$LOG_DIR/dashboard.log" 2>&1 &
BOOT_DASH_PID=$!
echo "      Dashboard bootstrap PID: $BOOT_DASH_PID"

echo "      Waiting for dashboard..."
for i in $(seq 1 30); do
    if curl -s http://localhost:5173 >/dev/null 2>&1; then
        DASH_PID=$(lsof -t -iTCP:5173 -sTCP:LISTEN | head -n 1)
        if [ -n "$DASH_PID" ]; then
            echo "$DASH_PID" > "$DASH_PID_FILE"
            echo "      Dashboard PID: $DASH_PID"
        fi
        echo "      Dashboard is ready!"
        break
    fi
    sleep 1
done

if ! curl -s http://localhost:5173 >/dev/null 2>&1; then
    echo "      Dashboard failed to start. Check: tail -f $LOG_DIR/dashboard.log"
    exit 1
fi

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
