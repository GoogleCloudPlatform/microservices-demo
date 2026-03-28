"""
Stage 1: Sliding window ingestion pipeline.

Collects data from Docker stats API and Loki, maintains per-service
sliding windows of Observations for downstream feature extraction.
"""

from dataclasses import dataclass, field
from collections import deque
from typing import Dict, List, Optional
import time
import json
import math
import logging
import threading
import os
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import requests

logger = logging.getLogger(__name__)

WINDOW_SIZE = 20          # observations per service
DOCKER_POLL_INTERVAL = 5.0   # seconds
LOKI_POLL_INTERVAL = 10.0    # seconds
TRACE_POLL_INTERVAL = 15.0   # seconds
LOKI_URL = os.getenv("AEGIS_LOKI_URL", "http://localhost:3100")
JAEGER_URL = os.getenv("AEGIS_JAEGER_URL", "http://localhost:16686")
PROMETHEUS_URL = os.getenv("AEGIS_PROMETHEUS_URL", "http://localhost:9090")
ORCHESTRATOR = os.getenv("AEGIS_ORCHESTRATOR", "auto").strip().lower()
K8S_NAMESPACE = os.getenv("AEGIS_K8S_NAMESPACE", "default")

ALL_SERVICES = [
    "frontend", "productcatalogservice", "cartservice", "recommendationservice",
    "checkoutservice", "paymentservice", "shippingservice", "emailservice",
    "currencyservice", "adservice", "redis-cart",
]


@dataclass
class Observation:
    """One data point for one service at one moment."""
    timestamp: float
    service: str

    # Docker stats (rates)
    cpu_percent: float = 0.0
    mem_percent: float = 0.0
    mem_bytes: float = 0.0
    mem_limit_bytes: float = 0.0
    net_rx_mbps: float = 0.0    # MB/s computed from delta
    net_tx_mbps: float = 0.0
    block_read_mbps: float = 0.0
    block_write_mbps: float = 0.0

    # Loki log features (window aggregated over last LOKI_POLL_INTERVAL seconds)
    log_count: int = 0
    error_count: int = 0
    warn_count: int = 0
    info_count: int = 0
    error_rate: float = 0.0     # error_count / log_count
    warn_rate: float = 0.0
    exception_count: int = 0    # lines containing "exception" or "Exception"
    timeout_count: int = 0
    template_entropy: float = 0.0   # Shannon entropy of message length distribution
    log_volume_per_sec: float = 0.0
    unique_templates: int = 0
    new_templates_seen: int = 0
    oom_mention_count: int = 0
    avg_message_length: float = 0.0
    log_volume_change_pct: float = 0.0

    # Jaeger trace features
    trace_count: int = 0
    trace_error_count: int = 0
    trace_duration_mean: float = 0.0


class SlidingWindowState:
    """Per-service deque of last WINDOW_SIZE Observations."""

    def __init__(self, window_size: int = WINDOW_SIZE):
        self.window_size = window_size
        self.windows: Dict[str, deque] = {
            svc: deque(maxlen=window_size) for svc in ALL_SERVICES
        }
        self._lock = threading.Lock()

    def push(self, obs: Observation):
        with self._lock:
            self.windows[obs.service].append(obs)

    def get_window(self, service: str) -> List[Observation]:
        with self._lock:
            return list(self.windows[service])

    def get_latest(self, service: str) -> Optional[Observation]:
        with self._lock:
            w = self.windows[service]
            return w[-1] if w else None

    def is_filled(self, service: str) -> bool:
        with self._lock:
            return len(self.windows[service]) >= self.window_size

    def fill_fraction(self, service: str) -> float:
        with self._lock:
            return len(self.windows[service]) / self.window_size


