#!/usr/bin/env python3
"""
collect_demo.py — 5-minute demo dataset collection script.

Collects metrics, logs, and traces from the running Online Boutique stack,
injects a single gradual memory-leak failure into recommendationservice,
and produces four Parquet/CSV tables:

  pipeline/data/processed/demo_metrics.parquet
  pipeline/data/processed/demo_logs.parquet
  pipeline/data/processed/demo_traces.parquet
  pipeline/data/processed/demo_log_aggregates.parquet
  pipeline/data/processed/demo_collection_summary.json

Run from the repo root:
  python3 pipeline/scripts/collect_demo.py

Prerequisites:
  pip3 install -r pipeline/requirements.txt
  docker compose up -d   (all 17 containers must be running)
"""

from __future__ import annotations

import json
import logging
import os
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

# ── Add pipeline root to path so label_engine is importable ──────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PIPELINE_DIR = REPO_ROOT / "pipeline"
sys.path.insert(0, str(PIPELINE_DIR / "scripts"))

from label_engine import (
    FailureEventRegistry,
    validate_labels,
    PRE_FAILURE_BUFFER_K,
    TIMESTEP_SECONDS,
    BUFFER_SECONDS,
)

# ── Drain3 import (optional — graceful fallback if not installed) ─────────────
try:
    from drain3 import TemplateMiner
    from drain3.template_miner_config import TemplateMinerConfig
    DRAIN3_AVAILABLE = True
except ImportError:
    DRAIN3_AVAILABLE = False
    logging.warning("drain3 not installed — log templates will be raw messages")

# ── Configuration ──────────────────────────────────────────────────────────────

LOKI_URL      = "http://localhost:3100"
JAEGER_URL    = "http://localhost:16686"
DOCKER_SOCKET = "unix://var/run/docker.sock"

COMPOSE_PROJECT  = "microservices-demo"
INJECT_SERVICE   = "recommendationservice"   # has python3 available
POLL_INTERVAL_S  = 15                         # seconds between metric snapshots

# Collection timing (seconds from script start)
NORMAL_PHASE_S   = 90    # 6 × 15 s normal baseline
PRE_FAIL_PHASE_S = 75    # 5 × 15 s pre-failure ramp (matches BUFFER_SECONDS)
ACTIVE_FAIL_S    = 120   # 8 × 15 s active injection
RECOVERY_S       = 60    # 4 × 15 s post-recovery
TOTAL_RUN_S      = NORMAL_PHASE_S + PRE_FAIL_PHASE_S + ACTIVE_FAIL_S + RECOVERY_S  # 345 s ≈ 6 min

OUTPUT_DIR       = PIPELINE_DIR / "data" / "processed"
DRAIN_INI        = PIPELINE_DIR / "data" / "drain3.ini"
DRAIN_STATE_FILE = PIPELINE_DIR / "data" / "drain3_state.json"

# Online Boutique services (10 app services — loadgenerator excluded from labels)
APP_SERVICES = [
    "frontend",
    "cartservice",
    "productcatalogservice",
    "currencyservice",
    "paymentservice",
    "shippingservice",
    "emailservice",
    "checkoutservice",
    "recommendationservice",
    "adservice",
]

# Observability services (also monitored for metrics, no failure labels)
OBS_SERVICES = ["prometheus", "loki", "jaeger", "grafana", "promtail", "loadgenerator"]

ALL_MONITORED = APP_SERVICES + OBS_SERVICES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("collect_demo")


# ── Utility ────────────────────────────────────────────────────────────────────

def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def floor15(dt: datetime) -> datetime:
    """Floor a datetime to the nearest 15-second boundary."""
    s = (dt.hour * 3600 + dt.minute * 60 + dt.second) // 15 * 15
    return dt.replace(hour=s // 3600, minute=(s % 3600) // 60,
                      second=s % 60, microsecond=0)


# ── Docker Stats Poller ────────────────────────────────────────────────────────

