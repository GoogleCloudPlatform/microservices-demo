# Demo Dataset — Verification Report

> Generated: 2026-03-27T22:40:10Z

## Overall: ✅ PASSED

---

## Table: `metrics`

**Status**: ✅ PASSED

| Label | Count |
|-------|-------|
| Total rows | 176 |
| `failure=1` | 3 |
| `pre_failure=1` | 2 |
| `future_failure=1` | 5 |
| Normal (all zeros) | 171 |

No violations.

---

## Table: `logs`

**Status**: ✅ PASSED

| Label | Count |
|-------|-------|
| Total rows | 3508 |
| `failure=1` | 75 |
| `pre_failure=1` | 60 |
| `future_failure=1` | 135 |
| Normal (all zeros) | 3373 |

No violations.

---

## Table: `traces`

**Status**: ✅ PASSED

| Label | Count |
|-------|-------|
| Total rows | 11449 |
| `failure=1` | 0 |
| `pre_failure=1` | 0 |
| `future_failure=1` | 0 |
| Normal (all zeros) | 11449 |

No violations.

---

## Table: `log_aggregates`

**Status**: ✅ PASSED

| Label | Count |
|-------|-------|
| Total rows | 190 |
| `failure=1` | 6 |
| `pre_failure=1` | 4 |
| `future_failure=1` | 10 |
| Normal (all zeros) | 180 |

No violations.

---

## Schema Compliance

| Table | Required columns | Missing | Status |
|-------|-----------------|---------|--------|
| `metrics` | 15 | — | ✅ |
| `logs` | 12 | — | ✅ |
| `traces` | 10 | — | ✅ |
| `log_aggregates` | 14 | — | ✅ |