class DockerStatsCollector:
    """Collects Docker container stats and computes rates."""

    def __init__(self):
        self._client = None
        self._available = False
        self._prev_cumulative: Dict[str, Dict] = {}
        self._prev_poll_time: float = 0.0
        self._init_docker()

    def _init_docker(self):
        try:
            import docker as docker_sdk
            self._client = docker_sdk.from_env()
            self._client.ping()
            self._available = True
            logger.info("DockerStatsCollector: Docker available")
        except Exception as e:
            self._available = False
            logger.warning(f"DockerStatsCollector: Docker not available: {e}")

    def _fetch_container_stats(self, container, svc: str, elapsed: float) -> Optional[Dict]:
        """Fetch stats for a single container and return parsed metrics."""
        try:
            raw = container.stats(stream=False)

            # CPU %
            cpu_delta = (
                raw["cpu_stats"]["cpu_usage"]["total_usage"]
                - raw["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            sys_delta = (
                raw["cpu_stats"].get("system_cpu_usage", 0)
                - raw["precpu_stats"].get("system_cpu_usage", 0)
            )
            n_cpus = raw["cpu_stats"].get("online_cpus") or len(
                raw["cpu_stats"]["cpu_usage"].get("percpu_usage", [1])
            )
            cpu_pct = (cpu_delta / sys_delta) * n_cpus * 100.0 if sys_delta > 0 else 0.0

            # Memory
            mem_usage = raw["memory_stats"].get("usage", 0)
            mem_limit = raw["memory_stats"].get("limit", 1)
            mem_pct = (mem_usage / mem_limit) * 100.0 if mem_limit > 0 else 0.0

            # Network cumulative bytes
            nets = raw.get("networks", {})
            cum_rx = sum(v.get("rx_bytes", 0) for v in nets.values())
            cum_tx = sum(v.get("tx_bytes", 0) for v in nets.values())

            # Block I/O cumulative bytes
            bio = raw.get("blkio_stats", {}).get("io_service_bytes_recursive") or []
            cum_br = sum(e.get("value", 0) for e in bio if e.get("op", "").lower() == "read")
            cum_bw = sum(e.get("value", 0) for e in bio if e.get("op", "").lower() == "write")

            new_cum = {
                "net_rx": cum_rx, "net_tx": cum_tx,
                "block_r": cum_br, "block_w": cum_bw,
            }

            # Compute rates
            prev = self._prev_cumulative.get(svc, {})
            if prev and elapsed > 0:
                net_rx_mbs = max(0.0, (cum_rx - prev["net_rx"]) / elapsed / 1e6)
                net_tx_mbs = max(0.0, (cum_tx - prev["net_tx"]) / elapsed / 1e6)
                block_r_mbs = max(0.0, (cum_br - prev["block_r"]) / elapsed / 1e6)
                block_w_mbs = max(0.0, (cum_bw - prev["block_w"]) / elapsed / 1e6)
            else:
                net_rx_mbs = 0.0
                net_tx_mbs = 0.0
                block_r_mbs = 0.0
                block_w_mbs = 0.0

            return {
                "svc": svc,
                "cpu_percent": round(min(cpu_pct, 100.0), 2),
                "mem_percent": round(min(mem_pct, 100.0), 2),
                "mem_bytes": float(mem_usage),
                "mem_limit_bytes": float(mem_limit),
                "net_rx_mbps": round(net_rx_mbs, 4),
                "net_tx_mbps": round(net_tx_mbs, 4),
                "block_read_mbps": round(block_r_mbs, 4),
                "block_write_mbps": round(block_w_mbs, 4),
                "_new_cum": new_cum,
            }
        except Exception as e:
            logger.debug(f"DockerStatsCollector: error fetching stats for {svc}: {e}")
            return None

    def poll(self) -> Dict[str, Dict]:
        """
        Poll stats for all running containers simultaneously.
        Returns Dict[service_name, metrics_dict].
        """
        if not self._available:
            self._init_docker()
            if not self._available:
                return {}

        try:
            now = time.time()
            elapsed = now - self._prev_poll_time if self._prev_poll_time > 0 else 8.0
            self._prev_poll_time = now

            containers = self._client.containers.list()

            # Map container -> service name
            container_svc_pairs = []
            for container in containers:
                raw_name = container.name
                svc = None
                for s in ALL_SERVICES:
                    if s in raw_name:
                        svc = s
                        break
                if svc is not None:
                    container_svc_pairs.append((container, svc))

            stats_map: Dict[str, Dict] = {}
            new_cumulative: Dict[str, Dict] = {}

            # Fetch stats concurrently
            with ThreadPoolExecutor(max_workers=16) as executor:
                futures = {
                    executor.submit(self._fetch_container_stats, container, svc, elapsed): svc
                    for container, svc in container_svc_pairs
                }
                for future in as_completed(futures):
                    result = future.result()
                    if result is not None:
                        svc = result["svc"]
                        new_cumulative[svc] = result.pop("_new_cum")
                        result.pop("svc")
                        stats_map[svc] = result

            self._prev_cumulative = new_cumulative
            return stats_map

        except Exception as e:
            logger.warning(f"DockerStatsCollector.poll error: {e}")
            self._available = False
            return {}


class PrometheusStatsCollector:
    """Collects per-pod resource metrics from Prometheus for Kubernetes workloads."""

    def __init__(self, base_url: str = PROMETHEUS_URL, namespace: str = K8S_NAMESPACE):
        self.base_url = base_url.rstrip("/")
        self.namespace = namespace

    def _query(self, promql: str) -> List[Dict]:
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/query",
                params={"query": promql},
                timeout=3.0,
            )
            response.raise_for_status()
            payload = response.json()
            if payload.get("status") != "success":
                return []
            return payload.get("data", {}).get("result", []) or []
        except Exception as exc:
            logger.debug("PrometheusStatsCollector query failed: %s", exc)
            return []

    @staticmethod
    def _service_from_pod_name(pod_name: str) -> Optional[str]:
        for service in ALL_SERVICES:
            if pod_name == service or pod_name.startswith(f"{service}-"):
                return service
        return None

    @staticmethod
    def _sample_value(series: Dict) -> float:
        value = series.get("value", [None, "0"])
        try:
            return float(value[1])
        except (TypeError, ValueError, IndexError):
            return 0.0

    def poll(self) -> Dict[str, Dict]:
        query_map = {
            "cpu_percent": (
                f'sum by (container_label_io_kubernetes_pod_name) ('
                f'rate(container_cpu_usage_seconds_total{{'
                f'container_label_io_kubernetes_pod_namespace="{self.namespace}",'
                'image!=""}[2m])) * 100'
            ),
            "mem_bytes": (
                f'sum by (container_label_io_kubernetes_pod_name) ('
                f'container_memory_working_set_bytes{{'
                f'container_label_io_kubernetes_pod_namespace="{self.namespace}",'
                'image!=""})'
            ),
            "mem_limit_bytes": (
                f'sum by (container_label_io_kubernetes_pod_name) ('
                f'container_spec_memory_limit_bytes{{'
                f'container_label_io_kubernetes_pod_namespace="{self.namespace}",'
                'image!=""})'
            ),
            "net_rx_mbps": (
                f'sum by (container_label_io_kubernetes_pod_name) ('
                f'rate(container_network_receive_bytes_total{{'
                f'container_label_io_kubernetes_pod_namespace="{self.namespace}"}}[2m])) / 1e6'
            ),
            "net_tx_mbps": (
                f'sum by (container_label_io_kubernetes_pod_name) ('
                f'rate(container_network_transmit_bytes_total{{'
                f'container_label_io_kubernetes_pod_namespace="{self.namespace}"}}[2m])) / 1e6'
            ),
            "block_read_mbps": (
                f'sum by (container_label_io_kubernetes_pod_name) ('
                f'rate(container_fs_reads_bytes_total{{'
                f'container_label_io_kubernetes_pod_namespace="{self.namespace}",'
                'image!=""}[2m])) / 1e6'
            ),
            "block_write_mbps": (
                f'sum by (container_label_io_kubernetes_pod_name) ('
                f'rate(container_fs_writes_bytes_total{{'
                f'container_label_io_kubernetes_pod_namespace="{self.namespace}",'
                'image!=""}[2m])) / 1e6'
            ),
        }

        stats_map: Dict[str, Dict] = {service: {} for service in ALL_SERVICES}
        for field, query in query_map.items():
            for series in self._query(query):
                pod_name = series.get("metric", {}).get("container_label_io_kubernetes_pod_name", "")
                service = self._service_from_pod_name(pod_name)
                if service is None:
                    continue
                stats_map.setdefault(service, {})[field] = self._sample_value(series)

        for service, metrics in stats_map.items():
            mem_bytes = float(metrics.get("mem_bytes", 0.0))
            mem_limit_bytes = float(metrics.get("mem_limit_bytes", 0.0))
            metrics.setdefault("cpu_percent", 0.0)
            metrics.setdefault("mem_bytes", mem_bytes)
            metrics.setdefault("mem_limit_bytes", mem_limit_bytes)
            metrics.setdefault("mem_percent", (mem_bytes / mem_limit_bytes * 100.0) if mem_limit_bytes > 0 else 0.0)
            metrics.setdefault("net_rx_mbps", 0.0)
            metrics.setdefault("net_tx_mbps", 0.0)
            metrics.setdefault("block_read_mbps", 0.0)
            metrics.setdefault("block_write_mbps", 0.0)
        return stats_map


