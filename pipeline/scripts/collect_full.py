#!/usr/bin/env python3
"""
collect_full.py — Full-scale dataset generation for LSTM + Isolation Forest training.

Runs 42 collection episodes (~3.7 hours total) rotating through all three failure
types and two injection targets, accumulating data across runs into four Parquet tables.

Key properties:
  - Checkpoint file saves progress after every run — fully resumable if interrupted
  - Parquet files are written incrementally (never lose more than one run's data)
  - Three failure types: memory_leak, cpu_starvation, network_latency
  - Two injection targets: recommendationservice, emailservice (both have python3)
  - Pure-normal runs interspersed for Isolation Forest baseline
  - Final commit + git push when all runs complete

Run (detached, survives terminal close):
  bash pipeline/scripts/run_collection.sh

Check progress:
  tail -f pipeline/logs/full_collection.log

Merge with a second batch later:
  python3 pipeline/scripts/merge_datasets.py \\
      pipeline/data/processed/full_metrics.parquet \\
      pipeline/data/processed/batch2_metrics.parquet \\
      pipeline/data/processed/merged_metrics.parquet
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

import docker
import pandas as pd
import numpy as np
import requests
from tqdm import tqdm

# ── Path setup ────────────────────────────────────────────────────────────────
REPO_ROOT    = Path(__file__).resolve().parent.parent.parent
PIPELINE_DIR = REPO_ROOT / "pipeline"
sys.path.insert(0, str(PIPELINE_DIR / "scripts"))

from collect_demo import (
    MetricsPoller, LogStreamer, JaegerPoller, Drain3Parser,
    LogAggregator, FailureInjector, DatasetBuilder,
    ALL_MONITORED, POLL_INTERVAL_S,
    LOKI_URL, JAEGER_URL,
    NORMAL_PHASE_S, PRE_FAIL_PHASE_S, ACTIVE_FAIL_S, RECOVERY_S,
    utcnow, iso, floor15,
)
from label_engine import FailureEventRegistry, validate_labels

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_DIR = PIPELINE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "full_collection.log", mode="a"),
    ],
)
log = logging.getLogger("collect_full")

# ── Output paths ──────────────────────────────────────────────────────────────
OUTPUT_DIR       = PIPELINE_DIR / "data" / "processed"
CHECKPOINT_FILE  = OUTPUT_DIR / "full_collection_checkpoint.json"
SUMMARY_FILE     = OUTPUT_DIR / "full_collection_summary.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Run schedule ──────────────────────────────────────────────────────────────
# 42 runs total:
#   - 6 pure-normal runs (no injection) — baseline for Isolation Forest
#   - 12 memory_leak     × 2 targets = 12 runs
#   - 12 cpu_starvation  × 2 targets = 12 runs
#   - 12 network_latency × 2 targets = 12 runs
#
# Layout: interleave normal runs every 7th episode to ensure IF baseline
# is distributed throughout the collection window (catches time-of-day variance).
#
# Each entry: (failure_type_or_None, target_service_or_None)
INJECT_TARGETS = ["recommendationservice", "emailservice"]

_injection_runs: List[tuple] = []
for ft in ["memory_leak", "cpu_starvation", "network_latency"]:
    for i in range(12):
        _injection_runs.append((ft, INJECT_TARGETS[i % 2]))

# Interleave 6 pure-normal runs at positions 0, 7, 14, 21, 28, 35
RUN_SCHEDULE: List[tuple] = []
normal_slots = {0, 7, 14, 21, 28, 35}
inj_iter = iter(_injection_runs)
for i in range(42):
    if i in normal_slots:
        RUN_SCHEDULE.append((None, None))
    else:
        RUN_SCHEDULE.append(next(inj_iter))

assert len(RUN_SCHEDULE) == 42, f"Schedule length {len(RUN_SCHEDULE)} != 42"

TOTAL_RUNS = len(RUN_SCHEDULE)
RECOVERY_PAUSE_S = 20   # seconds to wait after restart before next run

# ── Jaeger services to poll ───────────────────────────────────────────────────
JAEGER_SERVICES = [
    "frontend", "checkoutservice", "cartservice",
    "productcatalogservice", "currencyservice",
    "recommendationservice", "paymentservice", "emailservice",
]


# ── Checkpoint helpers ─────────────────────────────────────────────────────────

def load_checkpoint() -> Dict:
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"completed_runs": 0, "run_results": []}


def save_checkpoint(cp: Dict) -> None:
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(cp, f, indent=2, default=str)


# ── Parquet merge helpers ──────────────────────────────────────────────────────

def append_to_parquet(new_df: pd.DataFrame, path: Path) -> int:
    """Append new_df to an existing parquet file (or create it). Returns total rows."""
    if new_df.empty:
        return int(pd.read_parquet(path).shape[0]) if path.exists() else 0

    if path.exists():
        existing = pd.read_parquet(path)
        combined = pd.concat([existing, new_df], ignore_index=True)
    else:
        combined = new_df

    combined.to_parquet(path, index=False, engine="pyarrow")
    return len(combined)


def read_parquet_safe(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path) if path.exists() else pd.DataFrame()


# ── Single-episode collection ──────────────────────────────────────────────────

def run_episode(
    run_idx: int,
    failure_type: Optional[str],
    target_service: Optional[str],
    docker_client: docker.DockerClient,
    drain_parser: Drain3Parser,
) -> Dict:
    """
    Run one 6-minute collection episode.

    Returns a dict with row counts and label stats for the checkpoint.
    """
    label = f"Run {run_idx+1}/{TOTAL_RUNS}"
    if failure_type:
        label += f" [{failure_type} → {target_service}]"
    else:
        label += " [NORMAL BASELINE]"

    log.info("=" * 60)
    log.info("  %s", label)
    log.info("=" * 60)

    registry  = FailureEventRegistry()
    metrics_p = MetricsPoller(docker_client)
    log_s     = LogStreamer(drain_parser)
    jaeger_p  = JaegerPoller()

    # Inject into the specified target (or None for normal)
    injector = FailureInjector(
        docker_client=docker_client,
        registry=registry,
        target_service=target_service or "recommendationservice",
    ) if failure_type else None

    collection_start = utcnow()
    log_fetch_start  = collection_start

    phase_normal_end = collection_start + timedelta(seconds=NORMAL_PHASE_S)
    phase_pre_end    = phase_normal_end  + timedelta(seconds=PRE_FAIL_PHASE_S)
    phase_active_end = phase_pre_end     + timedelta(seconds=ACTIVE_FAIL_S)
    phase_total_end  = phase_active_end  + timedelta(seconds=RECOVERY_S)

    stage1_done = stage2_done = stage3_done = stage4_done = recovery_done = False
    tick = 0

    while True:
        now     = utcnow()
        elapsed = (now - collection_start).total_seconds()

        if now >= phase_total_end:
            break

        # ── Injection schedule (only when failure_type is set) ──────────────
        if injector and failure_type:
            if elapsed >= NORMAL_PHASE_S and not stage1_done:
                injector.stage1_ramp()
                stage1_done = True

            pre_start = NORMAL_PHASE_S + PRE_FAIL_PHASE_S * 0.3
            if elapsed >= pre_start and not stage2_done:
                injector.stage2_pre_failure()
                stage2_done = True

            if elapsed >= (NORMAL_PHASE_S + PRE_FAIL_PHASE_S) and not stage3_done:
                injector.stage3_active_failure(failure_type)
                stage3_done = True

            active_mid = NORMAL_PHASE_S + PRE_FAIL_PHASE_S + ACTIVE_FAIL_S * 0.4
            if elapsed >= active_mid and not stage4_done:
                injector.stage4_peak(failure_type)
                stage4_done = True

            if elapsed >= (NORMAL_PHASE_S + PRE_FAIL_PHASE_S + ACTIVE_FAIL_S) \
                    and not recovery_done:
                injector.recover()
                recovery_done = True
                time.sleep(5)

        # ── Metrics poll ─────────────────────────────────────────────────────
        metrics_p.poll_once(utcnow())

        # ── Log fetch ─────────────────────────────────────────────────────────
        fetch_end = utcnow()
        log_s.fetch_range(log_fetch_start, fetch_end, limit=500)
        log_fetch_start = fetch_end

        tick += 1
        elapsed_tick = (utcnow() - now).total_seconds()
        time.sleep(max(0, POLL_INTERVAL_S - elapsed_tick))

    # ── Jaeger traces for this episode ────────────────────────────────────────
    for svc in JAEGER_SERVICES:
        jaeger_p.fetch_service_traces(svc, collection_start, utcnow(), limit=300)

    # ── Build DataFrames ──────────────────────────────────────────────────────
    metrics_df = metrics_p.build_dataframe()
    logs_df    = log_s.build_dataframe()
    traces_df  = jaeger_p.build_dataframe()

    # ── Stamp labels ──────────────────────────────────────────────────────────
    if not metrics_df.empty:
        metrics_df = registry.compute_labels_for_dataframe(metrics_df)
    if not logs_df.empty:
        logs_df = registry.compute_labels_for_dataframe(
            logs_df, ts_col="log_timestamp", svc_col="service_name")
    if not traces_df.empty:
        traces_df = registry.compute_labels_for_dataframe(
            traces_df, ts_col="start_time", svc_col="service_name")

    # ── Log aggregates ─────────────────────────────────────────────────────────
    log_agg_df = pd.DataFrame()
    if not logs_df.empty:
        log_agg_df = LogAggregator().build(logs_df)

    # ── Append to running parquet files ───────────────────────────────────────
    tables = {
        "full_metrics":        metrics_df,
        "full_logs":           logs_df,
        "full_traces":         traces_df,
        "full_log_aggregates": log_agg_df,
    }
    row_totals = {}
    for name, df in tables.items():
        path = OUTPUT_DIR / f"{name}.parquet"
        row_totals[name] = append_to_parquet(df, path)

    # ── Validation ────────────────────────────────────────────────────────────
    val_stats = {}
    for name, df in [("metrics", metrics_df), ("logs", logs_df)]:
        if not df.empty:
            r = validate_labels(df, strict=False)
            val_stats[name] = r["stats"]

    result = {
        "run_idx":        run_idx,
        "failure_type":   failure_type or "none",
        "target_service": target_service or "none",
        "start_time":     iso(collection_start),
        "end_time":       iso(utcnow()),
        "rows_this_run": {
            "metrics":        len(metrics_df),
            "logs":           len(logs_df),
            "traces":         len(traces_df),
            "log_aggregates": len(log_agg_df),
        },
        "cumulative_rows": row_totals,
        "label_stats":    val_stats,
        "failure_events": registry.get_summary()["events"],
    }

    if val_stats.get("metrics"):
        s = val_stats["metrics"]
        log.info("  ✓ metrics  %d rows | failure=%d | pre_failure=%d | future=%d | normal=%d",
                 s["total_rows"], s["failure_rows"], s["pre_failure_rows"],
                 s["future_failure_rows"], s["normal_rows"])

    log.info("  Cumulative: metrics=%d logs=%d traces=%d log_agg=%d",
             row_totals.get("full_metrics", 0),
             row_totals.get("full_logs", 0),
             row_totals.get("full_traces", 0),
             row_totals.get("full_log_aggregates", 0))

    return result


# ── Final actions ──────────────────────────────────────────────────────────────

def write_final_summary(checkpoint: Dict) -> None:
    """Write human-readable summary JSON."""
    runs = checkpoint["run_results"]

    # Aggregate label stats across all runs
    total_failure = total_pre = total_ff = total_normal = 0
    for r in runs:
        s = r.get("label_stats", {}).get("metrics", {})
        total_failure += s.get("failure_rows", 0)
        total_pre     += s.get("pre_failure_rows", 0)
        total_ff      += s.get("future_failure_rows", 0)
        total_normal  += s.get("normal_rows", 0)

    last = runs[-1] if runs else {}
    summary = {
        "generated_at":   iso(utcnow()),
        "total_runs":     len(runs),
        "cumulative_rows": last.get("cumulative_rows", {}),
        "failure_type_distribution": {
            ft: sum(1 for r in runs if r["failure_type"] == ft)
            for ft in ["memory_leak", "cpu_starvation", "network_latency", "none"]
        },
        "target_service_distribution": {
            svc: sum(1 for r in runs if r["target_service"] == svc)
            for svc in ["recommendationservice", "emailservice", "none"]
        },
        "label_totals": {
            "failure_rows":      total_failure,
            "pre_failure_rows":  total_pre,
            "future_failure_rows": total_ff,
            "normal_rows":       total_normal,
        },
        "run_log": [
            {k: v for k, v in r.items() if k != "label_stats"}
            for r in runs
        ],
    }

    with open(SUMMARY_FILE, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    log.info("Summary written → %s", SUMMARY_FILE)


def generate_csvs() -> None:
    """Write CSV versions of all parquet files (except traces — too large)."""
    for name in ["full_metrics", "full_logs", "full_log_aggregates"]:
        pq = OUTPUT_DIR / f"{name}.parquet"
        if pq.exists():
            df = pd.read_parquet(pq)
            df.to_csv(OUTPUT_DIR / f"{name}.csv", index=False)
            log.info("  CSV written: %s.csv (%d rows)", name, len(df))


def git_push_results() -> None:
    """Stage all output files, commit with stats, and push to origin/main."""
    log.info("Preparing git commit ...")

    # Load summary for commit message stats
    summary = {}
    if SUMMARY_FILE.exists():
        with open(SUMMARY_FILE) as f:
            summary = json.load(f)

    cr = summary.get("cumulative_rows", {})
    lt = summary.get("label_totals", {})

    files_to_add = [
        "pipeline/data/processed/full_metrics.parquet",
        "pipeline/data/processed/full_metrics.csv",
        "pipeline/data/processed/full_logs.parquet",
        "pipeline/data/processed/full_logs.csv",
        "pipeline/data/processed/full_traces.parquet",
        "pipeline/data/processed/full_log_aggregates.parquet",
        "pipeline/data/processed/full_log_aggregates.csv",
        "pipeline/data/processed/full_collection_summary.json",
        "pipeline/data/processed/full_collection_checkpoint.json",
        "pipeline/scripts/collect_full.py",
        "pipeline/scripts/collect_demo.py",
        "pipeline/scripts/run_collection.sh",
    ]

    # Only add files that actually exist
    existing = [f for f in files_to_add if (REPO_ROOT / f).exists()]

    if not existing:
        log.warning("No files to commit.")
        return

    subprocess.run(["git", "add", "-f"] + existing, cwd=REPO_ROOT, check=True)

    commit_msg = (
        f"data: full-scale training dataset ({summary.get('total_runs', '?')} collection runs)\n\n"
        f"Tables:\n"
        f"  full_metrics:        {cr.get('full_metrics', '?'):>7} rows\n"
        f"  full_logs:           {cr.get('full_logs', '?'):>7} rows\n"
        f"  full_traces:         {cr.get('full_traces', '?'):>7} rows\n"
        f"  full_log_aggregates: {cr.get('full_log_aggregates', '?'):>7} rows\n\n"
        f"Label breakdown (metrics):\n"
        f"  failure rows:      {lt.get('failure_rows', '?')}\n"
        f"  pre_failure rows:  {lt.get('pre_failure_rows', '?')}\n"
        f"  future_failure:    {lt.get('future_failure_rows', '?')}\n"
        f"  normal rows:       {lt.get('normal_rows', '?')}\n\n"
        f"Failure types: memory_leak / cpu_starvation / network_latency\n"
        f"Injection targets: recommendationservice, emailservice\n\n"
        f"Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
    )

    result = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=REPO_ROOT, capture_output=True, text=True
    )
    if result.returncode != 0:
        log.error("git commit failed: %s", result.stderr)
        return
    log.info("git commit OK")

    result = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=REPO_ROOT, capture_output=True, text=True
    )
    if result.returncode != 0:
        log.error("git push failed: %s", result.stderr)
    else:
        log.info("git push OK → origin/main")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    log.info("=" * 65)
    log.info("  Full-Scale Dataset Collection — %d runs (~%.1f hours)",
             TOTAL_RUNS, TOTAL_RUNS * 5.5 / 60)
    log.info("  Output → %s", OUTPUT_DIR)
    log.info("=" * 65)

    # ── Connect to Docker ─────────────────────────────────────────────────────
    try:
        docker_client = docker.from_env()
        docker_client.ping()
        log.info("Docker OK")
    except Exception as e:
        log.error("Docker connection failed: %s", e)
        sys.exit(1)

    # ── Load checkpoint (resume support) ─────────────────────────────────────
    checkpoint = load_checkpoint()
    completed  = checkpoint["completed_runs"]

    if completed > 0:
        log.info("Resuming from run %d / %d (checkpoint found)", completed + 1, TOTAL_RUNS)
    else:
        log.info("Starting fresh collection")

    # ── Shared Drain3 parser (persists templates across all runs) ─────────────
    drain_parser = Drain3Parser()

    # ── Run loop ──────────────────────────────────────────────────────────────
    for run_idx in range(completed, TOTAL_RUNS):
        failure_type, target_service = RUN_SCHEDULE[run_idx]

        try:
            result = run_episode(
                run_idx=run_idx,
                failure_type=failure_type,
                target_service=target_service,
                docker_client=docker_client,
                drain_parser=drain_parser,
            )
        except KeyboardInterrupt:
            log.warning("Interrupted at run %d — progress saved.", run_idx)
            break
        except Exception as e:
            log.error("Run %d failed with exception: %s", run_idx, e, exc_info=True)
            result = {
                "run_idx": run_idx,
                "failure_type": failure_type or "none",
                "target_service": target_service or "none",
                "error": str(e),
                "rows_this_run": {},
                "cumulative_rows": {},
                "label_stats": {},
                "failure_events": [],
            }

        # Save checkpoint after every run regardless of success/failure
        checkpoint["completed_runs"] = run_idx + 1
        checkpoint["run_results"].append(result)
        save_checkpoint(checkpoint)

        # Brief pause between runs so the restarted container stabilises
        if run_idx < TOTAL_RUNS - 1:
            log.info("Pausing %ds before next run ...", RECOVERY_PAUSE_S)
            time.sleep(RECOVERY_PAUSE_S)

    # ── All runs done ─────────────────────────────────────────────────────────
    log.info("")
    log.info("=" * 65)
    log.info("  All %d runs complete!", checkpoint["completed_runs"])
    log.info("=" * 65)

    write_final_summary(checkpoint)
    generate_csvs()
    git_push_results()

    log.info("Done. Dataset is live on GitHub.")


if __name__ == "__main__":
    main()
