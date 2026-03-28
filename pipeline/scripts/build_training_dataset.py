#!/usr/bin/env python3
"""
build_training_dataset.py

Merges processed + training data, builds:
  - Isolation Forest dataset: X_normal.npy + scaler.pkl
  - LSTM dataset: X_sequences.npy + y_sequences.npy
"""

import os
import sys
import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path

# Repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = REPO_ROOT / "pipeline" / "data" / "processed"
TRAINING_DIR = REPO_ROOT / "pipeline" / "data" / "training"

IF_DATA_DIR = REPO_ROOT / "ml" / "isolation_forest" / "data"
LSTM_DATA_DIR = REPO_ROOT / "ml" / "lstm" / "data"

# Feature columns from metrics
METRIC_FEATURES = [
    "cpu_percent",
    "mem_percent",
    "net_rx_mb",
    "net_tx_mb",
    "block_read_mb",
    "block_write_mb",
]

# Log aggregate features
LOG_FEATURES = [
    "log_count",
    "error_rate",
    "warn_rate",
    "template_entropy",
]

ALL_FEATURES = METRIC_FEATURES + LOG_FEATURES

WINDOW_SIZE = 20
STRIDE = 5


def load_metrics(directory: Path, label: str):
    """Load metrics parquet from directory."""
    candidates = [
        directory / "training_metrics.parquet",
        directory / "full_metrics.parquet",
    ]
    for path in candidates:
        if path.exists():
            print(f"  Loading metrics from {path}")
            df = pd.read_parquet(path)
            df["_source"] = label
            return df
    return None


def load_log_aggregates(directory: Path):
    """Load log aggregates parquet from directory."""
    candidates = [
        directory / "training_log_aggregates.parquet",
        directory / "full_log_aggregates.parquet",
        directory / "training_log_aggregates.csv",
        directory / "full_log_aggregates.csv",
    ]
    for path in candidates:
        if path.exists():
            print(f"  Loading log aggregates from {path}")
            if path.suffix == ".parquet":
                return pd.read_parquet(path)
            else:
                return pd.read_csv(path)
    return None