class LokiCollector:
    """Collects log features from Loki for all services."""

    def __init__(self) -> None:
        self._seen_templates_global = set()
        self._prev_totals: Dict[str, int] = {}

    def _compute_template_entropy(self, messages: List[str]) -> float:
        """
        Shannon entropy of first-30-char message templates as a proxy
        for log pattern diversity.
        """
        if not messages:
            return 0.0
        templates: Dict[str, int] = {}
        for msg in messages:
            tmpl = msg[:30] if len(msg) >= 30 else msg
            templates[tmpl] = templates.get(tmpl, 0) + 1
        total = sum(templates.values())
        entropy = 0.0
        for count in templates.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        return round(entropy, 4)

    def _query_service(self, svc: str, start_ns: int, end_ns: int) -> Dict:
        """Query Loki for a single service and return parsed log features."""
        empty = {
            "log_count": 0,
            "error_count": 0,
            "warn_count": 0,
            "info_count": 0,
            "exception_count": 0,
            "timeout_count": 0,
            "oom_mention_count": 0,
            "template_entropy": 0.0,
            "unique_templates": 0,
            "new_templates_seen": 0,
            "avg_message_length": 0.0,
            "log_volume_change_pct": 0.0,
            "recent_messages": [],
        }
        try:
            url = (
                f"{LOKI_URL}/loki/api/v1/query_range"
                f'?query={{compose_service="{svc}"}}'
                f"&limit=200&start={start_ns}&end={end_ns}&direction=forward"
            )
            resp = requests.get(url, timeout=5)
            if resp.status_code in (400, 404):
                return empty
            if resp.status_code != 200:
                return empty

            data = resp.json()
            result_streams = data.get("data", {}).get("result", [])

            log_count = 0
            error_count = 0
            warn_count = 0
            info_count = 0
            exception_count = 0
            timeout_count = 0
            oom_mention_count = 0
            messages = []
            templates = []
            message_lengths = []

            for stream in result_streams:
                values = stream.get("values", [])
                for ts_ns_str, line in values:
                    log_count += 1

                    # Skip known infrastructure noise lines (OTLP/trace exporter failures)
                    INFRA_NOISE = (
                        "traces export", "exporter export", "otlp", "spans export",
                        "grpc: addrconn", "failed to report", "report to backend",
                    )
                    if any(noise in line.lower() for noise in INFRA_NOISE):
                        log_count -= 1  # don't count it at all
                        continue

                    # Try JSON parse for structured logs
                    msg = line
                    level = ""
                    try:
                        parsed = json.loads(line)
                        msg = str(parsed.get("message", parsed.get("msg", line)))
                        level = str(parsed.get("level", parsed.get("severity", ""))).upper()
                    except (json.JSONDecodeError, Exception):
                        # Plain text log — detect level only from explicit prefix keywords
                        # to avoid false-positives from lines that happen to contain "error"
                        stripped = line.strip()
                        if stripped.startswith(("ERROR ", "CRITICAL ", "FATAL ")):
                            level = "ERROR"
                        elif stripped.startswith(("WARN ", "WARNING ")):
                            level = "WARN"
                        elif stripped.startswith("INFO "):
                            level = "INFO"
                        # For Go stdlib logs like "2026/03/28 10:47 some error occurred"
                        # only flag if the word "error" appears near the start
                        elif len(stripped) > 20 and "error" in stripped[:40].lower():
                            level = "ERROR"

                    # Count by level
                    if level in ("ERROR", "CRITICAL", "FATAL"):
                        error_count += 1
                    elif level in ("WARN", "WARNING"):
                        warn_count += 1
                    elif level == "INFO":
                        info_count += 1

                    # Count exceptions and timeouts
                    msg_lower = msg.lower()
                    line_lower = line.lower()
                    if "exception" in msg_lower or "traceback" in msg_lower or "exception" in line_lower:
                        exception_count += 1
                    if "timeout" in msg_lower or "timed out" in msg_lower or "timeout" in line_lower:
                        timeout_count += 1
                    if "out of memory" in msg_lower or "oom" in msg_lower or "killed" in msg_lower:
                        oom_mention_count += 1

                    messages.append(msg)
                    templates.append((msg[:48] if len(msg) >= 48 else msg).strip())
                    message_lengths.append(len(msg))

            template_entropy = self._compute_template_entropy(messages)
            unique_templates = len(set(templates))
            new_templates_seen = len(set(templates) - self._seen_templates_global)
            self._seen_templates_global.update(templates)
            avg_message_length = float(np.mean(message_lengths)) if message_lengths else 0.0
            prev_total = self._prev_totals.get(svc, 0)
            log_volume_change_pct = ((log_count / prev_total - 1.0) * 100.0) if prev_total > 0 else 0.0
            self._prev_totals[svc] = log_count

            # Keep last 5 messages for display
            recent_messages = messages[-5:] if messages else []

            return {
                "log_count": log_count,
                "error_count": error_count,
                "warn_count": warn_count,
                "info_count": info_count,
                "exception_count": exception_count,
                "timeout_count": timeout_count,
                "oom_mention_count": oom_mention_count,
                "template_entropy": template_entropy,
                "unique_templates": unique_templates,
                "new_templates_seen": new_templates_seen,
                "avg_message_length": round(avg_message_length, 2),
                "log_volume_change_pct": round(log_volume_change_pct, 4),
                "recent_messages": recent_messages,
            }

        except requests.exceptions.RequestException as e:
            logger.debug(f"LokiCollector: network error for {svc}: {e}")
            return empty
        except Exception as e:
            logger.debug(f"LokiCollector: unexpected error for {svc}: {e}")
            return empty

    def poll(self, lookback_seconds: float = 15.0) -> Dict[str, Dict]:
        """
        Query Loki for all services over the last lookback_seconds window.
        Returns Dict[service_name, log_features_dict].
        """
        end_ns = int(time.time() * 1e9)
        start_ns = int((time.time() - lookback_seconds) * 1e9)

        results: Dict[str, Dict] = {}
        with ThreadPoolExecutor(max_workers=len(ALL_SERVICES)) as executor:
            futures = {
                executor.submit(self._query_service, svc, start_ns, end_ns): svc
                for svc in ALL_SERVICES
            }
            for future in as_completed(futures):
                svc = futures[future]
                try:
                    results[svc] = future.result()
                except Exception as e:
                    logger.debug(f"LokiCollector: future error for {svc}: {e}")
                    results[svc] = {
                        "log_count": 0, "error_count": 0, "warn_count": 0,
                        "info_count": 0, "exception_count": 0, "timeout_count": 0,
                        "template_entropy": 0.0, "recent_messages": [],
                    }

        return results


