# Dataset Schema — AI Observability Platform

> **Contract document**: This schema defines every column in every table.
> All ML code must treat this as the authoritative specification.
> Schema version: 1.0 | Last updated: 2026-03-28

---

## Common Key Columns (present in ALL four tables)

Every row in every table carries these five columns:

| Column | Type | Values | Description |
|--------|------|---------|-------------|
| `timestamp` | string (ISO 8601) | e.g. `2026-03-28T12:00:00.123Z` | Millisecond-precision UTC timestamp of this observation |
| `service_name` | string | One of the 10 Online Boutique app services | Identifies which service this row describes |
| `failure` | int | 0 or 1 | **1** = a failure is actively being injected RIGHT NOW. Set from real injection timestamps — never inferred retroactively. |
| `pre_failure` | int | 0 or 1 | **1** = this timestep falls within K timesteps BEFORE a failure event begins (pre-failure buffer window). Only set when `failure=0`. A row cannot have both `failure=1` and `pre_failure=1`. |
| `future_failure` | int | 0 or 1 | **1** = at least one failure event begins within the next K timesteps from this row's timestamp. This is the **primary prediction target for the LSTM**. Computed from injection timestamps only — zero data leakage. |
| `failure_type` | string | See values below | Identifies the type of fault (or `"none"`) |
| `scenario_id` | string (UUID or `""`) | UUID string | Unique per injection run. All rows of one injection event (pre_failure + failure rows) share the same `scenario_id`. Empty string `""` for normal rows. |

### `failure_type` values

| Value | When set |
|-------|----------|
| `"none"` | `failure=0` AND `pre_failure=0` |
| `"pre_memory_leak"` | `pre_failure=1`, upcoming fault is memory leak |
| `"pre_cpu_starvation"` | `pre_failure=1`, upcoming fault is CPU starvation |
| `"pre_network_latency"` | `pre_failure=1`, upcoming fault is network latency |
| `"memory_leak"` | `failure=1`, active memory leak injection |
| `"cpu_starvation"` | `failure=1`, active CPU starvation |
| `"network_latency"` | `failure=1`, active network latency injection |

### Label relationship invariants

```
Normal operation:    failure=0, pre_failure=0, future_failure=0
Pre-failure buffer:  failure=0, pre_failure=1, future_failure=1
Active failure:      failure=1, pre_failure=0, future_failure=1
Post-recovery:       failure=0, pre_failure=0, future_failure=0
```

**CRITICAL**: `future_failure` is derived ONLY from injection timestamps.
It never uses any feature value (cpu, memory, error_rate, etc.).
This is enforced by `validate_labels()` and is the zero-leakage guarantee.

---

## TABLE 1: `metrics`

**File**: `pipeline/data/processed/demo_metrics.parquet`
**Grain**: One row per application service per 15-second polling interval
**Primary key**: `(timestamp, service_name)`

### Resource Metrics (from Docker Stats API)

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `cpu_usage_percent` | float | % (0–100+) | Container CPU usage as reported by Docker stats. Computed as `cpu_delta / system_cpu_delta * num_cpus * 100`. |
| `memory_usage_bytes` | float | bytes | Absolute container memory consumption (RSS equivalent from Docker stats). |
| `memory_usage_percent` | float | % (0–100) | `memory_usage_bytes / memory_limit_bytes * 100`. If no limit: `memory_usage_bytes / total_node_memory * 100`. |
| `memory_limit_bytes` | float | bytes | Container memory limit. `-1` if unlimited. |
| `network_rx_bytes_per_sec` | float | bytes/s | Network bytes received per second (computed from Docker stats cumulative counter delta). |
| `network_tx_bytes_per_sec` | float | bytes/s | Network bytes transmitted per second. |
| `fs_reads_per_sec` | float | ops/s | Block I/O read operations per second. |
| `fs_writes_per_sec` | float | ops/s | Block I/O write operations per second. |

### Request Metrics (from app instrumentation if available)

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `request_rate` | float | req/s | Requests per second. **0.0** if metric unavailable for this service. |
| `error_rate` | float | 0–1 | Fraction of requests returning HTTP 5xx. **0.0** if unavailable. |
| `p50_latency_ms` | float | ms | 50th percentile request latency. **0.0** if unavailable. |
| `p99_latency_ms` | float | ms | 99th percentile request latency. **0.0** if unavailable. |
| `active_connections` | float | count | Current open connections. **0.0** if unavailable. |

### Derived / Trend Metrics

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `cpu_trend_5min` | float | % delta | `cpu_usage_percent` minus its value 5 minutes ago. Positive = rising. **0.0** if insufficient history. |
| `memory_trend_5min` | float | % delta | `memory_usage_percent` minus its value 5 minutes ago. **0.0** if insufficient history. |
| `error_rate_trend_5min` | float | fraction delta | `error_rate` minus its value 5 minutes ago. **0.0** if insufficient history. |

---

## TABLE 2: `logs`

**File**: `pipeline/data/processed/demo_logs.parquet`
**Grain**: One row per log line emitted by any application container
**Primary key**: `(log_timestamp, service_name, drain_template_id)`