class MetricsPoller:
    """
    Polls Docker Stats API for all app containers every POLL_INTERVAL_S seconds.
    Stores raw rows keyed by (timestamp_iso, service_name).
    """

    def __init__(self, docker_client: docker.DockerClient) -> None:
        self._client = docker_client
        self.rows: List[Dict] = []
        self._lock = threading.Lock()

    def _container_name_to_service(self, name: str) -> Optional[str]:
        """
        Map a container name to a service name.

        This stack uses explicit container_name: in docker-compose.yml, so the
        container names are already the bare service names (e.g. "frontend",
        "recommendationservice"). We also handle the standard Compose pattern
        <project>-<service>-<index> as a fallback.
        """
        name = name.lstrip("/")

        # Case 1: bare name matches directly (our docker-compose.yml uses container_name:)
        if name in ALL_MONITORED:
            return name

        # Case 2: <project>-<service>-<index>  (standard Compose v2 naming)
        prefix = f"{COMPOSE_PROJECT}-"
        if name.startswith(prefix):
            rest = name[len(prefix):]
            parts = rest.rsplit("-", 1)
            svc = parts[0] if len(parts) == 2 and parts[1].isdigit() else rest
            if svc in ALL_MONITORED:
                return svc

        # Case 3: <project>_<service>_<index>  (legacy Compose v1 naming)
        prefix_v1 = f"{COMPOSE_PROJECT}_"
        if name.startswith(prefix_v1):
            rest = name[len(prefix_v1):]
            parts = rest.rsplit("_", 1)
            svc = parts[0] if len(parts) == 2 and parts[1].isdigit() else rest
            if svc in ALL_MONITORED:
                return svc

        return None

    def poll_once(self, timestamp: datetime) -> int:
        """Poll all running containers; return number of containers sampled."""
        ts_iso = iso(timestamp)
        try:
            containers = self._client.containers.list()
        except Exception as e:
            log.warning("Docker list containers failed: %s", e)
            return 0

        sampled = 0
        for ctr in containers:
            svc = self._container_name_to_service(ctr.name)
            if svc is None:
                continue
            try:
                stats = ctr.stats(stream=False)
            except Exception as e:
                log.debug("Stats failed for %s: %s", ctr.name, e)
                continue

            row = self._parse_stats(stats, ts_iso, svc)
            with self._lock:
                self.rows.append(row)
            sampled += 1

        return sampled

    @staticmethod
    def _parse_stats(s: Dict, ts_iso: str, svc: str) -> Dict:
        """Extract and compute metrics from raw Docker stats dict."""
        row: Dict[str, Any] = {
            "timestamp": ts_iso,
            "service_name": svc,
        }

        # ── CPU ──────────────────────────────────────────────────────────────
        try:
            cpu = s["cpu_stats"]
            precpu = s["precpu_stats"]
            cpu_delta = (cpu["cpu_usage"]["total_usage"]
                         - precpu["cpu_usage"]["total_usage"])
            sys_delta = (cpu.get("system_cpu_usage", 0)
                         - precpu.get("system_cpu_usage", 0))
            num_cpus = cpu.get("online_cpus") or len(cpu["cpu_usage"].get("percpu_usage", [1]))
            if sys_delta > 0:
                row["cpu_usage_percent"] = round(cpu_delta / sys_delta * num_cpus * 100, 4)
            else:
                row["cpu_usage_percent"] = 0.0
        except (KeyError, ZeroDivisionError):
            row["cpu_usage_percent"] = 0.0

        # ── Memory ────────────────────────────────────────────────────────────
        try:
            mem = s["memory_stats"]
            usage = float(mem.get("usage", 0))
            limit = float(mem.get("limit", -1))
            # Docker includes file cache in "usage"; subtract it for RSS-like
            cache = float(mem.get("stats", {}).get("cache", 0))
            rss = max(0.0, usage - cache)
            row["memory_usage_bytes"] = rss
            if limit > 0 and limit < 9e18:   # 9e18 ≈ "unlimited" on Linux
                row["memory_limit_bytes"] = limit
                row["memory_usage_percent"] = round(rss / limit * 100, 4)
            else:
                row["memory_limit_bytes"] = -1.0
                # Fall back to total node memory reported in stats
                total = float(mem.get("limit", 0))
                row["memory_usage_percent"] = round(rss / total * 100, 4) if total > 0 else 0.0
        except (KeyError, ZeroDivisionError):
            row["memory_usage_bytes"] = 0.0
            row["memory_limit_bytes"] = -1.0
            row["memory_usage_percent"] = 0.0

        # ── Network ───────────────────────────────────────────────────────────
        try:
            nets = s.get("networks", {})
            rx = sum(n.get("rx_bytes", 0) for n in nets.values())
            tx = sum(n.get("tx_bytes", 0) for n in nets.values())
            # Convert cumulative bytes to per-second rates using poll interval
            row["network_rx_bytes_per_sec"] = round(rx / POLL_INTERVAL_S, 2)
            row["network_tx_bytes_per_sec"] = round(tx / POLL_INTERVAL_S, 2)
        except Exception:
            row["network_rx_bytes_per_sec"] = 0.0
            row["network_tx_bytes_per_sec"] = 0.0

        # ── Block I/O ─────────────────────────────────────────────────────────
        try:
            bio = s.get("blkio_stats", {}).get("io_service_bytes_recursive") or []
            reads  = sum(b.get("value", 0) for b in bio if b.get("op") == "read")
            writes = sum(b.get("value", 0) for b in bio if b.get("op") == "write")
            row["fs_reads_per_sec"]  = round(reads  / POLL_INTERVAL_S, 2)
            row["fs_writes_per_sec"] = round(writes / POLL_INTERVAL_S, 2)
        except Exception:
            row["fs_reads_per_sec"]  = 0.0
            row["fs_writes_per_sec"] = 0.0

        # ── Request metrics (not available via Docker stats — fill with 0) ────
        for col in ("request_rate", "error_rate", "p50_latency_ms",
                    "p99_latency_ms", "active_connections"):
            row[col] = 0.0

        return row

    def build_dataframe(self) -> pd.DataFrame:
        """Convert accumulated rows to a DataFrame and compute trend columns."""
        with self._lock:
            rows = list(self.rows)

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values(["service_name", "timestamp"]).reset_index(drop=True)

        # ── Trend metrics (delta from 5 min ago = 20 rows back at 15 s each) ─
        lookback = 20   # 5 min / 15 s
        for svc, grp in df.groupby("service_name"):
            idx = grp.index
            for col, trend_col in [
                ("cpu_usage_percent",   "cpu_trend_5min"),
                ("memory_usage_percent","memory_trend_5min"),
                ("error_rate",          "error_rate_trend_5min"),
            ]:
                vals = grp[col].values
                trend = np.zeros(len(vals))
                for i in range(lookback, len(vals)):
                    trend[i] = round(float(vals[i] - vals[i - lookback]), 6)
                df.loc[idx, trend_col] = trend

        # Fill trend cols for services with fewer than lookback samples
        for tc in ("cpu_trend_5min", "memory_trend_5min", "error_rate_trend_5min"):
            if tc not in df.columns:
                df[tc] = 0.0
            df[tc] = df[tc].fillna(0.0)

        # Convert timestamp back to ISO string for schema compliance
        df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S.") + \
                          df["timestamp"].dt.microsecond.apply(lambda x: f"{x // 1000:03d}") + "Z"

        return df


# ── Log Streamer (Loki) ────────────────────────────────────────────────────────

class LogStreamer:
    """
    Queries Loki for logs from all app containers over a time window.
    Parses each log line and optionally extracts Drain3 templates.
    """

    def __init__(self, drain_parser: Optional["Drain3Parser"]) -> None:
        self.rows: List[Dict] = []
        self._parser = drain_parser
        self._seen_templates: set = set()

    def fetch_range(self, start: datetime, end: datetime, limit: int = 5000) -> int:
        """Fetch all logs from Loki between start and end. Returns count fetched."""
        start_ns = int(start.timestamp() * 1e9)
        end_ns   = int(end.timestamp()   * 1e9)

        params = {
            "query": '{compose_service=~".+"}',
            "start": str(start_ns),
            "end":   str(end_ns),
            "limit": str(limit),
            "direction": "forward",
        }

        try:
            resp = requests.get(
                f"{LOKI_URL}/loki/api/v1/query_range",
                params=params,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ConnectionError:
            log.warning("Loki not reachable at %s", LOKI_URL)
            return 0
        except Exception as e:
            log.warning("Loki query failed: %s", e)
            return 0

        result = data.get("data", {}).get("result", [])
        count = 0
        for stream in result:
            labels  = stream.get("stream", {})
            # Prefer compose_service (set by Promtail Docker SD), fall back to service
            svc = (labels.get("compose_service")
                   or labels.get("service_name")
                   or labels.get("service")
                   or "unknown")
            values  = stream.get("values", [])

            for ts_ns_str, raw_msg in values:
                ts_ns = int(ts_ns_str)
                ts_dt = datetime.fromtimestamp(ts_ns / 1e9, tz=timezone.utc)
                row = self._parse_log_line(raw_msg, ts_dt, svc)
                self.rows.append(row)
                count += 1

        return count

    def _parse_log_line(self, raw: str, ts: datetime, svc: str) -> Dict:
        """Parse a single log line into a row dict."""
        raw_trunc = raw[:500]
        msg_lower = raw.lower()

        # Severity detection
        severity = "UNKNOWN"
        for lvl in ("FATAL", "ERROR", "WARN", "WARNING", "INFO", "DEBUG"):
            kw = lvl if lvl != "WARNING" else "WARN"
            if lvl in raw or lvl.lower() in raw:
                severity = kw
                break
        if severity == "UNKNOWN":
            # Try JSON log format
            try:
                obj = json.loads(raw)
                sev_field = obj.get("severity") or obj.get("level") or obj.get("lvl") or ""
                severity = sev_field.upper()[:7] if sev_field else "INFO"
            except (json.JSONDecodeError, AttributeError):
                severity = "INFO"

        severity_map = {
            "FATAL": "FATAL", "ERROR": "ERROR", "WARN": "WARN",
            "WARNING": "WARN", "INFO": "INFO", "DEBUG": "DEBUG",
        }
        severity = severity_map.get(severity, "UNKNOWN")

        # Drain3 template extraction
        template_id = "T0"
        template_str = raw_trunc
        if self._parser is not None:
            template_id, template_str = self._parser.process(raw_trunc)

        # Boolean flags
        is_error   = int(severity in ("ERROR", "FATAL"))
        is_warning = int(severity == "WARN")
        contains_exception = int(any(k in msg_lower for k in
                                     ("exception", "traceback", "panic")))
        contains_timeout   = int(any(k in msg_lower for k in ("timeout", "timed out")))
        contains_oom       = int(any(k in msg_lower for k in
                                     ("out of memory", "oom", "killed")))

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
            "contains_exception": contains_exception,
            "contains_timeout":   contains_timeout,
            "contains_oom":       contains_oom,
            # Label cols — filled later by registry
            "timestamp":          iso(ts),
            "failure":            0,
            "pre_failure":        0,
            "future_failure":     0,
            "failure_type":       "none",
            "scenario_id":        "",
        }

    def build_dataframe(self) -> pd.DataFrame:
        if not self.rows:
            return pd.DataFrame()
        df = pd.DataFrame(self.rows)
        # Drop duplicate (log_timestamp, service_name, drain_template_id)
        df = df.drop_duplicates(
            subset=["log_timestamp", "service_name", "drain_template_id"]
        ).reset_index(drop=True)
        return df


# ── Jaeger Trace Poller ────────────────────────────────────────────────────────

class JaegerPoller:
    """Fetches trace spans from the Jaeger HTTP API."""

    def __init__(self) -> None:
        self.rows: List[Dict] = []

    def fetch_service_traces(
        self,
        service: str,
        start: datetime,
        end: datetime,
        limit: int = 200,
    ) -> int:
        """Fetch traces for one service. Returns number of spans collected."""
        start_us = int(start.timestamp() * 1e6)
        end_us   = int(end.timestamp()   * 1e6)

        params = {
            "service": service,
            "start":   str(start_us),
            "end":     str(end_us),
            "limit":   str(limit),
        }

        try:
            resp = requests.get(
                f"{JAEGER_URL}/api/traces",
                params=params,
                timeout=15,
            )
            if resp.status_code == 404:
                return 0
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ConnectionError:
            log.debug("Jaeger not reachable")
            return 0
        except Exception as e:
            log.debug("Jaeger query error for %s: %s", service, e)
            return 0

        count = 0
        for trace in data.get("data", []):
            trace_id = trace.get("traceID", "")
            processes = trace.get("processes", {})
            for span in trace.get("spans", []):
                row = self._parse_span(span, trace_id, processes)
                self.rows.append(row)
                count += 1

        return count

    @staticmethod
    def _parse_span(span: Dict, trace_id: str, processes: Dict) -> Dict:
        span_id      = span.get("spanID", "")
        parent_id    = ""
        refs = span.get("references", [])
        for ref in refs:
            if ref.get("refType") == "CHILD_OF":
                parent_id = ref.get("spanID", "")
                break

        # Start time: Jaeger uses microseconds
        start_us = span.get("startTime", 0)
        start_dt = datetime.fromtimestamp(start_us / 1e6, tz=timezone.utc)
        duration_us = span.get("duration", 0)
        duration_ms = round(duration_us / 1000.0, 3)

        # Tags
        tags_dict: Dict[str, Any] = {}
        for tag in span.get("tags", []):
            tags_dict[tag.get("key", "")] = tag.get("value")

        http_status = int(tags_dict.get("http.status_code", 0) or 0)
        otel_status = str(tags_dict.get("otel.status_code", "") or "")
        error_tag   = bool(tags_dict.get("error", False))

        if otel_status.upper() == "ERROR" or error_tag:
            status_code = "ERROR"
        elif otel_status.upper() == "OK":
            status_code = "OK"
        else:
            status_code = "UNSET"

        is_error = int(status_code == "ERROR" or http_status >= 500)

        # Caller / callee services
        proc_key     = span.get("processID", "")
        caller_svc   = processes.get(proc_key, {}).get("serviceName", "")
        callee_svc   = str(tags_dict.get("peer.service") or
                           tags_dict.get("net.peer.name") or "")

        tags_str = json.dumps(tags_dict)[:1000]

        return {
            "trace_id":        trace_id,
            "span_id":         span_id,
            "parent_span_id":  parent_id,
            "operation_name":  span.get("operationName", ""),
            "start_time":      iso(start_dt),
            "duration_ms":     duration_ms,
            "status_code":     status_code,
            "http_status_code": http_status,
            "is_error":        is_error,
            "tags":            tags_str,
            "caller_service":  caller_svc,
            "callee_service":  callee_svc,
            # Common key cols
            "timestamp":       iso(start_dt),
            "service_name":    caller_svc,
            "failure":         0,
            "pre_failure":     0,
            "future_failure":  0,
            "failure_type":    "none",
            "scenario_id":     "",
        }

    def build_dataframe(self) -> pd.DataFrame:
        if not self.rows:
            return pd.DataFrame()
        df = pd.DataFrame(self.rows)
        df = df.drop_duplicates(subset=["trace_id", "span_id"]).reset_index(drop=True)
        return df


# ── Drain3 Parser wrapper ─────────────────────────────────────────────────────

class Drain3Parser:
    """Thin wrapper around drain3.TemplateMiner."""

    def __init__(self) -> None:
        if not DRAIN3_AVAILABLE:
            self._miner = None
            return

        config = TemplateMinerConfig()
        if DRAIN_INI.exists():
            config.load(str(DRAIN_INI))

        # Use file-based persistence if state file exists
        if DRAIN_STATE_FILE.exists():
            from drain3.file_persistence import FilePersistence
            persistence = FilePersistence(str(DRAIN_STATE_FILE))
        else:
            persistence = None

        self._miner = TemplateMiner(
            persistence_handler=persistence,
            config=config,
        )

    def process(self, message: str):
        """Return (template_id, template_str)."""
        if self._miner is None:
            return "T0", message
        try:
            result = self._miner.add_log_message(message)
            if result:
                cluster = result["cluster"]
                tid = f"T{cluster.cluster_id}"
                tpl = cluster.get_template()
                return tid, tpl
        except Exception:
            pass
        return "T0", message


# ── Log Aggregator ─────────────────────────────────────────────────────────────

class LogAggregator:
    """
    Builds the log_aggregates table from raw log rows.
    One row per (service, 15-second window).
    """

    def build(self, logs_df: pd.DataFrame) -> pd.DataFrame:
        if logs_df.empty:
            return pd.DataFrame()

        df = logs_df.copy()
        df["_ts"] = pd.to_datetime(df["log_timestamp"], utc=True)
        df["_bucket"] = df["_ts"].dt.floor("15s")

        agg_rows = []
        seen_templates_global: set = set()
        prev_window_totals: Dict[str, int] = {}

        # Process windows in chronological order
        for (bucket, svc), grp in df.groupby(["_bucket", "service_name"]):
            total  = len(grp)
            errors = int(grp["is_error"].sum())
            warns  = int(grp["is_warning"].sum())
            infos  = int((grp["severity"] == "INFO").sum())

            templates = grp["drain_template_id"].tolist()
            tpl_counts = pd.Series(templates).value_counts()
            unique_t = len(tpl_counts)

            # Shannon entropy
            if unique_t > 1:
                probs = tpl_counts / tpl_counts.sum()
                entropy = float(-np.sum(probs * np.log2(probs + 1e-12)))
            else:
                entropy = 0.0

            # New templates (never seen in any prior window)
            new_t = len(set(templates) - seen_templates_global)
            seen_templates_global.update(templates)

            exc_count  = int(grp["contains_exception"].sum())
            to_count   = int(grp["contains_timeout"].sum())
            oom_count  = int(grp["contains_oom"].sum())
            avg_len    = float(grp["message_length"].mean())

            # Log volume change %
            prev_total = prev_window_totals.get(svc, 0)
            if prev_total > 0:
                vol_change = round((total / prev_total - 1) * 100, 4)
            else:
                vol_change = 0.0
            prev_window_totals[svc] = total

            # Grab label from any row in this window (they should all match)
            first = grp.iloc[0]

            agg_rows.append({
                "window_start":        iso(bucket),
                "window_end":          iso(bucket + timedelta(seconds=15)),
                "service_name":        svc,
                "total_log_lines":     total,
                "error_count":         errors,
                "warning_count":       warns,
                "info_count":          infos,
                "error_rate_logs":     round(errors / total, 6) if total > 0 else 0.0,
                "warning_rate_logs":   round(warns  / total, 6) if total > 0 else 0.0,
                "unique_templates":    unique_t,
                "template_entropy":    round(entropy, 6),
                "new_templates_seen":  new_t,
                "exception_count":     exc_count,
                "timeout_count":       to_count,
                "oom_mention_count":   oom_count,
                "avg_message_length":  round(avg_len, 2),
                "log_volume_change_pct": vol_change,
                # Common label cols (carried from logs)
                "timestamp":           iso(bucket),
                "failure":             int(first["failure"]),
                "pre_failure":         int(first["pre_failure"]),
                "future_failure":      int(first["future_failure"]),
                "failure_type":        str(first["failure_type"]),
                "scenario_id":         str(first["scenario_id"]),
            })

        return pd.DataFrame(agg_rows)


# ── Failure Injector ───────────────────────────────────────────────────────────

class FailureInjector:
    """
    Injects a gradual memory leak into recommendationservice via docker exec.

    5-stage injection timeline:
      Stage 0: normal baseline          (0 MB extra)
      Stage 1: slight ramp              (30 MB)   — failure=0, pre_failure=0
      Stage 2: pre-failure buffer start (80 MB)   — pre_failure=1 window opens
      Stage 3: active failure begins    (150 MB)  — failure=1
      Stage 4: peak failure             (200 MB)  — failure=1
      Recovery: container restart
    """

    def __init__(
        self,
        docker_client: docker.DockerClient,
        registry: FailureEventRegistry,
    ) -> None:
        self._client   = docker_client
        self._registry = registry
        self._scenario_id: Optional[str] = None
        self._alloc_handle: Optional[Any] = None

    def _find_container(self) -> Optional[Any]:
        """Find the recommendationservice container."""
        try:
            for c in self._client.containers.list():
                name = c.name.lstrip("/")
                # Match bare name (our stack uses container_name:) OR
                # Compose-prefixed name e.g. microservices-demo-recommendationservice-1
                if name == INJECT_SERVICE or name.endswith(f"-{INJECT_SERVICE}-1") \
                        or name.endswith(f"_{INJECT_SERVICE}_1"):
                    return c
        except Exception as e:
            log.warning("Could not find injection target: %s", e)
        return None

    def _exec_python(self, container: Any, code: str) -> bool:
        """Run a python3 -c snippet inside the container. Returns True on success."""
        try:
            result = container.exec_run(
                ["python3", "-c", code],
                detach=False,
                stream=False,
            )
            if result.exit_code not in (0, None):
                log.debug("exec returned exit code %s", result.exit_code)
                return False
            return True
        except Exception as e:
            log.warning("exec_run failed: %s", e)
            return False

    def stage1_ramp(self) -> bool:
        """Allocate ~30 MB — normal operation, no labels set."""
        ctr = self._find_container()
        if ctr is None:
            return False
        log.info("[INJECTOR] Stage 1 — gentle ramp (30 MB)")
        code = (
            "import threading, time\n"
            "data = bytearray(30 * 1024 * 1024)\n"
            "time.sleep(9999)\n"
        )
        # Run detached so it persists
        try:
            ctr.exec_run(["python3", "-c", code], detach=True)
            return True
        except Exception as e:
            log.warning("Stage 1 injection failed: %s", e)
            return False

    def stage2_pre_failure(self) -> bool:
        """Allocate ~80 MB cumulative — pre_failure window will open."""
        ctr = self._find_container()
        if ctr is None:
            return False
        log.info("[INJECTOR] Stage 2 — pre-failure ramp (80 MB)")
        code = (
            "import time\n"
            "data = bytearray(80 * 1024 * 1024)\n"
            "time.sleep(9999)\n"
        )
        try:
            ctr.exec_run(["python3", "-c", code], detach=True)
            return True
        except Exception as e:
            log.warning("Stage 2 injection failed: %s", e)
            return False

    def stage3_active_failure(self) -> str:
        """
        Allocate ~150 MB — register failure start, return scenario_id.
        This is the moment failure=1 begins.
        """
        ctr = self._find_container()
        if ctr is None:
            return ""

        # Register failure BEFORE allocating so timestamp is accurate
        sid = self._registry.register_failure_start(
            service_name=INJECT_SERVICE,
            failure_type="memory_leak",
        )
        self._scenario_id = sid
        log.info("[INJECTOR] Stage 3 — ACTIVE FAILURE starts (150 MB) scenario=%s", sid)

        code = (
            "import time\n"
            "data = bytearray(150 * 1024 * 1024)\n"
            "time.sleep(9999)\n"
        )
        try:
            ctr.exec_run(["python3", "-c", code], detach=True)
        except Exception as e:
            log.warning("Stage 3 allocation failed: %s", e)

        return sid

    def stage4_peak(self) -> bool:
        """Allocate ~200 MB — peak of injection."""
        ctr = self._find_container()
        if ctr is None:
            return False
        log.info("[INJECTOR] Stage 4 — peak failure (200 MB)")
        code = (
            "import time\n"
            "data = bytearray(200 * 1024 * 1024)\n"
            "time.sleep(9999)\n"
        )
        try:
            ctr.exec_run(["python3", "-c", code], detach=True)
            return True
        except Exception as e:
            log.warning("Stage 4 injection failed: %s", e)
            return False

    def recover(self) -> None:
        """Restart the container to clear all allocations."""
        ctr = self._find_container()
        if self._scenario_id:
            self._registry.register_failure_end(self._scenario_id)
            log.info("[INJECTOR] Registered failure end for scenario=%s", self._scenario_id)

        if ctr is None:
            return
        try:
            log.info("[INJECTOR] Restarting %s for recovery", INJECT_SERVICE)
            ctr.restart(timeout=10)
        except Exception as e:
            log.warning("Container restart failed: %s", e)


# ── Dataset Builder ────────────────────────────────────────────────────────────

class DatasetBuilder:
    """
    Saves the four tables as Parquet + CSV and writes the collection summary JSON.
    """

    def __init__(self, output_dir: Path) -> None:
        self._dir = output_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        metrics: pd.DataFrame,
        logs: pd.DataFrame,
        traces: pd.DataFrame,
        log_agg: pd.DataFrame,
        summary: Dict,
    ) -> None:
        log.info("Saving dataset tables to %s", self._dir)

        tables = {
            "demo_metrics":        metrics,
            "demo_logs":           logs,
            "demo_traces":         traces,
            "demo_log_aggregates": log_agg,
        }

        for name, df in tables.items():
            if df.empty:
                log.warning("Table '%s' is EMPTY — skipping", name)
                continue
            parquet_path = self._dir / f"{name}.parquet"
            csv_path     = self._dir / f"{name}.csv"
            df.to_parquet(parquet_path, index=False, engine="pyarrow")
            df.to_csv(csv_path, index=False)
            log.info("  ✓ %s  (%d rows)", parquet_path.name, len(df))

        # Summary JSON
        summary_path = self._dir / "demo_collection_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        log.info("  ✓ %s", summary_path.name)