class JaegerCollector:
    """Collects short-range trace aggregates from Jaeger."""

    def _query_service(self, svc: str, start_us: int, end_us: int) -> Dict:
        empty = {
            "trace_count": 0,
            "trace_error_count": 0,
            "trace_duration_mean": 0.0,
        }
        try:
            resp = requests.get(
                f"{JAEGER_URL}/api/traces",
                params={
                    "service": svc,
                    "start": str(start_us),
                    "end": str(end_us),
                    "limit": "50",
                },
                timeout=8,
            )
            if resp.status_code in (400, 404):
                return empty
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return empty

        span_count = 0
        error_count = 0
        durations = []

        for trace in data.get("data", []):
            for span in trace.get("spans", []):
                proc_id = span.get("processID", "")
                process = (trace.get("processes") or {}).get(proc_id, {})
                service_name = process.get("serviceName", svc)
                if service_name != svc:
                    continue
                span_count += 1
                duration_ms = float(span.get("duration", 0) or 0) / 1000.0
                durations.append(duration_ms)
                tags = {tag.get("key"): tag.get("value") for tag in span.get("tags", [])}
                http_status = int(tags.get("http.status_code", 0) or 0)
                otel_status = str(tags.get("otel.status_code", "") or "").upper()
                if otel_status == "ERROR" or http_status >= 500 or bool(tags.get("error", False)):
                    error_count += 1

        return {
            "trace_count": span_count,
            "trace_error_count": error_count,
            "trace_duration_mean": round(float(np.mean(durations)) if durations else 0.0, 4),
        }

    def poll(self, lookback_seconds: float = TRACE_POLL_INTERVAL) -> Dict[str, Dict]:
        end_dt = datetime.now(timezone.utc)
        start_dt = end_dt.timestamp() - lookback_seconds
        end_us = int(end_dt.timestamp() * 1e6)
        start_us = int(start_dt * 1e6)

        results: Dict[str, Dict] = {}
        with ThreadPoolExecutor(max_workers=len(ALL_SERVICES)) as executor:
            futures = {
                executor.submit(self._query_service, svc, start_us, end_us): svc
                for svc in ALL_SERVICES
            }
            for future in as_completed(futures):
                svc = futures[future]
                try:
                    results[svc] = future.result()
                except Exception:
                    results[svc] = {
                        "trace_count": 0,
                        "trace_error_count": 0,
                        "trace_duration_mean": 0.0,
                    }
        return results


