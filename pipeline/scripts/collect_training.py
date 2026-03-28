#!/usr/bin/env python3
"""
collect_training.py — Full-scale LSTM/IF training dataset collection.

5 runs × 90 minutes = 7.5 hours of continuous, properly-shaped time-series data.

Key improvements over collect_full.py:
  1. CONTINUOUS runs (not episodic) — LSTM windows work within each 90-min run
  2. 4 injection events per run — more positive sequences per run
  3. Varied intensity (mild/medium/heavy) per event — model learns shape, not magnitude
  4. Drain3 inner-message extraction — JSON logs parsed correctly, real templates emerge
  5. Global timestamp trace labeling — traces correctly labeled during failure windows
  6. Extended pre-failure buffer (180s = 12 steps) — richer warning signal for LSTM
  7. Parallel Docker stats polling — faster ticks, more metric rows per run
  8. Output → pipeline/data/training/ (separate from demo processed data)
  9. Checkpoint/resume — safe to kill and restart, picks up from last completed run
  10. Auto git-push when all 5 runs complete

Run (detached, survives Claude Code disconnect):
  bash pipeline/scripts/run_training.sh

Monitor:
  tail -f pipeline/logs/training_collection.log
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import docker
import pandas as pd
import numpy as np
import requests

# ── Path setup ────────────────────────────────────────────────────────────────
REPO_ROOT    = Path(__file__).resolve().parent.parent.parent
PIPELINE_DIR = REPO_ROOT / "pipeline"
sys.path.insert(0, str(PIPELINE_DIR / "scripts"))

from collect_demo import (
    JaegerPoller, Drain3Parser, LogAggregator,
    ALL_MONITORED, LOKI_URL, JAEGER_URL,
    utcnow, iso,
)
from label_engine import (
    FailureEventRegistry, validate_labels,
    BUFFER_SECONDS as DEFAULT_BUFFER,
)

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_DIR = PIPELINE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "training_collection.log", mode="a"),
    ],
)
log = logging.getLogger("collect_training")

# ── Output ────────────────────────────────────────────────────────────────────
TRAINING_DIR = PIPELINE_DIR / "data" / "training"
TRAINING_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_FILE = TRAINING_DIR / "checkpoint.json"
SUMMARY_FILE    = TRAINING_DIR / "collection_summary.json"

# ── Timing constants (all wall-clock seconds) ─────────────────────────────────
POLL_INTERVAL_S     = 15    # metric sampling cadence
PRE_FAIL_BUFFER_S   = 180   # 12 × 15s — extended pre-failure window for LSTM
EVENT_PRE_FAIL_S    = 180   # 3 min pre-failure ramp per event
EVENT_ACTIVE_S      = 300   # 5 min active failure per event
EVENT_RECOVERY_S    = 420   # 7 min recovery (restart + stabilise) per event
EVENT_TOTAL_S       = EVENT_PRE_FAIL_S + EVENT_ACTIVE_S + EVENT_RECOVERY_S  # 900s = 15 min
NORMAL_BASELINE_S   = 720   # 12 min pure baseline before first injection
FINAL_TAIL_S        = 1080  # 18 min normal tail after last injection
EVENTS_PER_RUN      = 4
TOTAL_RUN_S         = NORMAL_BASELINE_S + EVENTS_PER_RUN * EVENT_TOTAL_S + FINAL_TAIL_S
# = 720 + 4×900 + 1080 = 5400s = 90 min ✓

LOKI_LIMIT_PER_TICK = 100   # small per-tick limit keeps fetches fast

JAEGER_SERVICES = [
    "frontend", "checkoutservice", "cartservice",
    "productcatalogservice", "currencyservice",
    "recommendationservice", "paymentservice", "emailservice",
]

# ── 5-run training schedule ────────────────────────────────────────────────────
# Each run: (target_service, [(failure_type, intensity), ...] × 4 events)
# Intensities: "mild" | "medium" | "heavy"
# Alternates targets so both services appear across runs

TRAINING_SCHEDULE = [
    {
        "target_service": "recommendationservice",
        "events": [
            ("memory_leak",     "mild"),
            ("cpu_starvation",  "heavy"),
            ("network_latency", "medium"),
            ("memory_leak",     "heavy"),
        ],
    },
    {
        "target_service": "emailservice",
        "events": [
            ("cpu_starvation",  "mild"),
            ("network_latency", "heavy"),
            ("memory_leak",     "medium"),
            ("cpu_starvation",  "heavy"),
        ],
    },
    {
        "target_service": "recommendationservice",
        "events": [
            ("network_latency", "mild"),
            ("memory_leak",     "heavy"),
            ("cpu_starvation",  "medium"),
            ("network_latency", "heavy"),
        ],
    },
    {
        "target_service": "emailservice",
        "events": [
            ("memory_leak",     "medium"),
            ("cpu_starvation",  "mild"),
            ("network_latency", "heavy"),
            ("memory_leak",     "heavy"),
        ],
    },
    {
        "target_service": "recommendationservice",
        "events": [
            ("cpu_starvation",  "medium"),
            ("network_latency", "mild"),
            ("memory_leak",     "heavy"),
            ("cpu_starvation",  "heavy"),
        ],
    },
]

TOTAL_RUNS = len(TRAINING_SCHEDULE)

# ── Injection code templates by type and intensity ─────────────────────────────

def _memory_leak_code(stage: str, intensity: str) -> str:
    sizes = {
        "mild":   {"stage3": 50,  "stage4": 80},
        "medium": {"stage3": 100, "stage4": 160},
        "heavy":  {"stage3": 200, "stage4": 320},
    }
    mb = sizes[intensity][stage]
    return (
        f"import time\n"
        f"data = bytearray({mb} * 1024 * 1024)\n"
        f"time.sleep(9999)\n"
    )

def _cpu_starvation_code(stage: str, intensity: str) -> str:
    threads = {
        "mild":   {"stage3": 2,  "stage4": 2},
        "medium": {"stage3": 4,  "stage4": 4},
        "heavy":  {"stage3": 6,  "stage4": 8},
    }
    n = threads[intensity][stage]
    return (
        "import threading, time\n"
        "def _burn():\n"
        "    while True:\n"
        "        [i * i for i in range(80000)]\n"
        f"threads = [threading.Thread(target=_burn, daemon=True) for _ in range({n})]\n"
        "[t.start() for t in threads]\n"
        "time.sleep(9999)\n"
    )

def _network_latency_code(stage: str, intensity: str) -> str:
    threads = {
        "mild":   {"stage3": 4,  "stage4": 4},
        "medium": {"stage3": 8,  "stage4": 12},
        "heavy":  {"stage3": 12, "stage4": 20},
    }
    n = threads[intensity][stage]
    return (
        "import socket, threading, time\n"
        "PAYLOAD = b'X' * 65536\n"
        "def _flood():\n"
        "    while True:\n"
        "        try:\n"
        "            srv = socket.socket()\n"
        "            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\n"
        "            srv.bind(('127.0.0.1', 0))\n"
        "            srv.listen(1)\n"
        "            port = srv.getsockname()[1]\n"
        "            cli = socket.socket()\n"
        "            cli.connect(('127.0.0.1', port))\n"
        "            conn, _ = srv.accept()\n"
        "            for _ in range(80): cli.sendall(PAYLOAD)\n"
        "            cli.close(); conn.close(); srv.close()\n"
        "        except Exception: time.sleep(0.05)\n"
        f"threads = [threading.Thread(target=_flood, daemon=True) for _ in range({n})]\n"
        "[t.start() for t in threads]\n"
        "time.sleep(9999)\n"
    )

def injection_code(failure_type: str, stage: str, intensity: str) -> str:
    if failure_type == "memory_leak":
        return _memory_leak_code(stage, intensity)
    elif failure_type == "cpu_starvation":
        return _cpu_starvation_code(stage, intensity)
    else:
        return _network_latency_code(stage, intensity)


# ── Training Injector ─────────────────────────────────────────────────────────

class TrainingInjector:
    """
    Manages injection for one 90-minute run with multiple events.
    Each event is independently registered in the FailureEventRegistry.
    """

    def __init__(
        self,
        docker_client: docker.DockerClient,
        registry: FailureEventRegistry,
        target_service: str,
    ) -> None:
        self._client  = docker_client
        self._reg     = registry
        self._target  = target_service
        self._scenario_ids: Dict[int, str] = {}   # event_idx → scenario_id

    def _find_container(self) -> Optional[Any]:
        svc = self._target
        try:
            for c in self._client.containers.list():
                name = c.name.lstrip("/")
                if name == svc or name.endswith(f"-{svc}-1") or name.endswith(f"_{svc}_1"):
                    return c
        except Exception as e:
            log.warning("Cannot find container '%s': %s", svc, e)
        return None

    def _exec(self, code: str) -> None:
        ctr = self._find_container()
        if ctr is None:
            log.warning("Container '%s' not found — skipping exec", self._target)
            return
        try:
            ctr.exec_run(["python3", "-c", code], detach=True)
        except Exception as e:
            log.warning("exec_run failed on %s: %s", self._target, e)

    def stage1_ramp(self, event_idx: int, failure_type: str, intensity: str) -> None:
        """Subtle ramp — no labels yet."""
        log.info("[INJECT] Event %d stage1 ramp (%s %s)", event_idx, failure_type, intensity)
        # Use a lighter version (one step below intensity) for the ramp
        ramp_intensity = {"heavy": "medium", "medium": "mild", "mild": "mild"}[intensity]
        self._exec(injection_code(failure_type, "stage3", ramp_intensity))

    def stage2_pre_ramp(self, event_idx: int, failure_type: str, intensity: str) -> None:
        """Pre-failure escalation — pre_failure label opens."""
        log.info("[INJECT] Event %d stage2 pre-failure (%s %s)", event_idx, failure_type, intensity)
        self._exec(injection_code(failure_type, "stage3", intensity))

    def stage3_active(self, event_idx: int, failure_type: str, intensity: str) -> str:
        """Register failure start + inject at full intensity."""
        sid = self._reg.register_failure_start(
            service_name=self._target,
            failure_type=failure_type,
        )
        self._scenario_ids[event_idx] = sid
        log.info("[INJECT] Event %d ACTIVE (%s %s) scenario=%s",
                 event_idx, failure_type, intensity, sid[:8])
        self._exec(injection_code(failure_type, "stage3", intensity))
        return sid

    def stage4_peak(self, event_idx: int, failure_type: str, intensity: str) -> None:
        """Peak injection — failure=1 continues."""
        log.info("[INJECT] Event %d peak (%s %s)", event_idx, failure_type, intensity)
        self._exec(injection_code(failure_type, "stage4", intensity))

    def recover(self, event_idx: int) -> None:
        """Register failure end + restart container."""
        sid = self._scenario_ids.get(event_idx)
        if sid:
            self._reg.register_failure_end(sid)
            log.info("[INJECT] Event %d failure end registered (scenario=%s)", event_idx, sid[:8])

        ctr = self._find_container()
        if ctr:
            try:
                log.info("[INJECT] Restarting %s ...", self._target)
                ctr.restart(timeout=15)
                time.sleep(8)  # wait for service to come back
            except Exception as e:
                log.warning("Restart failed: %s", e)


# ── Parallel Metrics Poller ───────────────────────────────────────────────────

class ParallelMetricsPoller:
    """
    Polls Docker stats for all containers in parallel threads.
    This is the key fix that keeps tick cadence near 15s despite 16 containers.
    """

    def __init__(self, docker_client: docker.DockerClient) -> None:
        self._client = docker_client
        self.rows: List[Dict] = []
        self._lock = threading.Lock()

    def _service_from_name(self, name: str) -> Optional[str]:
        name = name.lstrip("/")
        if name in ALL_MONITORED:
            return name
        for sep in ("-", "_"):
            if name.endswith(f"{sep}1"):
                parts = name.rsplit(sep, 2)
                if len(parts) >= 2 and parts[-1] == "1":
                    svc = parts[-2]
                    if svc in ALL_MONITORED:
                        return svc
        return None

    def _poll_one(self, container: Any, ts_iso: str) -> Optional[Dict]:
        svc = self._service_from_name(container.name)
        if svc is None:
            return None
        try:
            s = container.stats(stream=False)
        except Exception:
            return None
        return self._parse(s, ts_iso, svc)

    @staticmethod
    def _parse(s: Dict, ts_iso: str, svc: str) -> Dict:
        row: Dict = {"timestamp": ts_iso, "service_name": svc}

        # CPU
        try:
            cpu = s["cpu_stats"]; pcpu = s["precpu_stats"]
            cdelta = cpu["cpu_usage"]["total_usage"] - pcpu["cpu_usage"]["total_usage"]
            sdelta = cpu.get("system_cpu_usage", 0) - pcpu.get("system_cpu_usage", 0)
            ncpu   = cpu.get("online_cpus") or len(cpu["cpu_usage"].get("percpu_usage", [1]))
            row["cpu_usage_percent"] = round(cdelta / sdelta * ncpu * 100, 4) if sdelta > 0 else 0.0
        except Exception:
            row["cpu_usage_percent"] = 0.0

        # Memory
        try:
            mem   = s["memory_stats"]
            usage = float(mem.get("usage", 0))
            limit = float(mem.get("limit", -1))
            cache = float(mem.get("stats", {}).get("cache", 0))
            rss   = max(0.0, usage - cache)
            row["memory_usage_bytes"] = rss
            if 0 < limit < 9e18:
                row["memory_limit_bytes"]   = limit
                row["memory_usage_percent"] = round(rss / limit * 100, 4)
            else:
                row["memory_limit_bytes"]   = -1.0
                row["memory_usage_percent"] = round(rss / limit * 100, 4) if limit > 0 else 0.0
        except Exception:
            row["memory_usage_bytes"] = row["memory_limit_bytes"] = 0.0
            row["memory_usage_percent"] = 0.0

        # Network
        try:
            nets = s.get("networks", {})
            rx = sum(n.get("rx_bytes", 0) for n in nets.values())
            tx = sum(n.get("tx_bytes", 0) for n in nets.values())
            row["network_rx_bytes_per_sec"] = round(rx / 15, 2)
            row["network_tx_bytes_per_sec"] = round(tx / 15, 2)
        except Exception:
            row["network_rx_bytes_per_sec"] = row["network_tx_bytes_per_sec"] = 0.0

        # Block I/O
        try:
            bio = s.get("blkio_stats", {}).get("io_service_bytes_recursive") or []
            reads  = sum(b.get("value", 0) for b in bio if b.get("op") == "read")
            writes = sum(b.get("value", 0) for b in bio if b.get("op") == "write")
            row["fs_reads_per_sec"]  = round(reads  / 15, 2)
            row["fs_writes_per_sec"] = round(writes / 15, 2)
        except Exception:
            row["fs_reads_per_sec"] = row["fs_writes_per_sec"] = 0.0

        for col in ("request_rate", "error_rate", "p50_latency_ms",
                    "p99_latency_ms", "active_connections"):
            row[col] = 0.0

        return row

    def poll_once(self, timestamp: datetime) -> int:
        ts_iso = iso(timestamp)
        try:
            containers = self._client.containers.list()
        except Exception as e:
            log.warning("Container list failed: %s", e)
            return 0

        results = []
        with ThreadPoolExecutor(max_workers=min(16, len(containers))) as ex:
            futs = {ex.submit(self._poll_one, c, ts_iso): c for c in containers}
            for fut in as_completed(futs):
                row = fut.result()
                if row:
                    results.append(row)

        with self._lock:
            self.rows.extend(results)
        return len(results)

    def build_dataframe(self) -> pd.DataFrame:
        with self._lock:
            rows = list(self.rows)
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values(["service_name", "timestamp"]).reset_index(drop=True)

        # Trend columns (change from 20 rows back = 5 min)
        lookback = 20
        for svc, grp in df.groupby("service_name"):
            idx = grp.index
            for col, tc in [("cpu_usage_percent", "cpu_trend_5min"),
                             ("memory_usage_percent", "memory_trend_5min"),
                             ("error_rate", "error_rate_trend_5min")]:
                vals  = grp[col].values
                trend = np.zeros(len(vals))
                for i in range(lookback, len(vals)):
                    trend[i] = round(float(vals[i] - vals[i - lookback]), 6)
                df.loc[idx, tc] = trend

        for tc in ("cpu_trend_5min", "memory_trend_5min", "error_rate_trend_5min"):
            if tc not in df.columns:
                df[tc] = 0.0
            df[tc] = df[tc].fillna(0.0)

        df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S.") + \
                          df["timestamp"].dt.microsecond.apply(lambda x: f"{x//1000:03d}") + "Z"
        return df


# ── Fixed Log Streamer (Drain3 inner-message extraction) ──────────────────────

class TrainingLogStreamer:
    """
    Fetches logs from Loki and extracts inner message from JSON-formatted logs
    before feeding to Drain3. This is the key fix for getting real templates.
    """

    def __init__(self, drain_parser: Optional[Drain3Parser]) -> None:
        self.rows: List[Dict] = []
        self._parser = drain_parser

    def fetch_range(self, start: datetime, end: datetime, limit: int = 100) -> int:
        start_ns = int(start.timestamp() * 1e9)
        end_ns   = int(end.timestamp()   * 1e9)
        params = {
            "query":     '{compose_service=~".+"}',
            "start":     str(start_ns),
            "end":       str(end_ns),
            "limit":     str(limit),
            "direction": "forward",
        }
        try:
            resp = requests.get(
                f"{LOKI_URL}/loki/api/v1/query_range",
                params=params, timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ConnectionError:
            return 0
        except Exception as e:
            log.debug("Loki error: %s", e)
            return 0

        count = 0
        for stream in data.get("data", {}).get("result", []):
            labels = stream.get("stream", {})
            svc    = (labels.get("compose_service") or
                      labels.get("service_name") or
                      labels.get("service") or "unknown")
            for ts_ns_str, raw_msg in stream.get("values", []):
                ts_dt = datetime.fromtimestamp(int(ts_ns_str) / 1e9, tz=timezone.utc)
                self.rows.append(self._parse(raw_msg, ts_dt, svc))
                count += 1
        return count

    def _parse(self, raw: str, ts: datetime, svc: str) -> Dict:
        raw_trunc = raw[:500]
        msg_lower = raw.lower()

        # ── Severity detection ─────────────────────────────────────────────────
        severity = "INFO"
        for lvl in ("FATAL", "ERROR", "WARN", "WARNING", "INFO", "DEBUG"):
            if lvl in raw or lvl.lower() in raw:
                severity = "WARN" if lvl == "WARNING" else lvl
                break
        try:
            obj = json.loads(raw)
            sev = obj.get("severity") or obj.get("level") or obj.get("lvl") or ""
            if sev:
                severity = str(sev).upper()[:5]
        except (json.JSONDecodeError, AttributeError):
            pass

        # ── KEY FIX: extract inner message for Drain3 ──────────────────────────
        message_for_drain = raw_trunc
        try:
            obj = json.loads(raw)
            inner = (obj.get("message") or obj.get("msg") or
                     obj.get("MESSAGE") or obj.get("log") or "")
            if inner and isinstance(inner, str) and len(inner) > 5:
                message_for_drain = inner
        except (json.JSONDecodeError, AttributeError):
            pass

        template_id, template_str = "T0", message_for_drain
        if self._parser is not None:
            try:
                template_id, template_str = self._parser.process(message_for_drain)
            except Exception:
                pass

        is_error   = int(severity in ("ERROR", "FATAL"))
        is_warning = int(severity == "WARN")

        return {
            "log_timestamp":      iso(ts),
            "service_name":       svc,
            "severity":           severity,
            "drain_template_id":  template_id,
            "drain_template":     template_str,
            "raw_message":        raw_trunc,
            "is_error":           is_error,
            "is_warning":         is_warning,
            "message_length":     len(raw),
            "contains_exception": int(any(k in msg_lower for k in ("exception","traceback","panic"))),
            "contains_timeout":   int(any(k in msg_lower for k in ("timeout","timed out"))),
            "contains_oom":       int(any(k in msg_lower for k in ("out of memory","oom","killed"))),
            "timestamp":          iso(ts),
            "failure": 0, "pre_failure": 0, "future_failure": 0,
            "failure_type": "none", "scenario_id": "",
        }

    def build_dataframe(self) -> pd.DataFrame:
        if not self.rows:
            return pd.DataFrame()
        df = pd.DataFrame(self.rows)
        return df.drop_duplicates(
            subset=["log_timestamp", "service_name", "drain_template_id"]
        ).reset_index(drop=True)


# ── Parquet helpers ───────────────────────────────────────────────────────────

def append_parquet(new_df: pd.DataFrame, path: Path) -> int:
    if new_df.empty:
        return int(pd.read_parquet(path).shape[0]) if path.exists() else 0
    existing = pd.read_parquet(path) if path.exists() else pd.DataFrame()
    combined = pd.concat([existing, new_df], ignore_index=True)
    combined.to_parquet(path, index=False, engine="pyarrow")
    return len(combined)


def load_checkpoint() -> Dict:
    if CHECKPOINT_FILE.exists():
        return json.loads(CHECKPOINT_FILE.read_text())
    return {"completed_runs": 0, "run_results": []}


def save_checkpoint(cp: Dict) -> None:
    CHECKPOINT_FILE.write_text(json.dumps(cp, indent=2, default=str))


# ── Single 90-minute run ──────────────────────────────────────────────────────

def run_training_episode(
    run_idx: int,
    run_cfg: Dict,
    docker_client: docker.DockerClient,
    drain_parser: Drain3Parser,
) -> Dict:
    target  = run_cfg["target_service"]
    events  = run_cfg["events"]    # list of (failure_type, intensity)

    log.info("=" * 65)
    log.info("  Training Run %d/%d  →  %s", run_idx + 1, TOTAL_RUNS, target)
    log.info("  Events: %s", " | ".join(f"{ft}({inten})" for ft, inten in events))
    log.info("  Duration: %.0f min", TOTAL_RUN_S / 60)
    log.info("=" * 65)

    # Registry with extended 180s pre-failure buffer
    registry   = FailureEventRegistry(buffer_seconds=PRE_FAIL_BUFFER_S)
    metrics_p  = ParallelMetricsPoller(docker_client)
    log_s      = TrainingLogStreamer(drain_parser)
    jaeger_p   = JaegerPoller()
    injector   = TrainingInjector(docker_client, registry, target)

    start_time      = utcnow()
    log_fetch_start = start_time

    # Per-event injection state
    event_states = [
        {"s1": False, "s2": False, "s3": False, "s4": False, "rec": False}
        for _ in range(EVENTS_PER_RUN)
    ]

    # Precompute event timing offsets
    def event_offset(i: int) -> int:
        return NORMAL_BASELINE_S + i * EVENT_TOTAL_S

    log.info("Run starts at %s", iso(start_time))
    log.info("Expected end : %s", iso(start_time + timedelta(seconds=TOTAL_RUN_S)))

    while True:
        now     = utcnow()
        elapsed = (now - start_time).total_seconds()

        if elapsed >= TOTAL_RUN_S:
            log.info("Run %d complete (%.0fs elapsed)", run_idx + 1, elapsed)
            break

        # ── Injection scheduling ───────────────────────────────────────────────
        for i, (failure_type, intensity) in enumerate(events):
            state  = event_states[i]
            offset = event_offset(i)

            # Stage 1: subtle ramp (just after event window opens)
            if elapsed >= offset and not state["s1"]:
                injector.stage1_ramp(i, failure_type, intensity)
                state["s1"] = True

            # Stage 2: pre-failure escalation (30% into pre-fail window)
            pre_ramp_t = offset + EVENT_PRE_FAIL_S * 0.3
            if elapsed >= pre_ramp_t and not state["s2"]:
                injector.stage2_pre_ramp(i, failure_type, intensity)
                state["s2"] = True

            # Stage 3: active failure starts
            active_t = offset + EVENT_PRE_FAIL_S
            if elapsed >= active_t and not state["s3"]:
                injector.stage3_active(i, failure_type, intensity)
                state["s3"] = True

            # Stage 4: peak
            peak_t = offset + EVENT_PRE_FAIL_S + EVENT_ACTIVE_S * 0.5
            if elapsed >= peak_t and not state["s4"]:
                injector.stage4_peak(i, failure_type, intensity)
                state["s4"] = True

            # Recovery
            rec_t = offset + EVENT_PRE_FAIL_S + EVENT_ACTIVE_S
            if elapsed >= rec_t and not state["rec"]:
                injector.recover(i)
                state["rec"] = True

        # ── Metrics (parallel) ────────────────────────────────────────────────
        n_ctr = metrics_p.poll_once(utcnow())

        # ── Logs (small per-tick limit for speed) ────────────────────────────
        fetch_end = utcnow()
        log_s.fetch_range(log_fetch_start, fetch_end, limit=LOKI_LIMIT_PER_TICK)
        log_fetch_start = fetch_end

        # Progress log every ~5 min
        if int(elapsed) % 300 < POLL_INTERVAL_S + 5:
            active_events = sum(
                1 for i, s in enumerate(event_states)
                if s["s3"] and not s["rec"]
            )
            log.info("  t=%.0f/%ds  containers=%d  logs=%d  active_injections=%d",
                     elapsed, TOTAL_RUN_S, n_ctr, len(log_s.rows), active_events)

        # Sleep to maintain ~15s cadence
        elapsed_tick = (utcnow() - now).total_seconds()
        time.sleep(max(0, POLL_INTERVAL_S - elapsed_tick))

    # ── Jaeger traces for this run ─────────────────────────────────────────────
    log.info("Fetching traces ...")
    for svc in JAEGER_SERVICES:
        jaeger_p.fetch_service_traces(svc, start_time, utcnow(), limit=400)

    # ── Build DataFrames ──────────────────────────────────────────────────────
    log.info("Building DataFrames ...")
    metrics_df = metrics_p.build_dataframe()
    logs_df    = log_s.build_dataframe()
    traces_df  = jaeger_p.build_dataframe()

    # ── Stamp labels ──────────────────────────────────────────────────────────
    # metrics/logs: match by service_name (injection target)
    # traces: global timestamp matching (fixes the Jaeger name mismatch bug)
    if not metrics_df.empty:
        metrics_df = registry.compute_labels_for_dataframe(metrics_df)
    if not logs_df.empty:
        logs_df = registry.compute_labels_for_dataframe(
            logs_df, ts_col="log_timestamp", svc_col="service_name")
    if not traces_df.empty:
        traces_df = registry.compute_global_labels_for_dataframe(
            traces_df, ts_col="start_time")

    # ── Log aggregates ────────────────────────────────────────────────────────
    log_agg_df = pd.DataFrame()
    if not logs_df.empty:
        log_agg_df = LogAggregator().build(logs_df)

    # ── Validate ──────────────────────────────────────────────────────────────
    for name, df in [("metrics", metrics_df), ("logs", logs_df), ("traces", traces_df)]:
        if not df.empty:
            r = validate_labels(df, strict=False)
            s = r["stats"]
            status = "✓" if r["passed"] else "✗"
            log.info("  %s %s: %d rows | failure=%d pre_failure=%d future=%d normal=%d",
                     status, name, s["total_rows"], s["failure_rows"],
                     s["pre_failure_rows"], s["future_failure_rows"], s["normal_rows"])

    # ── Append to training parquet files ──────────────────────────────────────
    row_totals = {}
    for name, df in [
        ("training_metrics",        metrics_df),
        ("training_logs",           logs_df),
        ("training_traces",         traces_df),
        ("training_log_aggregates", log_agg_df),
    ]:
        row_totals[name] = append_parquet(df, TRAINING_DIR / f"{name}.parquet")

    log.info("  Cumulative: metrics=%s  logs=%s  traces=%s  log_agg=%s",
             row_totals.get("training_metrics", 0),
             row_totals.get("training_logs", 0),
             row_totals.get("training_traces", 0),
             row_totals.get("training_log_aggregates", 0))

    val_stats = {}
    for name, df in [("metrics", metrics_df), ("logs", logs_df), ("traces", traces_df)]:
        if not df.empty:
            val_stats[name] = validate_labels(df, strict=False)["stats"]

    return {
        "run_idx":        run_idx,
        "target_service": target,
        "start_time":     iso(start_time),
        "end_time":       iso(utcnow()),
        "events":         [{"failure_type": ft, "intensity": inten} for ft, inten in events],
        "rows_this_run": {
            "metrics": len(metrics_df), "logs": len(logs_df),
            "traces":  len(traces_df),  "log_aggregates": len(log_agg_df),
        },
        "cumulative_rows": row_totals,
        "label_stats":     val_stats,
        "failure_events":  registry.get_summary()["events"],
    }


# ── Final: CSVs + summary + git push ─────────────────────────────────────────

def write_csvs() -> None:
    for name in ["training_metrics", "training_logs", "training_log_aggregates"]:
        pq = TRAINING_DIR / f"{name}.parquet"
        if pq.exists():
            df = pd.read_parquet(pq)
            df.to_csv(TRAINING_DIR / f"{name}.csv", index=False)
            log.info("  CSV: %s.csv (%d rows)", name, len(df))


def write_summary(cp: Dict) -> None:
    runs = cp["run_results"]
    last = runs[-1] if runs else {}
    cr   = last.get("cumulative_rows", {})

    totals = {"failure_rows": 0, "pre_failure_rows": 0,
              "future_failure_rows": 0, "normal_rows": 0}
    for r in runs:
        for s in r.get("label_stats", {}).values():
            for k in totals:
                totals[k] += s.get(k, 0)

    summary = {
        "generated_at":    iso(utcnow()),
        "total_runs":      len(runs),
        "total_duration_h": round(sum(
            (datetime.fromisoformat(r["end_time"].replace("Z", "+00:00")) -
             datetime.fromisoformat(r["start_time"].replace("Z", "+00:00"))
             ).total_seconds() for r in runs if "end_time" in r
        ) / 3600, 2),
        "cumulative_rows": cr,
        "pre_failure_buffer_seconds": PRE_FAIL_BUFFER_S,
        "events_per_run":  EVENTS_PER_RUN,
        "label_totals":    totals,
        "drain3_inner_message_extraction": True,
        "trace_labeling":  "global_timestamp",
        "run_log": runs,
    }
    SUMMARY_FILE.write_text(json.dumps(summary, indent=2, default=str))
    log.info("Summary → %s", SUMMARY_FILE)


def git_push(cp: Dict) -> None:
    log.info("Preparing git push ...")
    runs = cp["run_results"]
    last = runs[-1] if runs else {}
    cr   = last.get("cumulative_rows", {})

    files = [
        str(TRAINING_DIR / "training_metrics.parquet"),
        str(TRAINING_DIR / "training_metrics.csv"),
        str(TRAINING_DIR / "training_logs.parquet"),
        str(TRAINING_DIR / "training_logs.csv"),
        str(TRAINING_DIR / "training_traces.parquet"),
        str(TRAINING_DIR / "training_log_aggregates.parquet"),
        str(TRAINING_DIR / "training_log_aggregates.csv"),
        str(TRAINING_DIR / "collection_summary.json"),
        str(TRAINING_DIR / "checkpoint.json"),
        str(PIPELINE_DIR / "scripts" / "collect_training.py"),
        str(PIPELINE_DIR / "scripts" / "label_engine.py"),
        str(PIPELINE_DIR / "scripts" / "run_training.sh"),
    ]
    existing = [f for f in files if Path(f).exists()]
    subprocess.run(["git", "add", "-f"] + existing, cwd=REPO_ROOT, check=True)

    msg = (
        f"data(training): 5×90-min continuous training dataset\n\n"
        f"  training_metrics:        {cr.get('training_metrics','?'):>7} rows\n"
        f"  training_logs:           {cr.get('training_logs','?'):>7} rows\n"
        f"  training_traces:         {cr.get('training_traces','?'):>7} rows\n"
        f"  training_log_aggregates: {cr.get('training_log_aggregates','?'):>7} rows\n\n"
        f"Fixes vs previous dataset:\n"
        f"  - Continuous 90-min runs (valid LSTM sliding windows)\n"
        f"  - 4 injection events per run (more positive sequences)\n"
        f"  - Drain3 inner-message extraction (real log templates)\n"
        f"  - Global timestamp trace labeling (traces now labeled)\n"
        f"  - 180s pre-failure buffer (12 timesteps, up from 5)\n"
        f"  - Varied injection intensity (mild/medium/heavy)\n"
        f"  - Parallel Docker stats polling (faster ticks)\n\n"
        f"Output: pipeline/data/training/\n\n"
        f"Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
    )
    r = subprocess.run(["git", "commit", "-m", msg],
                       cwd=REPO_ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        log.error("git commit failed: %s", r.stderr)
        return
    log.info("git commit OK")

    r = subprocess.run(["git", "push", "origin", "main"],
                       cwd=REPO_ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        log.error("git push failed: %s", r.stderr)
    else:
        log.info("git push OK → origin/main")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    log.info("=" * 65)
    log.info("  Training Dataset Collection — %d × 90-min runs", TOTAL_RUNS)
    log.info("  Total: ~%.1f hours  |  Output: %s", TOTAL_RUNS * 1.5, TRAINING_DIR)
    log.info("=" * 65)

    try:
        client = docker.from_env()
        client.ping()
        log.info("Docker OK")
    except Exception as e:
        log.error("Docker error: %s", e)
        sys.exit(1)

    cp        = load_checkpoint()
    completed = cp["completed_runs"]
    if completed > 0:
        log.info("Resuming from run %d / %d", completed + 1, TOTAL_RUNS)

    drain_parser = Drain3Parser()

    for run_idx in range(completed, TOTAL_RUNS):
        run_cfg = TRAINING_SCHEDULE[run_idx]
        try:
            result = run_training_episode(run_idx, run_cfg, client, drain_parser)
        except KeyboardInterrupt:
            log.warning("Interrupted — progress saved at run %d", run_idx)
            break
        except Exception as e:
            log.error("Run %d failed: %s", run_idx, e, exc_info=True)
            result = {"run_idx": run_idx, "error": str(e),
                      "rows_this_run": {}, "cumulative_rows": {},
                      "label_stats": {}, "failure_events": []}

        cp["completed_runs"] = run_idx + 1
        cp["run_results"].append(result)
        save_checkpoint(cp)

        if run_idx < TOTAL_RUNS - 1:
            log.info("Pausing 30s before next run ...")
            time.sleep(30)

    log.info("")
    log.info("=" * 65)
    log.info("  All %d runs done!", cp["completed_runs"])
    log.info("=" * 65)

    write_csvs()
    write_summary(cp)
    git_push(cp)
    log.info("Done — dataset live on GitHub.")


if __name__ == "__main__":
    main()
