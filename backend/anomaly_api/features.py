"""
Stage 2: Rich feature extraction from a window of Observations.

Takes a List[Observation] for a single service and produces a flat
feature dict with statistical aggregates, trend indicators, composite
pressure metrics, and human-readable anomaly flags.
"""

from typing import Dict, List

import numpy as np

from anomaly_api.ingestion import Observation, WINDOW_SIZE

# Raw metrics to compute full statistical suite for
RAW_METRICS = [
    "cpu_percent",
    "mem_percent",
    "net_rx_mbps",
    "net_tx_mbps",
    "block_read_mbps",
    "block_write_mbps",
    "error_rate",
    "warn_rate",
    "log_count",
    "exception_count",
    "template_entropy",
    "log_volume_per_sec",
]


def extract_features(service: str, window: List[Observation]) -> Dict:
    """
    Extracts a rich feature dict from a window of observations.
    Returns empty dict if window is empty.
    """
    if not window:
        return {}

    n = len(window)
    timestamps = np.array([obs.timestamp for obs in window], dtype=float)
    first_ts = timestamps[0]
    last_ts = timestamps[-1]
    window_duration_s = float(last_ts - first_ts) if n > 1 else 0.0

    # Normalized time axis [0, 1] for slope computation
    if window_duration_s > 0:
        norm_t = (timestamps - first_ts) / window_duration_s
    else:
        norm_t = np.linspace(0.0, 1.0, n)

    features: Dict = {}

    for metric in RAW_METRICS:
        values = np.array([getattr(obs, metric, 0.0) for obs in window], dtype=float)

        mean_val = float(np.mean(values))
        std_val = float(np.std(values))
        min_val = float(np.min(values))
        max_val = float(np.max(values))
        p95_val = float(np.percentile(values, 95))

        # Rate of change: (last - first) / duration
        if window_duration_s > 0 and n > 1:
            roc_val = float((values[-1] - values[0]) / window_duration_s)
        else:
            roc_val = 0.0

        # Linear slope via polyfit on normalized time
        if n >= 2:
            try:
                slope_val = float(np.polyfit(norm_t, values, 1)[0])
            except Exception:
                slope_val = 0.0
        else:
            slope_val = 0.0

        features[f"{metric}_mean"] = mean_val
        features[f"{metric}_std"] = std_val
        features[f"{metric}_min"] = min_val
        features[f"{metric}_max"] = max_val
        features[f"{metric}_p95"] = p95_val
        features[f"{metric}_roc"] = roc_val
        features[f"{metric}_slope"] = slope_val

    # ── Composite features ──────────────────────────────────────────────────

    cpu_mean = features["cpu_percent_mean"]
    cpu_std = features["cpu_percent_std"]
    mem_mean = features["mem_percent_mean"]
    mem_std = features["mem_percent_std"]

    # cpu_pressure: penalizes high variance
    features["cpu_pressure"] = cpu_mean * (1.0 + cpu_std / max(cpu_mean, 1.0))

    # memory_pressure: penalizes high variance
    features["memory_pressure"] = mem_mean * (1.0 + mem_std / max(mem_mean, 1.0))

    # network_pressure: total throughput
    features["network_pressure"] = (
        features["net_rx_mbps_mean"] + features["net_tx_mbps_mean"]
    )

    # error_momentum: is error rate rising?
    features["error_momentum"] = (
        features["error_rate_slope"] * window_duration_s
    )

    # log_anomaly_score: weighted composite of error signals
    features["log_anomaly_score"] = (
        features["error_rate_mean"] * 3.0
        + features["warn_rate_mean"]
        + features["exception_count_mean"] * 2.0
    ) / 6.0

    # io_pressure: total block I/O
    features["io_pressure"] = (
        features["block_read_mbps_mean"] + features["block_write_mbps_mean"]
    )

    # Window metadata
    features["window_filled_fraction"] = n / WINDOW_SIZE
    features["window_duration_s"] = window_duration_s

    # ── Feature flags: human-readable anomaly indicators ────────────────────

    flags: List[str] = []

    if features["cpu_percent_max"] > 50:
        flags.append("cpu_spike")
    if features["cpu_percent_slope"] > 2.0:
        flags.append("cpu_trending_up")
    if features["mem_percent_mean"] > 80:
        flags.append("memory_high")
    if features["mem_percent_slope"] > 1.0:
        flags.append("memory_trending_up")
    if features["error_rate_mean"] > 0.10:           # >10% of logs are errors
        flags.append("error_rate_high")
    if features["error_rate_slope"] > 0.003:          # error rate actively climbing
        flags.append("error_rate_rising")
    if features["exception_count_mean"] > 0.5:        # avg >0.5 exceptions per sample
        flags.append("exceptions_detected")
    if features["network_pressure"] < 0.0002 and n > 8:  # truly zero traffic (<200 B/s)
        flags.append("network_drop")
    if features["log_count_mean"] > 300:              # unusually high log volume
        flags.append("log_volume_spike")
    if features["io_pressure"] > 10:
        flags.append("io_high")

    features["feature_flags"] = flags

    return features
