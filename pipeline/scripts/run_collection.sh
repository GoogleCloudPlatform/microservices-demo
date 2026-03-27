#!/usr/bin/env bash
# run_collection.sh — Launch full-scale dataset collection detached from terminal.
#
# This script starts collect_full.py under nohup so it keeps running even
# after Claude Code disconnects, the terminal closes, or your laptop sleeps
# (as long as Docker keeps running).
#
# Usage:
#   bash pipeline/scripts/run_collection.sh
#
# Monitor progress:
#   tail -f pipeline/logs/full_collection.log
#
# Check if it's still running:
#   cat pipeline/logs/full_collection.pid | xargs ps -p
#
# Stop early (progress is saved — can resume):
#   cat pipeline/logs/full_collection.pid | xargs kill

set -e

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_DIR="$REPO_ROOT/pipeline/logs"
LOG_FILE="$LOG_DIR/full_collection.log"
PID_FILE="$LOG_DIR/full_collection.pid"
SCRIPT="$REPO_ROOT/pipeline/scripts/collect_full.py"

mkdir -p "$LOG_DIR"

# ── Guard: don't start a second instance ──────────────────────────────────────
if [ -f "$PID_FILE" ]; then
    EXISTING_PID=$(cat "$PID_FILE")
    if kill -0 "$EXISTING_PID" 2>/dev/null; then
        echo "Collection is already running (PID $EXISTING_PID)."
        echo "To monitor: tail -f $LOG_FILE"
        echo "To stop:    kill $EXISTING_PID"
        exit 1
    else
        echo "Stale PID file found — removing."
        rm -f "$PID_FILE"
    fi
fi

# ── Verify Docker is running ───────────────────────────────────────────────────
if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker is not running. Start Docker Desktop first."
    exit 1
fi

# ── Verify dependencies are installed ─────────────────────────────────────────
if ! python3 -c "import docker, pandas, pyarrow, drain3" 2>/dev/null; then
    echo "Installing pipeline dependencies ..."
    pip3 install -r "$REPO_ROOT/pipeline/requirements.txt" --quiet
fi

echo "========================================================"
echo "  Starting full-scale dataset collection"
echo "  Script  : $SCRIPT"
echo "  Log     : $LOG_FILE"
echo "  PID file: $PID_FILE"
echo "  Duration: ~3.7 hours (42 runs × ~5.5 min each)"
echo "========================================================"
echo ""

# ── Launch detached ───────────────────────────────────────────────────────────
cd "$REPO_ROOT"
nohup python3 -u "$SCRIPT" >> "$LOG_FILE" 2>&1 &
PID=$!

echo $PID > "$PID_FILE"
echo "Collection started in background — PID $PID"
echo ""
echo "Commands:"
echo "  Monitor : tail -f $LOG_FILE"
echo "  Progress: grep 'Run [0-9]' $LOG_FILE | tail -5"
echo "  Running : cat $PID_FILE | xargs ps -p"
echo "  Stop    : cat $PID_FILE | xargs kill"
echo ""
echo "Collection will git push automatically when finished."