# ── Main collection loop ───────────────────────────────────────────────────────

def run_collection() -> None:
    log.info("=" * 65)
    log.info("  AI Observability — Demo Dataset Collection")
    log.info("  Total run: ~%d seconds (~%.1f minutes)", TOTAL_RUN_S, TOTAL_RUN_S / 60)
    log.info("=" * 65)

    # ── Connect to Docker ─────────────────────────────────────────────────────
    try:
        docker_client = docker.from_env()
        docker_client.ping()
        log.info("Docker connection OK")
    except Exception as e:
        log.error("Cannot connect to Docker: %s", e)
        log.error("Make sure Docker is running and you have permission to the socket.")
        sys.exit(1)

    # ── Initialise components ─────────────────────────────────────────────────
    registry   = FailureEventRegistry()
    drain_p    = Drain3Parser()
    metrics_p  = MetricsPoller(docker_client)
    log_s      = LogStreamer(drain_p)
    jaeger_p   = JaegerPoller()
    injector   = FailureInjector(docker_client, registry)
    builder    = DatasetBuilder(OUTPUT_DIR)

    # ── Collection state ──────────────────────────────────────────────────────
    collection_start = utcnow()
    log_fetch_start  = collection_start   # rolling cursor for Loki queries
    injection_done   = False
    recovery_done    = False

    # Phase timestamps (elapsed seconds from collection_start)
    phase_normal_end   = collection_start + timedelta(seconds=NORMAL_PHASE_S)
    phase_pre_end      = phase_normal_end  + timedelta(seconds=PRE_FAIL_PHASE_S)
    phase_active_end   = phase_pre_end     + timedelta(seconds=ACTIVE_FAIL_S)
    phase_total_end    = phase_active_end  + timedelta(seconds=RECOVERY_S)

    log.info("Schedule:")
    log.info("  Normal phase ends    : %s", iso(phase_normal_end))
    log.info("  Active failure begins: %s", iso(phase_pre_end))
    log.info("  Recovery starts      : %s", iso(phase_active_end))
    log.info("  Collection ends      : %s", iso(phase_total_end))
    log.info("")

    stage1_done = False
    stage2_done = False
    stage3_done = False
    stage4_done = False

    # ── Main polling loop ─────────────────────────────────────────────────────
    tick = 0
    total_ticks = int(TOTAL_RUN_S / POLL_INTERVAL_S) + 2

    with tqdm(total=total_ticks, desc="Collecting", unit="tick") as pbar:
        while True:
            now = utcnow()
            elapsed = (now - collection_start).total_seconds()

            if now >= phase_total_end:
                log.info("Collection window complete.")
                break

            # ── Failure injection schedule ────────────────────────────────────
            if elapsed >= NORMAL_PHASE_S and not stage1_done:
                injector.stage1_ramp()
                stage1_done = True

            pre_fail_start_elapsed = NORMAL_PHASE_S + (PRE_FAIL_PHASE_S * 0.3)
            if elapsed >= pre_fail_start_elapsed and not stage2_done:
                injector.stage2_pre_failure()
                stage2_done = True

            if elapsed >= (NORMAL_PHASE_S + PRE_FAIL_PHASE_S) and not stage3_done:
                injector.stage3_active_failure()
                stage3_done = True

            active_midpoint = NORMAL_PHASE_S + PRE_FAIL_PHASE_S + ACTIVE_FAIL_S * 0.4
            if elapsed >= active_midpoint and not stage4_done:
                injector.stage4_peak()
                stage4_done = True

            if elapsed >= (NORMAL_PHASE_S + PRE_FAIL_PHASE_S + ACTIVE_FAIL_S) and not recovery_done:
                injector.recover()
                recovery_done = True
                time.sleep(5)   # brief pause for container restart

            # ── Metrics poll ──────────────────────────────────────────────────
            snap_time = utcnow()
            n_sampled = metrics_p.poll_once(snap_time)
            log.debug("Tick %d: sampled %d containers", tick, n_sampled)

            # ── Log fetch (every tick) ────────────────────────────────────────
            fetch_end  = utcnow()
            n_logs = log_s.fetch_range(log_fetch_start, fetch_end, limit=500)
            log_fetch_start = fetch_end
            if n_logs > 0:
                log.debug("Fetched %d log lines from Loki", n_logs)

            tick += 1
            pbar.update(1)
            pbar.set_postfix({"containers": n_sampled, "logs": len(log_s.rows)})

            # Sleep until next poll interval
            elapsed_this_tick = (utcnow() - snap_time).total_seconds()
            sleep_time = max(0, POLL_INTERVAL_S - elapsed_this_tick)
            time.sleep(sleep_time)

    # ── Fetch Jaeger traces for the full window ───────────────────────────────
    log.info("Fetching Jaeger traces for collection window ...")
    total_spans = 0
    jaeger_svc_names = [
        "frontend",
        "checkoutservice",
        "cartservice",
        "productcatalogservice",
        "currencyservice",
        "recommendationservice",
        "paymentservice",
        "emailservice",
    ]
    for svc in jaeger_svc_names:
        n = jaeger_p.fetch_service_traces(svc, collection_start, utcnow(), limit=500)
        total_spans += n
        if n > 0:
            log.info("  %s: %d spans", svc, n)
    log.info("Total spans collected: %d", total_spans)

    # ── Build DataFrames ──────────────────────────────────────────────────────
    log.info("Building DataFrames ...")
    metrics_df = metrics_p.build_dataframe()
    logs_df    = log_s.build_dataframe()
    traces_df  = jaeger_p.build_dataframe()

    log.info("  metrics rows  : %d", len(metrics_df))
    log.info("  logs rows     : %d", len(logs_df))
    log.info("  traces rows   : %d", len(traces_df))

    # ── Stamp labels ──────────────────────────────────────────────────────────
    log.info("Stamping labels from FailureEventRegistry ...")

    if not metrics_df.empty:
        metrics_df = registry.compute_labels_for_dataframe(metrics_df)

    if not logs_df.empty:
        logs_df = registry.compute_labels_for_dataframe(
            logs_df, ts_col="log_timestamp", svc_col="service_name"
        )

    if not traces_df.empty:
        traces_df = registry.compute_labels_for_dataframe(
            traces_df, ts_col="start_time", svc_col="service_name"
        )

    # ── Build log aggregates ──────────────────────────────────────────────────
    log_agg_df = pd.DataFrame()
    if not logs_df.empty:
        log.info("Building log aggregates ...")
        aggregator = LogAggregator()
        log_agg_df = aggregator.build(logs_df)
        log.info("  log_aggregates rows: %d", len(log_agg_df))

    # ── Validate labels ───────────────────────────────────────────────────────
    log.info("Validating labels ...")
    for name, df in [("metrics", metrics_df), ("logs", logs_df),
                     ("traces", traces_df), ("log_aggregates", log_agg_df)]:
        if df.empty:
            log.warning("  %s: EMPTY — skipping validation", name)
            continue
        report = validate_labels(df, strict=False)
        if report["passed"]:
            stats = report["stats"]
            log.info(
                "  ✓ %s: %d rows | failure=%d | pre_failure=%d | future_failure=%d | normal=%d",
                name,
                stats["total_rows"],
                stats["failure_rows"],
                stats["pre_failure_rows"],
                stats["future_failure_rows"],
                stats["normal_rows"],
            )
        else:
            log.error("  ✗ %s VALIDATION FAILED:", name)
            for v in report["violations"]:
                log.error("    %s", v)

    # ── Print label distribution ──────────────────────────────────────────────
    if not metrics_df.empty:
        log.info("")
        log.info("=== Metrics label distribution (all services) ===")
        dist = (
            metrics_df.groupby(["failure", "pre_failure", "future_failure", "failure_type"])
            .size()
            .reset_index(name="count")
        )
        log.info("\n%s", dist.to_string(index=False))

    # ── Build summary ─────────────────────────────────────────────────────────
    summary = {
        "collection_start":  iso(collection_start),
        "collection_end":    iso(utcnow()),
        "duration_seconds":  int((utcnow() - collection_start).total_seconds()),
        "poll_interval_s":   POLL_INTERVAL_S,
        "inject_service":    INJECT_SERVICE,
        "failure_registry":  registry.get_summary(),
        "table_row_counts": {
            "metrics":        len(metrics_df),
            "logs":           len(logs_df),
            "traces":         len(traces_df),
            "log_aggregates": len(log_agg_df),
        },
        "services_monitored": ALL_MONITORED,
        "drain3_available":   DRAIN3_AVAILABLE,
    }

    if not metrics_df.empty:
        v = validate_labels(metrics_df, strict=False)
        summary["label_stats_metrics"] = v["stats"]

    # ── Save everything ───────────────────────────────────────────────────────
    builder.save(metrics_df, logs_df, traces_df, log_agg_df, summary)

    log.info("")
    log.info("=" * 65)
    log.info("  Collection complete!  Output → %s", OUTPUT_DIR)
    log.info("=" * 65)

    # ── Print quick inspection ────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("DATASET SNAPSHOT")
    print("=" * 65)
    if not metrics_df.empty:
        print("\nmetrics.parquet — head(3):")
        cols = ["timestamp", "service_name", "cpu_usage_percent",
                "memory_usage_percent", "failure", "pre_failure",
                "future_failure", "failure_type"]
        avail = [c for c in cols if c in metrics_df.columns]
        print(metrics_df[avail].head(3).to_string(index=False))

    print(f"\nTotal rows — metrics: {len(metrics_df)} | logs: {len(logs_df)} "
          f"| traces: {len(traces_df)} | log_agg: {len(log_agg_df)}")
    if not metrics_df.empty and "failure" in metrics_df.columns:
        print(f"Failure rows (metrics): {(metrics_df['failure']==1).sum()}")
        print(f"Pre-failure rows      : {(metrics_df['pre_failure']==1).sum()}")
        print(f"Future-failure rows   : {(metrics_df['future_failure']==1).sum()}")


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_collection()