class IngestionPipeline:
    """Orchestrates all collectors and feeds the sliding window."""

    def __init__(self, window_state: SlidingWindowState):
        self.window_state = window_state
        if ORCHESTRATOR == "kubernetes":
            self.metrics_collector = PrometheusStatsCollector()
        else:
            self.metrics_collector = DockerStatsCollector()
        self.loki = LokiCollector()
        self.jaeger = JaegerCollector()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_loki_poll = 0.0
        self._last_trace_poll = 0.0
        self._loki_cache: Dict[str, Dict] = {}  # last Loki results per service
        self._trace_cache: Dict[str, Dict] = {}

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info("IngestionPipeline started")

    def stop(self):
        self._running = False
        logger.info("IngestionPipeline stopping")

    def _loop(self):
        while self._running:
            try:
                # Resource stats every poll cycle
                resource_stats = self.metrics_collector.poll()

                # Loki every LOKI_POLL_INTERVAL
                now = time.time()
                if now - self._last_loki_poll >= LOKI_POLL_INTERVAL:
                    try:
                        self._loki_cache = self.loki.poll(lookback_seconds=LOKI_POLL_INTERVAL + 2)
                        self._last_loki_poll = now
                    except Exception as e:
                        logger.warning(f"Loki poll error: {e}")
                if now - self._last_trace_poll >= TRACE_POLL_INTERVAL:
                    try:
                        self._trace_cache = self.jaeger.poll(lookback_seconds=TRACE_POLL_INTERVAL + 2)
                        self._last_trace_poll = now
                    except Exception as e:
                        logger.warning(f"Jaeger poll error: {e}")

                # Build and push one Observation per service
                for svc in ALL_SERVICES:
                    ds = resource_stats.get(svc, {})
                    ls = self._loki_cache.get(svc, {})
                    ts = self._trace_cache.get(svc, {})

                    log_count = ls.get("log_count", 0)
                    error_count = ls.get("error_count", 0)
                    warn_count = ls.get("warn_count", 0)

                    obs = Observation(
                        timestamp=time.time(),
                        service=svc,
                        cpu_percent=ds.get("cpu_percent", 0.0),
                        mem_percent=ds.get("mem_percent", 0.0),
                        mem_bytes=ds.get("mem_bytes", 0.0),
                        mem_limit_bytes=ds.get("mem_limit_bytes", 0.0),
                        net_rx_mbps=ds.get("net_rx_mbps", 0.0),
                        net_tx_mbps=ds.get("net_tx_mbps", 0.0),
                        block_read_mbps=ds.get("block_read_mbps", 0.0),
                        block_write_mbps=ds.get("block_write_mbps", 0.0),
                        log_count=log_count,
                        error_count=error_count,
                        warn_count=warn_count,
                        info_count=ls.get("info_count", 0),
                        error_rate=error_count / max(log_count, 1),
                        warn_rate=warn_count / max(log_count, 1),
                        exception_count=ls.get("exception_count", 0),
                        timeout_count=ls.get("timeout_count", 0),
                        template_entropy=ls.get("template_entropy", 0.0),
                        log_volume_per_sec=log_count / LOKI_POLL_INTERVAL,
                        unique_templates=ls.get("unique_templates", 0),
                        new_templates_seen=ls.get("new_templates_seen", 0),
                        oom_mention_count=ls.get("oom_mention_count", 0),
                        avg_message_length=ls.get("avg_message_length", 0.0),
                        log_volume_change_pct=ls.get("log_volume_change_pct", 0.0),
                        trace_count=ts.get("trace_count", 0),
                        trace_error_count=ts.get("trace_error_count", 0),
                        trace_duration_mean=ts.get("trace_duration_mean", 0.0),
                    )
                    self.window_state.push(obs)

            except Exception as e:
                logger.error(f"Ingestion loop error: {e}")

            time.sleep(DOCKER_POLL_INTERVAL)
