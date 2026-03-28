"""
label_engine.py — Temporal label computation for the AI Observability dataset.

This module is the single source of truth for all failure labels.
It is used by collect_demo.py during data collection and can be imported
by any downstream ML training script.

Label definitions (from SCHEMA.md):
  failure        = 1 while a fault injection is actively running
  pre_failure    = 1 for K timesteps BEFORE a failure event starts (failure=0)
  future_failure = 1 if any failure event begins within the next K timesteps

Constants:
  PRE_FAILURE_BUFFER_K  = 5  (timesteps)
  TIMESTEP_SECONDS      = 15 (seconds per polling interval)
  BUFFER_SECONDS        = 75 (K * TIMESTEP_SECONDS)

Zero-leakage guarantee:
  future_failure is derived ONLY from injection timestamps stored in
  FailureEventRegistry.  It never reads any feature column (cpu, memory, etc.).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd

# ── Constants ─────────────────────────────────────────────────────────────────

PRE_FAILURE_BUFFER_K: int = 5          # number of 15-second steps to look back
TIMESTEP_SECONDS: int = 15             # polling cadence in seconds
BUFFER_SECONDS: int = PRE_FAILURE_BUFFER_K * TIMESTEP_SECONDS  # 75 s


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class FailureEvent:
    """Represents one complete injection episode."""
    scenario_id: str
    failure_type: str          # "memory_leak" | "cpu_starvation" | "network_latency"
    service_name: str
    start_time: datetime       # UTC — when injection began (failure=1 starts)
    end_time: Optional[datetime] = None   # UTC — when injection ended / container restarted
    buffer_seconds: int = BUFFER_SECONDS  # configurable pre-failure window (default 75s)
    pre_failure_type: str = field(init=False)

    def __post_init__(self) -> None:
        self.pre_failure_type = f"pre_{self.failure_type}"

    @property
    def pre_failure_start(self) -> datetime:
        """First timestep where pre_failure=1 (buffer_seconds before injection)."""
        return self.start_time - timedelta(seconds=self.buffer_seconds)

    def is_active_at(self, ts: datetime) -> bool:
        """True if ts falls within the active injection window."""
        if ts < self.start_time:
            return False
        if self.end_time is not None and ts >= self.end_time:
            return False
        return True

    def is_pre_failure_at(self, ts: datetime) -> bool:
        """True if ts is in the pre-failure buffer (before injection start)."""
        return self.pre_failure_start <= ts < self.start_time

    def future_failure_horizon(self) -> datetime:
        """
        Any timestamp t where t <= start_time < t + buffer_seconds
        will have future_failure=1 (i.e. a failure begins within the next K steps).
        """
        return self.start_time


# ── Registry ───────────────────────────────────────────────────────────────────

class FailureEventRegistry:
    """
    Tracks all failure injection episodes during a collection run.

    Usage pattern
    -------------
    registry = FailureEventRegistry()

    # When injection begins:
    sid = registry.register_failure_start("recommendationservice", "memory_leak")

    # When injection ends / container recovers:
    registry.register_failure_end(sid)

    # After all data is collected — stamp labels onto a DataFrame:
    df = registry.compute_labels_for_dataframe(df, ts_col="timestamp",
                                                svc_col="service_name")
    """

    def __init__(self, buffer_seconds: int = BUFFER_SECONDS) -> None:
        self._events: Dict[str, FailureEvent] = {}   # scenario_id → event
        self._active: Optional[str] = None            # scenario_id of current injection
        self._buffer_seconds = buffer_seconds         # pre-failure window length

    # ── Registration API ──────────────────────────────────────────────────────

    def register_failure_start(
        self,
        service_name: str,
        failure_type: str,
        start_time: Optional[datetime] = None,
    ) -> str:
        """
        Call this immediately when fault injection begins.

        Parameters
        ----------
        service_name : str
            The microservice being injected (e.g. "recommendationservice").
        failure_type : str
            One of: "memory_leak", "cpu_starvation", "network_latency".
        start_time : datetime, optional
            Override injection start time (UTC).  Defaults to utcnow().

        Returns
        -------
        str
            The scenario_id UUID assigned to this episode.
        """
        if start_time is None:
            start_time = datetime.now(timezone.utc)

        scenario_id = str(uuid.uuid4())
        event = FailureEvent(
            scenario_id=scenario_id,
            failure_type=failure_type,
            service_name=service_name,
            start_time=start_time,
            buffer_seconds=self._buffer_seconds,
        )
        self._events[scenario_id] = event
        self._active = scenario_id
        return scenario_id

    def register_failure_end(
        self,
        scenario_id: str,
        end_time: Optional[datetime] = None,
    ) -> None:
        """
        Call this when the injection window ends (container restart / manual stop).

        Parameters
        ----------
        scenario_id : str
            The UUID returned by register_failure_start().
        end_time : datetime, optional
            Override end time (UTC).  Defaults to utcnow().
        """
        if scenario_id not in self._events:
            raise KeyError(f"Unknown scenario_id: {scenario_id}")
        if end_time is None:
            end_time = datetime.now(timezone.utc)
        self._events[scenario_id].end_time = end_time
        if self._active == scenario_id:
            self._active = None

    # ── Point-in-time label query ──────────────────────────────────────────────

    def get_labels_for_timestamp(
        self,
        ts: datetime,
        service_name: str,
    ) -> Tuple[int, int, int, str, str]:
        """
        Return (failure, pre_failure, future_failure, failure_type, scenario_id)
        for a single (timestamp, service_name) observation.

        The tuple follows the SCHEMA.md invariants:
          - failure and pre_failure cannot both be 1
          - future_failure=1 whenever failure=1 OR pre_failure=1
        """
        failure = 0
        pre_failure = 0
        future_failure = 0
        failure_type = "none"
        scenario_id_out = ""

        for sid, ev in self._events.items():
            if ev.service_name != service_name:
                continue

            if ev.is_active_at(ts):
                failure = 1
                pre_failure = 0
                future_failure = 1
                failure_type = ev.failure_type
                scenario_id_out = sid
                break  # active injection takes priority

            if ev.is_pre_failure_at(ts):
                pre_failure = 1
                future_failure = 1
                failure_type = ev.pre_failure_type
                scenario_id_out = sid
                # don't break — a later event could be active

            # Check future_failure horizon: is a new failure about to start?
            horizon = ev.future_failure_horizon()
            if ts <= horizon < ts + timedelta(seconds=BUFFER_SECONDS):
                future_failure = 1

        return failure, pre_failure, future_failure, failure_type, scenario_id_out

    # ── Bulk DataFrame labelling ───────────────────────────────────────────────

    def compute_labels_for_dataframe(
        self,
        df: pd.DataFrame,
        ts_col: str = "timestamp",
        svc_col: str = "service_name",
    ) -> pd.DataFrame:
        """
        Stamp (failure, pre_failure, future_failure, failure_type, scenario_id)
        onto every row of *df* in-place.

        Parameters
        ----------
        df : pd.DataFrame
            Must contain columns *ts_col* and *svc_col*.
        ts_col : str
            Column holding ISO 8601 timestamp strings (or datetime objects).
        svc_col : str
            Column holding service name strings.

        Returns
        -------
        pd.DataFrame
            The same DataFrame with label columns added/overwritten.
        """
        # Ensure timestamps are tz-aware datetime objects
        ts_series = pd.to_datetime(df[ts_col], utc=True)

        failures: List[int] = []
        pre_failures: List[int] = []
        future_failures: List[int] = []
        ftypes: List[str] = []
        sids: List[str] = []

        for ts, svc in zip(ts_series, df[svc_col]):
            f, pf, ff, ft, sid = self.get_labels_for_timestamp(ts, svc)
            failures.append(f)
            pre_failures.append(pf)
            future_failures.append(ff)
            ftypes.append(ft)
            sids.append(sid)

        df = df.copy()
        df["failure"] = failures
        df["pre_failure"] = pre_failures
        df["future_failure"] = future_failures
        df["failure_type"] = ftypes
        df["scenario_id"] = sids

        # Enforce integer dtype (never bool, never float)
        for col in ("failure", "pre_failure", "future_failure"):
            df[col] = df[col].astype(int)

        return df

    # ── Global (service-agnostic) labelling — used for traces ─────────────────

    def _get_labels_any_service(
        self, ts: datetime
    ) -> Tuple[int, int, int, str, str]:
        """
        Like get_labels_for_timestamp() but matches ANY service's failure events.
        Used for traces where the span's reported service name may differ from
        the Docker injection target name.
        """
        failure = pre_failure = future_failure = 0
        failure_type = "none"
        scenario_id_out = ""

        for sid, ev in self._events.items():
            if ev.is_active_at(ts):
                failure = 1
                pre_failure = 0
                future_failure = 1
                failure_type = ev.failure_type
                scenario_id_out = sid
                break

            if ev.is_pre_failure_at(ts):
                pre_failure = 1
                future_failure = 1
                failure_type = ev.pre_failure_type
                scenario_id_out = sid

            horizon = ev.future_failure_horizon()
            if ts <= horizon < ts + timedelta(seconds=ev.buffer_seconds):
                future_failure = 1

        return failure, pre_failure, future_failure, failure_type, scenario_id_out

    def compute_global_labels_for_dataframe(
        self,
        df: pd.DataFrame,
        ts_col: str = "timestamp",
    ) -> pd.DataFrame:
        """
        Stamp labels onto traces/logs using timestamp-only matching (no service filter).
        Any span executing during a failure window is labeled — regardless of what
        service name Jaeger recorded for the process.
        """
        ts_series = pd.to_datetime(df[ts_col], utc=True)

        failures: List[int] = []
        pre_failures: List[int] = []
        future_failures: List[int] = []
        ftypes: List[str] = []
        sids: List[str] = []

        for ts in ts_series:
            f, pf, ff, ft, sid = self._get_labels_any_service(ts)
            failures.append(f)
            pre_failures.append(pf)
            future_failures.append(ff)
            ftypes.append(ft)
            sids.append(sid)

        df = df.copy()
        df["failure"] = failures
        df["pre_failure"] = pre_failures
        df["future_failure"] = future_failures
        df["failure_type"] = ftypes
        df["scenario_id"] = sids

        for col in ("failure", "pre_failure", "future_failure"):
            df[col] = df[col].astype(int)

        return df

    # ── Introspection ─────────────────────────────────────────────────────────

    def get_summary(self) -> Dict:
        """Return a serialisable summary of all registered events."""
        events_out = []
        for ev in self._events.values():
            events_out.append({
                "scenario_id": ev.scenario_id,
                "service_name": ev.service_name,
                "failure_type": ev.failure_type,
                "start_time": ev.start_time.isoformat(),
                "end_time": ev.end_time.isoformat() if ev.end_time else None,
                "pre_failure_start": ev.pre_failure_start.isoformat(),
                "duration_seconds": (
                    (ev.end_time - ev.start_time).total_seconds()
                    if ev.end_time else None
                ),
            })
        return {
            "total_events": len(self._events),
            "events": events_out,
            "pre_failure_buffer_k": PRE_FAILURE_BUFFER_K,
            "timestep_seconds": TIMESTEP_SECONDS,
            "buffer_seconds": BUFFER_SECONDS,
        }

    def all_events(self) -> List[FailureEvent]:
        return list(self._events.values())


# ── Validation ─────────────────────────────────────────────────────────────────

def validate_labels(df: pd.DataFrame, strict: bool = True) -> Dict:
    """
    Validate label integrity on a labelled DataFrame.

    Checks enforced
    ---------------
    1. No row has both failure=1 and pre_failure=1
    2. Every row with failure=1 or pre_failure=1 also has future_failure=1
    3. failure_type values are from the allowed set
    4. Label columns are integer dtype (0/1 only)
    5. scenario_id is non-empty whenever failure=1 or pre_failure=1
    6. future_failure is never derived from feature columns (cannot check here,
       but we verify it matches the label-only constraint above)

    Parameters
    ----------
    df : pd.DataFrame
        Must contain: failure, pre_failure, future_failure, failure_type, scenario_id
    strict : bool
        If True, raise ValueError on any violation.  If False, return report only.

    Returns
    -------
    dict
        Validation report with keys: passed (bool), violations (list of str),
        stats (dict with label counts).
    """
    violations: List[str] = []

    required_cols = {"failure", "pre_failure", "future_failure", "failure_type", "scenario_id"}
    missing = required_cols - set(df.columns)
    if missing:
        msg = f"Missing required label columns: {missing}"
        if strict:
            raise ValueError(msg)
        return {"passed": False, "violations": [msg], "stats": {}}

    # 1. Mutual exclusion: failure=1 AND pre_failure=1 must never co-occur
    both_set = df[(df["failure"] == 1) & (df["pre_failure"] == 1)]
    if len(both_set) > 0:
        violations.append(
            f"VIOLATION: {len(both_set)} rows have both failure=1 AND pre_failure=1"
        )

    # 2. future_failure must be 1 whenever failure=1 or pre_failure=1
    active_or_pre = df[(df["failure"] == 1) | (df["pre_failure"] == 1)]
    ff_missing = active_or_pre[active_or_pre["future_failure"] != 1]
    if len(ff_missing) > 0:
        violations.append(
            f"VIOLATION: {len(ff_missing)} rows have failure/pre_failure=1 but future_failure=0"
        )

    # 3. failure_type values
    allowed_types = {
        "none",
        "memory_leak", "cpu_starvation", "network_latency",
        "pre_memory_leak", "pre_cpu_starvation", "pre_network_latency",
    }
    bad_types = df[~df["failure_type"].isin(allowed_types)]["failure_type"].unique()
    if len(bad_types) > 0:
        violations.append(f"VIOLATION: Unknown failure_type values: {list(bad_types)}")

    # 4. Label dtype integrity (0/1 integers)
    for col in ("failure", "pre_failure", "future_failure"):
        if df[col].dtype not in ("int32", "int64", "int8"):
            violations.append(f"VIOLATION: Column '{col}' has non-integer dtype: {df[col].dtype}")
        bad_vals = df[~df[col].isin([0, 1])][col].unique()
        if len(bad_vals) > 0:
            violations.append(f"VIOLATION: Column '{col}' has values outside {{0,1}}: {bad_vals}")

    # 5. scenario_id non-empty when active or pre-failure
    for flag_col in ("failure", "pre_failure"):
        flagged = df[df[flag_col] == 1]
        empty_sid = flagged[flagged["scenario_id"] == ""]
        if len(empty_sid) > 0:
            violations.append(
                f"VIOLATION: {len(empty_sid)} rows with {flag_col}=1 have empty scenario_id"
            )

    # 6. Normal rows must have failure_type == "none"
    normal = df[(df["failure"] == 0) & (df["pre_failure"] == 0)]
    bad_normal_type = normal[normal["failure_type"] != "none"]
    if len(bad_normal_type) > 0:
        violations.append(
            f"VIOLATION: {len(bad_normal_type)} normal rows (failure=pre_failure=0) "
            f"have failure_type != 'none'"
        )

    # Stats
    stats = {
        "total_rows": len(df),
        "failure_rows": int((df["failure"] == 1).sum()),
        "pre_failure_rows": int((df["pre_failure"] == 1).sum()),
        "future_failure_rows": int((df["future_failure"] == 1).sum()),
        "normal_rows": int(
            ((df["failure"] == 0) & (df["pre_failure"] == 0) & (df["future_failure"] == 0)).sum()
        ),
        "failure_type_counts": df["failure_type"].value_counts().to_dict(),
    }

    passed = len(violations) == 0
    if not passed and strict:
        raise ValueError("Label validation failed:\n" + "\n".join(violations))

    return {"passed": passed, "violations": violations, "stats": stats}


# ── CLI self-test ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    print("=== FailureEventRegistry self-test ===\n")

    reg = FailureEventRegistry()

    # Simulate a 5-minute collection run
    now = datetime(2026, 3, 28, 12, 0, 0, tzinfo=timezone.utc)

    # Inject memory leak starting at T+2min, ending at T+4min
    inj_start = now + timedelta(minutes=2)
    inj_end   = now + timedelta(minutes=4)

    sid = reg.register_failure_start(
        service_name="recommendationservice",
        failure_type="memory_leak",
        start_time=inj_start,
    )
    reg.register_failure_end(sid, end_time=inj_end)

    print(f"Registered scenario: {sid}")
    print(f"Injection window: {inj_start.isoformat()} → {inj_end.isoformat()}")
    print(f"Pre-failure buffer: {(inj_start - timedelta(seconds=BUFFER_SECONDS)).isoformat()} → {inj_start.isoformat()}\n")

    # Build a small test DataFrame
    rows = []
    t = now
    for _ in range(25):   # 25 × 15s = 375 s = 6.25 min
        rows.append({"timestamp": t.isoformat(), "service_name": "recommendationservice",
                     "cpu_usage_percent": 10.0})
        t += timedelta(seconds=15)

    df_test = pd.DataFrame(rows)
    df_labelled = reg.compute_labels_for_dataframe(df_test)

    print("Label distribution:")
    print(df_labelled[["timestamp", "failure", "pre_failure", "future_failure",
                        "failure_type"]].to_string(index=False))
    print()

    report = validate_labels(df_labelled, strict=False)
    print("Validation report:")
    print(json.dumps(report, indent=2))

    assert report["passed"], f"Validation failed: {report['violations']}"
    print("\n✓ All checks passed.")
