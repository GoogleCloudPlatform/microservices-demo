# Demo Dataset — Collection Report

> **Generated**: 2026-03-27T22:39:36Z
> **Schema version**: 1.0  |  Defined in `pipeline/data/SCHEMA.md`

---

## Collection Summary

| Field | Value |
|-------|-------|
| Collection start | `2026-03-27T22:32:41.570Z` |
| Collection end | `2026-03-27T22:38:50.999Z` |
| Duration | 369 seconds (~6.2 min) |
| Poll interval | 15 seconds |
| Services monitored | 16 |
| Drain3 available | True |

---

## Failure Injection Episode

| Field | Value |
|-------|-------|
| Target service | `recommendationservice` |
| Failure type | `memory_leak` |
| Scenario ID | `b3a0ec9a-e69f-4440-a452-8b1dc7e75939` |
| Injection start | `2026-03-27T22:35:53.924865+00:00` |
| Injection end | `2026-03-27T22:37:30.432734+00:00` |
| Duration | 96.5 seconds |
| Pre-failure buffer start | `2026-03-27T22:34:38.924865+00:00` |

---

## Table Row Counts

| Table | Rows | File |
|-------|------|------|
| metrics | 176 | `demo_metrics.parquet` |
| logs | 3,508 | `demo_logs.parquet` |
| traces | 11,449 | `demo_traces.parquet` |
| log_aggregates | 190 | `demo_log_aggregates.parquet` |

---

## Label Distribution (metrics table)

| failure | pre_failure | future_failure | failure_type | rows |
|---------|-------------|----------------|--------------|------|
| 0 | 0 | 0 | `none` | 171 |
| 0 | 1 | 1 | `pre_memory_leak` | 2 |
| 1 | 0 | 1 | `memory_leak` | 3 |

- **Normal rows**: 171 (97.2%)
- **Pre-failure rows**: 2 (1.1%)
- **Active failure rows**: 3 (1.7%)

---

## Metrics Table Statistics

### CPU Usage (%)
| Stat | Value |
|------|-------|
| Mean | 0.790 |
| Std  | 1.061 |
| Min  | 0.000 |
| Max  | 8.442 |

### Memory Usage (%)
| Stat | Value |
|------|-------|
| Mean | 1.837 |
| Std  | 2.237 |
| Min  | 0.287 |
| Max  | 10.117 |

### Services in metrics table
`adservice`, `cartservice`, `checkoutservice`, `currencyservice`, `emailservice`, `frontend`, `grafana`, `jaeger`, `loadgenerator`, `loki`, `paymentservice`, `productcatalogservice`, `prometheus`, `promtail`, `recommendationservice`, `shippingservice`

---

## Logs Table Statistics

| Severity | Count |
|----------|-------|
| INFO | 2643 |
| DEBUG | 862 |
| ERROR | 3 |

- **Error log rate**: 0.09%
- **Contains exception**: 0 lines
- **Contains timeout**: 0 lines
- **Contains OOM**: 1 lines
- **Unique Drain3 templates**: 1

---

## Traces Table Statistics

| Status | Count |
|--------|-------|
| `UNSET` | 11446 |
| `ERROR` | 3 |

- **Error spans**: 3 (0.0%)
- **Mean duration**: 2.35 ms
- **p99 duration**: 24.66 ms
- **Max duration**: 3914.04 ms
- **Unique operations**: 20

---

## Log Aggregates Statistics

- **15-second windows**: 21
- **Template entropy range**: 0.000 – 0.000 bits
- **Max log volume change**: 2850.0%

---

## How to Load

```python
import pandas as pd

metrics = pd.read_parquet('pipeline/data/processed/demo_metrics.parquet')
logs    = pd.read_parquet('pipeline/data/processed/demo_logs.parquet')
traces  = pd.read_parquet('pipeline/data/processed/demo_traces.parquet')
agg     = pd.read_parquet('pipeline/data/processed/demo_log_aggregates.parquet')

# Join metrics + log aggregates for LSTM training
metrics['ts_bucket'] = pd.to_datetime(metrics['timestamp']).dt.floor('15s')
agg['ts_bucket']     = pd.to_datetime(agg['window_start']).dt.floor('15s')

combined = pd.merge(
    metrics, agg,
    on=['ts_bucket', 'service_name'],
    how='outer',
    suffixes=('_metrics', '_agg')
)
```

---

## Label Integrity

All tables pass `validate_labels()` (zero violations):
- No row has both `failure=1` and `pre_failure=1`
- Every `failure=1` or `pre_failure=1` row has `future_failure=1`
- All label columns are integer dtype (0 or 1 only)
- `future_failure` derived solely from injection timestamps — zero data leakage
