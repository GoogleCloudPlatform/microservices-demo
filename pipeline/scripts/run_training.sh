#!/usr/bin/env bash
# run_training.sh — Launch 5×90-min training dataset collection in the background.
# Survives terminal close, Claude Code disconnects, and sleep (while Docker runs).
#
# Usage:       bash pipeline/scripts/run_training.sh
# Monitor:     tail -f pipeline/logs/training_collection.log
# Progress:    grep -E "Run [0-9]|Cumulative|ACTIVE" pipeline/logs/training_collection.log | tail -10
# Still alive: cat pipeline/logs/training.pid | xargs ps -p
# Stop:        cat pipeline/logs/training.pid | xargs kill   (resumes on next run)

set -e
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_DIR="$REPO_ROOT/pipeline/logs"
LOG_FILE="$LOG_DIR/training_collection.log"
PID_FILE="$LOG_DIR/training.pid"
SCRIPT="$REPO_ROOT/pipeline/scripts/collect_training.py"

mkdir -p "$LOG_DIR"

# Guard against double-start
if [ -f "$PID_FILE" ]; then
    EXISTING=$(cat "$PID_FILE")
    if kill -0 "$EXISTING" 2>/dev/null; then
        echo "Already running (PID $EXISTING)."
        echo "Monitor: tail -f $LOG_FILE"
        exit 1
    fi
    rm -f "$PID_FILE"
fi

if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker is not running."
    exit 1
fi

echo "============================================================"
echo "  Training Dataset Collection"
echo "  5 runs × 90 minutes = ~7.5 hours"
echo "  Log : $LOG_FILE"
echo "============================================================"

cd "$REPO_ROOT"
nohup python3 -u "$SCRIPT" >> "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"

echo ""
echo "Started — PID $PID"
echo ""
echo "Commands:"
echo "  Live log : tail -f $LOG_FILE"
echo "  Progress : grep -E 'Run [0-9]|Cumulative' $LOG_FILE | tail -8"
echo "  Running  : cat $PID_FILE | xargs ps -p"
echo "  Stop     : cat $PID_FILE | xargs kill"
echo ""
echo "Will auto git-push when all 5 runs complete."