| Column | Type | Description |
|--------|------|-------------|
| `log_timestamp` | string (ISO 8601) | Timestamp from the log line itself (Loki-reported nanosecond timestamp converted to ISO). |
| `severity` | string | One of: `"DEBUG"`, `"INFO"`, `"WARN"`, `"ERROR"`, `"FATAL"`, `"UNKNOWN"`. Parsed from log content. |
| `drain_template_id` | string | Drain3 template identifier, e.g. `"T42"`. |
| `drain_template` | string | The abstract log template with variable tokens replaced by `<*>`. |
| `raw_message` | string | Raw log line truncated to 500 characters. |
| `is_error` | int (0/1) | 1 if `severity ∈ {ERROR, FATAL}`. |
| `is_warning` | int (0/1) | 1 if `severity == WARN`. |
| `message_length` | int | Character length of the raw message (before truncation). |
| `contains_exception` | int (0/1) | 1 if message contains "exception", "traceback", or "panic" (case-insensitive). |
| `contains_timeout` | int (0/1) | 1 if message contains "timeout" or "timed out" (case-insensitive). |
| `contains_oom` | int (0/1) | 1 if message contains "out of memory", "oom", or "killed" (case-insensitive). |

---

## TABLE 3: `traces`

**File**: `pipeline/data/processed/demo_traces.parquet`
**Grain**: One row per Jaeger trace span
**Primary key**: `(trace_id, span_id)`

| Column | Type | Description |
|--------|------|-------------|
| `trace_id` | string | Jaeger trace ID (hex string). |
| `span_id` | string | Jaeger span ID (hex string). |
| `parent_span_id` | string | Parent span ID. Empty string `""` if this is the root span. |
| `operation_name` | string | The traced operation name (e.g. `"hipstershop.CartService/GetCart"`). |
| `start_time` | string (ISO 8601) | Span start time converted from Jaeger microsecond timestamp. |
| `duration_ms` | float | Span duration in milliseconds. |
| `status_code` | string | `"OK"`, `"ERROR"`, or `"UNSET"`. Derived from span tags. |
| `http_status_code` | int | HTTP status code from span tags. `0` if not an HTTP span. |
| `is_error` | int (0/1) | 1 if `status_code == "ERROR"` or `http_status_code >= 500`. |
| `tags` | string | JSON-encoded span tags dict, truncated to 1000 characters. |
| `caller_service` | string | The service that initiated this span (from `process.serviceName`). |
| `callee_service` | string | The downstream service being called (from span tags if available). |

---

## TABLE 4: `log_aggregates`

**File**: `pipeline/data/processed/demo_log_aggregates.parquet`
**Grain**: One row per service per 15-second window
**Primary key**: `(window_start, service_name)`

These are pre-aggregated log statistics designed as LSTM feature inputs.
They share the same 15-second polling cadence as the `metrics` table.

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `window_start` | string (ISO 8601) | — | Start of the 15-second aggregation window. |
| `window_end` | string (ISO 8601) | — | End of the 15-second aggregation window. |
| `total_log_lines` | int | count | Total log lines emitted by this service in this window. |
| `error_count` | int | count | Lines with `severity ∈ {ERROR, FATAL}`. |
| `warning_count` | int | count | Lines with `severity == WARN`. |
| `info_count` | int | count | Lines with `severity == INFO`. |
| `error_rate_logs` | float | 0–1 | `error_count / total_log_lines`. 0 if `total_log_lines == 0`. |
| `warning_rate_logs` | float | 0–1 | `warning_count / total_log_lines`. |
| `unique_templates` | int | count | Number of distinct Drain3 template IDs seen in this window. |
| `template_entropy` | float | bits | Shannon entropy of template ID distribution: `−∑(p × log₂(p))`. High entropy = many different message types (unusual / potentially problematic). Low entropy = repetitive messages (normal steady state or tight error loop). |
| `new_templates_seen` | int | count | Template IDs appearing in this window that have NEVER been seen in any prior window across the entire collection run. Requires a global `seen_templates` set maintained across all windows. |
| `exception_count` | int | count | Lines where `contains_exception == 1`. |
| `timeout_count` | int | count | Lines where `contains_timeout == 1`. |
| `oom_mention_count` | int | count | Lines where `contains_oom == 1`. |
| `avg_message_length` | float | chars | Mean character length of log messages in this window. |
| `log_volume_change_pct` | float | % | `(total_log_lines / prev_window_total − 1) × 100`. 0 if no previous window. Captures sudden log floods. |

---

## Data Quality Notes

- **`request_rate`, `error_rate`, `p50_latency_ms`, `p99_latency_ms`**: These are 0.0 for most services because Online Boutique app services do not expose Prometheus metrics. They will become available if an OpenTelemetry Collector is added.
- **`cpu_usage_percent`**: May exceed 100 on multi-core systems (Docker reports uncapped usage).
- **`memory_limit_bytes`**: `-1` indicates no container memory limit is set. In this case `memory_usage_percent` is computed relative to total host memory.
- **All label columns** (`failure`, `pre_failure`, `future_failure`): Always integer dtype. Never `bool`, never `NaN`, never `float`.
- **`template_entropy`**: 0 if only one template seen in window (log₂(1) = 0). Maximum value depends on `unique_templates`: max = log₂(unique_templates).

---

## Joining Tables

To join `metrics` and `log_aggregates` for LSTM training:

```python
import pandas as pd

metrics = pd.read_parquet('pipeline/data/processed/demo_metrics.parquet')
agg     = pd.read_parquet('pipeline/data/processed/demo_log_aggregates.parquet')

# Align on 15-second window boundary
metrics['ts_bucket'] = pd.to_datetime(metrics['timestamp']).dt.floor('15s')
agg['ts_bucket']     = pd.to_datetime(agg['window_start']).dt.floor('15s')

combined = pd.merge(
    metrics, agg,
    on=['ts_bucket', 'service_name'],
    how='outer',
    suffixes=('_metrics', '_agg')
)
```

The common key is `(15s-bucket, service_name)`. Label columns from `metrics` take precedence; the `log_aggregates` label columns should match identically (enforced by `validate_labels()`).
