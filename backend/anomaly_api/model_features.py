from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np

from anomaly_api.ingestion import Observation

LSTM_SEQUENCE_WINDOW = 8

SEQUENCE_FEATURES = [
    "cpu_usage_percent",
    "memory_usage_bytes",
    "memory_limit_bytes",
    "memory_usage_percent",
    "network_rx_bytes_per_sec",
    "network_tx_bytes_per_sec",
    "fs_reads_per_sec",
    "fs_writes_per_sec",
    "request_rate",
    "error_rate",
    "p50_latency_ms",
    "p99_latency_ms",
    "active_connections",
    "cpu_trend_5min",
    "memory_trend_5min",
    "error_rate_trend_5min",
    "total_log_lines",
    "error_count",
    "warning_count",
    "info_count",
    "error_rate_logs",
    "warning_rate_logs",
    "unique_templates",
    "template_entropy",
    "new_templates_seen",
    "exception_count",
    "timeout_count",
    "oom_mention_count",
    "avg_message_length",
    "log_volume_change_pct",
    "trace_count",
    "trace_error_count",
    "trace_duration_mean",
]

IF_FEATURES = [
    f"{stat}_{feature}"
    for feature in SEQUENCE_FEATURES
    for stat in ("mean", "std")
]


def _trend(window: List[Observation], attr: str) -> float:
    if len(window) < 2:
        return 0.0
    first = float(getattr(window[0], attr, 0.0) or 0.0)
    last = float(getattr(window[-1], attr, 0.0) or 0.0)
    return last - first


def _row_from_observation(obs: Observation, window: List[Observation]) -> Dict[str, float]:
    return {
        "cpu_usage_percent": float(obs.cpu_percent or 0.0),
        "memory_usage_bytes": float(obs.mem_bytes or 0.0),
        "memory_limit_bytes": float(obs.mem_limit_bytes or 0.0),
        "memory_usage_percent": float(obs.mem_percent or 0.0),
        "network_rx_bytes_per_sec": float(obs.net_rx_mbps or 0.0) * 1e6,
        "network_tx_bytes_per_sec": float(obs.net_tx_mbps or 0.0) * 1e6,
        "fs_reads_per_sec": float(obs.block_read_mbps or 0.0) * 1e6,
        "fs_writes_per_sec": float(obs.block_write_mbps or 0.0) * 1e6,
        "request_rate": 0.0,
        "error_rate": float(obs.error_rate or 0.0),
        "p50_latency_ms": 0.0,
        "p99_latency_ms": 0.0,
        "active_connections": 0.0,
        "cpu_trend_5min": _trend(window, "cpu_percent"),
        "memory_trend_5min": _trend(window, "mem_percent"),
        "error_rate_trend_5min": _trend(window, "error_rate"),
        "total_log_lines": float(obs.log_count or 0.0),
        "error_count": float(obs.error_count or 0.0),
        "warning_count": float(obs.warn_count or 0.0),
        "info_count": float(obs.info_count or 0.0),
        "error_rate_logs": float(obs.error_rate or 0.0),
        "warning_rate_logs": float(obs.warn_rate or 0.0),
        "unique_templates": float(obs.unique_templates or 0.0),
        "template_entropy": float(obs.template_entropy or 0.0),
        "new_templates_seen": float(obs.new_templates_seen or 0.0),
        "exception_count": float(obs.exception_count or 0.0),
        "timeout_count": float(obs.timeout_count or 0.0),
        "oom_mention_count": float(obs.oom_mention_count or 0.0),
        "avg_message_length": float(obs.avg_message_length or 0.0),
        "log_volume_change_pct": float(obs.log_volume_change_pct or 0.0),
        "trace_count": float(obs.trace_count or 0.0),
        "trace_error_count": float(obs.trace_error_count or 0.0),
        "trace_duration_mean": float(obs.trace_duration_mean or 0.0),
    }


def build_sequence_rows(window: List[Observation], sequence_window: int = LSTM_SEQUENCE_WINDOW) -> List[Dict[str, float]]:
    if not window:
        return []
    recent = window[-sequence_window:]
    return [_row_from_observation(obs, recent[: idx + 1]) for idx, obs in enumerate(recent)]


def rows_to_sequence_array(rows: List[Dict[str, float]]) -> np.ndarray:
    if not rows:
        return np.zeros((0, len(SEQUENCE_FEATURES)), dtype=np.float32)
    data = np.zeros((len(rows), len(SEQUENCE_FEATURES)), dtype=np.float32)
    for row_idx, row in enumerate(rows):
        for col_idx, feature in enumerate(SEQUENCE_FEATURES):
            data[row_idx, col_idx] = float(row.get(feature, 0.0) or 0.0)
    return data


def build_if_feature_vector(sequence_array: np.ndarray) -> Dict[str, float]:
    if sequence_array.size == 0:
        return {name: 0.0 for name in IF_FEATURES}
    means = sequence_array.mean(axis=0)
    stds = sequence_array.std(axis=0)
    feature_vector: Dict[str, float] = {}
    for idx, feature in enumerate(SEQUENCE_FEATURES):
        feature_vector[f"mean_{feature}"] = float(means[idx])
        feature_vector[f"std_{feature}"] = float(stds[idx])
    return feature_vector


def top_if_contributors(
    feature_vector: Dict[str, float],
    scaler_mean: Optional[np.ndarray],
    scaler_scale: Optional[np.ndarray],
    limit: int = 6,
) -> List[Dict[str, float]]:
    if scaler_mean is None or scaler_scale is None:
        return []

    contributions = []
    for idx, feature in enumerate(IF_FEATURES):
        value = float(feature_vector.get(feature, 0.0))
        scale = float(scaler_scale[idx]) if scaler_scale[idx] else 1.0
        z_score = abs((value - float(scaler_mean[idx])) / scale)
        contributions.append({
            "feature": feature,
            "value": value,
            "z_score": round(z_score, 4),
        })
    contributions.sort(key=lambda item: item["z_score"], reverse=True)
    return contributions[:limit]


def top_sequence_features(row: Dict[str, float], limit: int = 6) -> List[Dict[str, float]]:
    ranked = sorted(
        (
            {"feature": key, "value": float(value)}
            for key, value in row.items()
            if isinstance(value, (int, float))
        ),
        key=lambda item: abs(item["value"]),
        reverse=True,
    )
    return ranked[:limit]