def normalize_metrics_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names to our feature set."""
    rename_map = {
        # cpu
        "cpu_usage_percent": "cpu_percent",
        "cpu_percent_usage": "cpu_percent",
        # memory
        "memory_usage_percent": "mem_percent",
        "mem_usage_percent": "mem_percent",
        # network
        "network_rx_bytes_per_sec": "net_rx_mb",
        "net_rx_bytes_per_sec": "net_rx_mb",
        "network_tx_bytes_per_sec": "net_tx_mb",
        "net_tx_bytes_per_sec": "net_tx_mb",
        # block io
        "fs_reads_per_sec": "block_read_mb",
        "fs_read_mb": "block_read_mb",
        "fs_writes_per_sec": "block_write_mb",
        "fs_write_mb": "block_write_mb",
    }
    df = df.rename(columns=rename_map)

    # Convert bytes/sec to MB (heuristic: if max > 1e6, likely bytes)
    for col in ["net_rx_mb", "net_tx_mb", "block_read_mb", "block_write_mb"]:
        if col in df.columns and df[col].max() > 1e5:
            df[col] = df[col] / 1e6

    return df


def join_log_features(metrics: pd.DataFrame, log_agg: pd.DataFrame) -> pd.DataFrame:
    """Join log aggregate features onto metrics using service + timestamp window."""
    if log_agg is None or log_agg.empty:
        for feat in LOG_FEATURES:
            metrics[feat] = 0.0
        return metrics

    # Normalize log agg columns
    log_rename = {
        "total_log_lines": "log_count",
        "error_rate_logs": "error_rate",
        "warning_rate_logs": "warn_rate",
        "template_entropy": "template_entropy",
        "error_count": "_error_count",
        "warning_count": "_warn_count",
    }
    log_agg = log_agg.rename(columns=log_rename)

    # Ensure timestamps are datetime
    for col in ["timestamp", "window_start"]:
        if col in log_agg.columns:
            log_agg[col] = pd.to_datetime(log_agg[col], utc=True, errors="coerce")

    if "timestamp" in metrics.columns:
        metrics["_ts"] = pd.to_datetime(metrics["timestamp"], utc=True, errors="coerce")
    else:
        metrics["_ts"] = pd.NaT

    # Build log lookup: service -> sorted (timestamp, features)
    log_ts_col = "timestamp" if "timestamp" in log_agg.columns else "window_start"

    # Ensure log features exist
    for feat in LOG_FEATURES:
        if feat not in log_agg.columns:
            log_agg[feat] = 0.0

    # Compute error_rate and warn_rate if missing
    if "error_rate" not in log_agg.columns or log_agg["error_rate"].isna().all():
        if "log_count" in log_agg.columns and log_agg["log_count"].sum() > 0:
            if "_error_count" in log_agg.columns:
                log_agg["error_rate"] = log_agg["_error_count"] / log_agg["log_count"].replace(0, 1)
            if "_warn_count" in log_agg.columns:
                log_agg["warn_rate"] = log_agg["_warn_count"] / log_agg["log_count"].replace(0, 1)

    svc_col = "service_name" if "service_name" in log_agg.columns else None
    if svc_col and "service_name" in metrics.columns:
        # Merge on service + nearest timestamp
        result_parts = []
        for svc, m_grp in metrics.groupby("service_name"):
            l_grp = log_agg[log_agg[svc_col] == svc] if svc_col else log_agg
            if l_grp.empty:
                for feat in LOG_FEATURES:
                    m_grp = m_grp.copy()
                    m_grp[feat] = 0.0
                result_parts.append(m_grp)
                continue

            l_grp = l_grp.sort_values(log_ts_col)
            l_ts = l_grp[log_ts_col].values.astype("datetime64[ns]")
            m_ts = m_grp["_ts"].values.astype("datetime64[ns]")

            # For each metric row, find nearest log window
            indices = np.searchsorted(l_ts, m_ts, side="left")
            indices = np.clip(indices, 0, len(l_ts) - 1)

            m_grp = m_grp.copy()
            for feat in LOG_FEATURES:
                vals = l_grp[feat].values
                m_grp[feat] = vals[indices]
            result_parts.append(m_grp)

        metrics = pd.concat(result_parts, ignore_index=True)
    else:
        for feat in LOG_FEATURES:
            metrics[feat] = 0.0

    return metrics


def build_feature_matrix(df: pd.DataFrame) -> np.ndarray:
    """Build feature matrix from dataframe, filling missing with 0."""
    X = np.zeros((len(df), len(ALL_FEATURES)), dtype=np.float32)
    for i, col in enumerate(ALL_FEATURES):
        if col in df.columns:
            X[:, i] = df[col].fillna(0.0).values
    return X


def build_sequences(df: pd.DataFrame, window: int, stride: int):
    """Build LSTM sequences per service, sorted by timestamp."""
    X_seqs = []
    y_seqs = []

    if "service_name" in df.columns:
        groups = df.groupby("service_name")
    else:
        groups = [("all", df)]

    for svc, grp in groups:
        grp = grp.sort_values("_ts") if "_ts" in grp.columns else grp

        X = build_feature_matrix(grp)
        y = grp["future_failure"].fillna(0).values.astype(np.float32) if "future_failure" in grp.columns else np.zeros(len(grp), dtype=np.float32)

        n = len(X)
        for start in range(0, n - window, stride):
            end = start + window
            X_seqs.append(X[start:end])
            # Label = 1 if any future_failure in the window is 1
            y_seqs.append(float(y[end - 1]))

    if not X_seqs:
        return np.array([]).reshape(0, window, len(ALL_FEATURES)), np.array([])

    return np.array(X_seqs, dtype=np.float32), np.array(y_seqs, dtype=np.float32)


def main():
    print("=" * 60)
    print("Building Training Datasets")
    print("=" * 60)

    # --- Load data ---
    dfs = []

    print("\nLoading processed data...")
    proc_metrics = load_metrics(PROCESSED_DIR, "processed")
    if proc_metrics is not None:
        dfs.append(proc_metrics)
    else:
        print("  No processed metrics found.")

    print("Loading training data (if exists)...")
    train_metrics = load_metrics(TRAINING_DIR, "training")
    if train_metrics is not None:
        dfs.append(train_metrics)
    else:
        print("  No training metrics found (OK - using processed only).")

    if not dfs:
        print("ERROR: No metrics data found at all. Exiting.")
        sys.exit(1)

    df = pd.concat(dfs, ignore_index=True)
    df = normalize_metrics_columns(df)

    # Ensure timestamp col
    if "timestamp" in df.columns:
        df["_ts"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    else:
        df["_ts"] = pd.NaT

    # --- Load log aggregates ---
    print("Loading log aggregates...")
    log_agg_list = []
    proc_logs = load_log_aggregates(PROCESSED_DIR)
    if proc_logs is not None:
        log_agg_list.append(proc_logs)
    train_logs = load_log_aggregates(TRAINING_DIR)
    if train_logs is not None:
        log_agg_list.append(train_logs)

    log_agg = pd.concat(log_agg_list, ignore_index=True) if log_agg_list else None

    # --- Join log features ---
    print("Joining log features onto metrics...")
    df = join_log_features(df, log_agg)

    # --- Stats ---
    total = len(df)
    normal_mask = (df["failure"] == 0) & (df["pre_failure"] == 0)
    failure_mask = df["failure"] == 1
    pre_failure_mask = df["pre_failure"] == 1

    n_normal = normal_mask.sum()
    n_failure = failure_mask.sum()
    n_pre_failure = pre_failure_mask.sum()

    print(f"\nDataset stats:")
    print(f"  Total rows:       {total}")
    print(f"  Normal rows:      {n_normal}")
    print(f"  Failure rows:     {n_failure}")
    print(f"  Pre-failure rows: {n_pre_failure}")

    # =============================================
    # Isolation Forest: X_normal
    # =============================================
    print("\n--- Building Isolation Forest dataset ---")

    from sklearn.preprocessing import StandardScaler

    normal_df = df[normal_mask].copy()
    X_normal = build_feature_matrix(normal_df)

    # Fit scaler
    scaler = StandardScaler()
    X_normal_scaled = scaler.fit_transform(X_normal)

    # Save
    IF_DATA_DIR.mkdir(parents=True, exist_ok=True)
    np.save(str(IF_DATA_DIR / "X_normal.npy"), X_normal_scaled.astype(np.float32))
    with open(str(IF_DATA_DIR / "scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)

    print(f"  X_normal shape: {X_normal_scaled.shape}")
    print(f"  Saved to {IF_DATA_DIR}/X_normal.npy + scaler.pkl")

    # =============================================
    # LSTM: sequences
    # =============================================
    print("\n--- Building LSTM sequences ---")

    X_seqs, y_seqs = build_sequences(df, window=WINDOW_SIZE, stride=STRIDE)

    if len(X_seqs) == 0:
        print("  Warning: No sequences built (not enough data). Creating dummy sequences.")
        X_seqs = np.zeros((1, WINDOW_SIZE, len(ALL_FEATURES)), dtype=np.float32)
        y_seqs = np.zeros(1, dtype=np.float32)

    pos_rate = float(y_seqs.mean()) if len(y_seqs) > 0 else 0.0

    print(f"  Sequence count:   {len(X_seqs)}")
    print(f"  Sequence shape:   {X_seqs.shape}")
    print(f"  Positive seq rate: {pos_rate:.3f}")

    LSTM_DATA_DIR.mkdir(parents=True, exist_ok=True)
    np.save(str(LSTM_DATA_DIR / "X_sequences.npy"), X_seqs)
    np.save(str(LSTM_DATA_DIR / "y_sequences.npy"), y_seqs)

    # Save feature metadata
    meta = {
        "features": ALL_FEATURES,
        "window_size": WINDOW_SIZE,
        "stride": STRIDE,
        "n_normal": int(n_normal),
        "n_failure": int(n_failure),
        "n_pre_failure": int(n_pre_failure),
        "total": total,
        "pos_rate": pos_rate,
    }
    with open(str(LSTM_DATA_DIR / "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\nSaved to {LSTM_DATA_DIR}/X_sequences.npy + y_sequences.npy")
    print("\nDataset build complete.")


if __name__ == "__main__":
    main()
