#!/usr/bin/env bash
# stop_platform.sh — Stop the AI Observability Platform

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$REPO_ROOT/pipeline/logs"

echo "Stopping AI Observability Platform..."

for PID_FILE in "$LOG_DIR/api.pid" "$LOG_DIR/dashboard.pid"; do
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            echo "  Stopped PID $PID ($(basename $PID_FILE .pid))"
        fi
        rm -f "$PID_FILE"
    fi
done

echo "Done."
