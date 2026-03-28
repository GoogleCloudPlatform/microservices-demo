"""
AI Observability Platform - FastAPI Backend

Port: 8001
- /health              GET  System health check
- /status              GET  Full system status with anomaly scores + incident state
- /ingest              POST Accept live metrics/logs, update scores
- /remediate           POST Execute the staged remediation pipeline
- /decision/validate   POST Validate an AI action proposal against policy
- /incidents/active    GET  Active incidents
- /incidents/history   GET  Recent incident history
- /incidents/similar   GET  Similar incidents from memory
- /history             GET  Last 100 score snapshots
- /alerts              GET  Active alerts (score > 0.7)
- /topology            GET  Rich service topology with features
- /window/{service}    GET  Raw window observations for sparklines
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
import logging
from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add repo root and backend to sys.path for imports
_file = os.path.abspath(__file__)
_backend = os.path.dirname(os.path.dirname(_file))
_repo_root = os.path.dirname(_backend)
for _p in [_backend, _repo_root]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from anomaly_api.correlation import CorrelationEngine
from anomaly_api.infrastructure import build_infrastructure_payload
from anomaly_api.model_features import (
    IF_FEATURES,
    LSTM_SEQUENCE_WINDOW,
    SEQUENCE_FEATURES,
    build_if_feature_vector,
    build_sequence_rows,
    rows_to_sequence_array,
    top_if_contributors,
    top_sequence_features,
)
from anomaly_api.security import require_operator_token
from anomaly_api.settings import load_settings
from anomaly_api.system_store import SQLiteLogHandler, SQLiteSystemStore
from remediation.engine import RemediationEngine
from remediation.models import ActionProposal
from remediation.policy import CRITICAL_SHARED_SERVICES, DEPENDENCY_GRAPH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
SETTINGS = load_settings()

ALL_SERVICES = [
    "frontend",
    "productcatalogservice",
    "cartservice",
    "recommendationservice",
    "checkoutservice",
    "paymentservice",
    "shippingservice",
    "emailservice",
    "currencyservice",
    "adservice",
    "redis-cart",
]
RUNTIME_FAILURE_TRIGGER_COUNT = 2
RUNTIME_RESTART_LOOP_THRESHOLD = 3
RUNTIME_STARTUP_GRACE_POLLS = 10
RUNTIME_AUTOMATION_WARMUP_S = 60

REVERSE_DEPENDENCY_GRAPH: Dict[str, List[str]] = {}
for _service_name, _dependencies in DEPENDENCY_GRAPH.items():
    for _dependency in _dependencies:
        REVERSE_DEPENDENCY_GRAPH.setdefault(_dependency, []).append(_service_name)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AppState:
    def __init__(self):
        self.started_at = time.time()
        self.models_loaded = False
        self.if_inference = None
        self.lstm_inference = None
        self.correlation_engine = None
        self.remediation_engine: Optional[RemediationEngine] = None

        self.current_scores: Dict[str, Dict] = {}
        self.current_model_insights: Dict[str, Dict] = {}
        self.history: deque = deque(maxlen=100)
        self.last_update: float = 0.0
        self.predictive_alerts: Dict[str, Dict[str, Any]] = {}
        self.predictive_cooldowns: Dict[str, float] = {}
        self.runtime_health: Dict[str, Dict[str, Any]] = {}
        self.system_store: Optional[SQLiteSystemStore] = None
        self.demo_task: Optional[asyncio.Task] = None

        self.window_state = None
        self.ingestion_pipeline = None


state = AppState()


def emit_system_event(
    *,
    event_type: str,
    category: str,
    severity: str,
    title: str,
    message: str,
    service: Optional[str] = None,
    status: str = "open",
    payload: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    if state.system_store is None:
        return None
    try:
        return state.system_store.add_event(
            event_type=event_type,
            category=category,
            severity=severity,
            title=title,
            message=message,
            service=service,
            status=status,
            payload=payload,
        )
    except Exception as exc:
        logger.debug("Failed to persist event %s: %s", event_type, exc)
        return None


def init_system_store() -> None:
    if state.system_store is not None:
        return
    state.system_store = SQLiteSystemStore(SETTINGS.system_db_path)
    root_logger = logging.getLogger()
    if not any(isinstance(handler, SQLiteLogHandler) for handler in root_logger.handlers):
        root_logger.addHandler(SQLiteLogHandler(state.system_store))


def latest_demo_run() -> Optional[Dict[str, Any]]:
    if state.system_store is None:
        return None
    try:
        return state.system_store.latest_demo_run()
    except Exception as exc:
        logger.debug("Failed to fetch latest demo run: %s", exc)
        return None


def _demo_summary_text(run: Dict[str, Any]) -> str:
    service = run.get("service", "service")
    status = run.get("status", "unknown")
    stage = run.get("stage", "unknown")
    summary = run.get("summary_text", "")
    return summary or f"Demo run for {service} is {status} at stage {stage}."


def _current_service_snapshot(service: str) -> Dict[str, Any]:
    snapshot = dict(state.current_scores.get(service, {}))
    workload = None
    if state.remediation_engine is not None:
        try:
            workload = state.remediation_engine.orchestrator.inspect_service(service).to_dict()
        except Exception as exc:
            workload = {"status": "unavailable", "message": str(exc)}
    return {
        "service": service,
        "score": round(float(snapshot.get("combined_score", 0.0) or 0.0), 4),
        "if_score": round(float(snapshot.get("if_score", 0.0) or 0.0), 4),
        "lstm_score": round(float(snapshot.get("lstm_score", 0.0) or 0.0), 4) if snapshot.get("lstm_score") is not None else None,
        "model_state": snapshot.get("model_state"),
        "feature_flags": snapshot.get("feature_flags", []),
        "workload": workload or {},
    }


def _build_demo_report(run_id: int, service: str, started_at: str, remediation_result: Dict[str, Any], platform: str) -> Dict[str, Any]:
    if state.system_store is None:
        return {
            "summary_text": f"Demo run {run_id} completed without a system store.",
            "summary_json": {},
            "report_markdown": "",
            "report_json": {},
        }

    events = state.system_store.list_events_since(started_at, limit=160, service=service)
    logs = state.system_store.list_logs_since(started_at, limit=220)
    error_logs = [item for item in logs if item.get("level") in {"ERROR", "CRITICAL"}]
    warning_logs = [item for item in logs if item.get("level") == "WARNING"]
    final_state = state.remediation_engine.orchestrator.inspect_service(service) if state.remediation_engine else None
    final_ok = bool(final_state and final_state.exists and final_state.running and final_state.status not in {"not_found", "dead", "exited"})
    execution_steps = remediation_result.get("execution_steps", [])
    step_names = [step.get("action") for step in execution_steps if step.get("action")]
    event_titles = [item.get("title") for item in events[:6] if item.get("title")]
    noteworthy_logs = [item.get("message") for item in error_logs[:3]] or [item.get("message") for item in warning_logs[:3]]

    summary_text = (
        f"AEGIS demo attacked {service} on {platform}, observed the outage, "
        f"applied {remediation_result.get('decision', {}).get('action', 'a recovery action')}, "
        f"and ended with the workload {'healthy' if final_ok else 'still degraded'}."
    )
    summary_json = {
        "run_id": run_id,
        "service": service,
        "platform": platform,
        "status": "resolved" if final_ok else "degraded",
        "incident_id": remediation_result.get("incident_id"),
        "decision_action": remediation_result.get("decision", {}).get("action"),
        "within_target": remediation_result.get("within_target"),
        "elapsed_s": remediation_result.get("elapsed_s"),
        "event_count": len(events),
        "log_count": len(logs),
        "error_log_count": len(error_logs),
        "warning_log_count": len(warning_logs),
        "event_titles": event_titles,
        "noteworthy_logs": noteworthy_logs,
        "execution_steps": step_names,
        "final_state": final_state.to_dict() if final_state else {},
    }
    markdown_lines = [
        "# AEGIS Autonomous Demo Report",
        "",
        f"Run ID: {run_id}",
        f"Service attacked: {service}",
        f"Platform: {platform}",
        f"Generated at: {utc_now_iso()}",
        "",
        "## Summary",
        "",
        summary_text,
        "",
        f"- Incident ID: {remediation_result.get('incident_id') or 'n/a'}",
        f"- Recovery action: {remediation_result.get('decision', {}).get('action', 'n/a')}",
        f"- Within target: {remediation_result.get('within_target')}",
        f"- Elapsed seconds: {remediation_result.get('elapsed_s')}",
        f"- Events recorded: {len(events)}",
        f"- Logs recorded: {len(logs)}",
        "",
        "## Timeline Highlights",
        "",
    ]
    markdown_lines.extend([f"- {title}" for title in event_titles] or ["- No notable events were captured."])
    markdown_lines.extend(["", "## Log Highlights", ""])
    markdown_lines.extend([f"- {line}" for line in noteworthy_logs] or ["- No warning or error log highlights were captured."])
    markdown_lines.extend(["", "## Execution Steps", ""])
    markdown_lines.extend([f"- {name}" for name in step_names] or ["- No execution steps recorded."])
    return {
        "summary_text": summary_text,
        "summary_json": summary_json,
        "report_markdown": "\n".join(markdown_lines),
        "report_json": {
            "generated_at": utc_now_iso(),
            "summary": summary_json,
            "events": events,
            "logs": logs,
            "remediation_result": remediation_result,
        },
    }


async def run_autonomous_demo(run_id: int, service: str, owner: str) -> None:
    orchestrator = state.remediation_engine.orchestrator if state.remediation_engine else None
    if orchestrator is None or state.system_store is None or state.remediation_engine is None:
        return

    demo = state.system_store.get_demo_run(run_id)
    started_at = demo["created_at"] if demo else utc_now_iso()
    platform = orchestrator.platform

    try:
        baseline = _current_service_snapshot(service)
        state.system_store.update_demo_run(
            run_id,
            stage="priming",
            status="running",
            summary_text=f"Preparing controlled failure sequence for {service} on {platform}.",
            summary_json={"baseline": baseline, "stage_history": [{"stage": "priming", "at": utc_now_iso()}]},
        )
        logger.info(
            "Autonomous demo started for %s on %s",
            service,
            platform,
            extra={"service": service, "event_type": "demo_started"},
        )
        emit_system_event(
            event_type="demo_started",
            category="demo",
            severity="warning",
            title=f"Autonomous demo started for {service}",
            message="AEGIS is intentionally disrupting a service to prove detection and recovery.",
            service=service,
            status="open",
            payload={"run_id": run_id, "owner": owner, "platform": platform, "baseline": baseline},
        )
        emit_system_event(
            event_type="demo_pressure_building",
            category="demo",
            severity="info",
            title=f"Controlled pressure building on {service}",
            message=(
                f"AEGIS is capturing the live baseline for {service} before injecting the failure. "
                f"Current score is {baseline['score']:.3f}."
            ),
            service=service,
            status="open",
            payload={"run_id": run_id, "baseline": baseline},
        )
        await asyncio.sleep(2.5)

        state.system_store.update_demo_run(
            run_id,
            stage="pressure_building",
            status="running",
            summary_text=f"Baseline captured for {service}; failure injection is about to start.",
            summary_json={"baseline": baseline, "stage_history": [{"stage": "priming", "at": utc_now_iso()}, {"stage": "pressure_building", "at": utc_now_iso()}]},
        )
        await asyncio.sleep(2.5)

        state.system_store.update_demo_run(run_id, stage="attacking", status="running")
        ok, message, details = orchestrator.stop_service(service)
        logger.info(
            "Demo attack injected for %s: %s",
            service,
            message,
            extra={"service": service, "event_type": "demo_attack_injected"},
        )
        emit_system_event(
            event_type="demo_attack_injected",
            category="demo",
            severity="warning" if ok else "critical",
            title=f"Intentional failure injected for {service}",
            message=message if ok else f"Failed to inject demo failure: {message}",
            service=service,
            status="open",
            payload={"run_id": run_id, "details": details},
        )
        if not ok:
            report = _build_demo_report(run_id, service, started_at, {}, platform)
            state.system_store.update_demo_run(
                run_id,
                status="failed",
                stage="failed",
                summary_text=report["summary_text"],
                summary_json=report["summary_json"],
                report_markdown=report["report_markdown"],
                report_json=report["report_json"],
            )
            return

        state.system_store.update_demo_run(
            run_id,
            stage="observing_failure",
            status="running",
            summary_text=f"Failure injected into {service}; observing cluster impact before remediation.",
        )
        emit_system_event(
            event_type="demo_failure_observed",
            category="demo",
            severity="warning",
            title=f"Watching failure propagation on {service}",
            message="The workload has been disrupted; AEGIS is waiting for the live telemetry and runtime signals to reflect the failure.",
            service=service,
            status="open",
            payload={"run_id": run_id, "post_attack_state": _current_service_snapshot(service)},
        )

        await asyncio.sleep(6.0)
        state.system_store.update_demo_run(run_id, stage="remediating", status="running")
        logger.info(
            "Autonomous recovery started for %s",
            service,
            extra={"service": service, "event_type": "demo_recovery_started"},
        )
        emit_system_event(
            event_type="demo_recovery_started",
            category="demo",
            severity="info",
            title=f"Autonomous recovery started for {service}",
            message="AEGIS is now running its remediation workflow against the intentionally disrupted service.",
            service=service,
            status="open",
            payload={"run_id": run_id},
        )

        evidence = _build_evidence(service, "service_unhealthy", state.current_scores)
        evidence["summary"] = (
            f"Autonomous demo run intentionally stopped {service}; the system must detect and restore the workload."
        )
        proposal = ActionProposal(
            source="demo",
            proposed_action="start_service",
            target=service,
            confidence=0.99,
            rationale="Autonomous demo recovery after an intentional service stop.",
        )
        remediation_result = state.remediation_engine.remediate(
            service=service,
            failure_type="service_unhealthy",
            severity="critical",
            affected_services=[service],
            evidence=evidence,
            proposal=proposal,
        )
        logger.info(
            "Demo remediation for %s selected %s and incident %s",
            service,
            remediation_result.get("decision", {}).get("action", "unknown"),
            remediation_result.get("incident_id"),
            extra={
                "service": service,
                "event_type": "demo_remediation_result",
                "incident_id": remediation_result.get("incident_id"),
            },
        )

        state.system_store.update_demo_run(
            run_id,
            stage="evaluating",
            status="running",
            incident_id=remediation_result.get("incident_id"),
            fix_action=remediation_result.get("decision", {}).get("action", ""),
            summary_text=(
                f"Remediation triggered for {service}; evaluating whether "
                f"{remediation_result.get('decision', {}).get('action', 'the selected action')} restored health."
            ),
        )

        for _ in range(8):
            runtime_state = orchestrator.inspect_service(service)
            if runtime_state.exists and runtime_state.running and runtime_state.status not in {"not_found", "dead", "exited"}:
                break
            await asyncio.sleep(1.5)

        report = _build_demo_report(run_id, service, started_at, remediation_result, platform)
        final_status = "resolved" if report["summary_json"].get("status") == "resolved" else "failed"
        state.system_store.update_demo_run(
            run_id,
            status=final_status,
            stage="completed",
            summary_text=report["summary_text"],
            summary_json=report["summary_json"],
            report_markdown=report["report_markdown"],
            report_json=report["report_json"],
        )
        logger.info(
            "Autonomous demo completed for %s with status %s",
            service,
            final_status,
            extra={
                "service": service,
                "event_type": "demo_completed",
                "incident_id": remediation_result.get("incident_id"),
            },
        )
        emit_system_event(
            event_type="demo_completed",
            category="demo",
            severity="info" if final_status == "resolved" else "warning",
            title=f"Autonomous demo completed for {service}",
            message=report["summary_text"],
            service=service,
            status="closed" if final_status == "resolved" else "open",
            payload={"run_id": run_id, "incident_id": remediation_result.get("incident_id"), "summary": report["summary_json"]},
        )
    except Exception as exc:
        logger.exception("Autonomous demo run failed")
        if state.system_store is not None:
            report = _build_demo_report(run_id, service, started_at, {"operator_summary": str(exc)}, platform)
            state.system_store.update_demo_run(
                run_id,
                status="failed",
                stage="failed",
                summary_text=f"Demo run failed: {exc}",
                summary_json={**report["summary_json"], "error": str(exc)},
                report_markdown=report["report_markdown"],
                report_json=report["report_json"],
            )
        emit_system_event(
            event_type="demo_failed",
            category="demo",
            severity="critical",
            title=f"Autonomous demo failed for {service}",
            message=str(exc),
            service=service,
            status="open",
            payload={"run_id": run_id},
        )
    finally:
        state.demo_task = None


def load_models():
    from ml.isolation_forest.inference import IFInference
    from ml.lstm.inference import LSTMInference

    inf = IFInference()
    inf.load()
    state.if_inference = inf
    logger.info("Isolation Forest model loaded from %s", inf.loaded_from)

    lstm = LSTMInference()
    lstm.load()
    state.lstm_inference = lstm
    logger.info("LSTM model loaded from %s", lstm.loaded_from)

    state.models_loaded = True
    try:
        state.correlation_engine = CorrelationEngine()
        logger.info("Correlation engine loaded")
    except Exception as exc:
        logger.warning("Correlation engine load failed: %s", exc)

    try:
        state.remediation_engine = RemediationEngine(
            score_provider=lambda: state.current_scores or compute_all_scores(),
            target_seconds=15,
            orchestrator_target=SETTINGS.orchestrator_target,
            kubernetes_namespace=SETTINGS.k8s_namespace,
            cooldown_s=SETTINGS.remediation_cooldown_s,
            lock_timeout_s=SETTINGS.remediation_lock_timeout_s,
            memory_limit=SETTINGS.incident_memory_limit,
            memory_retention_days=SETTINGS.incident_memory_retention_days,
        )
        logger.info("Remediation engine loaded")
    except Exception as exc:
        logger.warning("Remediation engine load failed: %s", exc)


def _score_status(combined: float) -> str:
    if combined < 0.4:
        return "normal"
    if combined < 0.7:
        return "warning"
    return "critical"


def _predict_failure_type(snapshot: Dict[str, Any], features: Dict[str, Any]) -> str:
    flags = set(snapshot.get("feature_flags", []) or features.get("feature_flags", []))
    mem = float(snapshot.get("mem_percent") or features.get("mem_percent_mean") or 0.0)
    cpu = float(snapshot.get("cpu_percent") or features.get("cpu_percent_mean") or 0.0)
    err = float(snapshot.get("error_rate") or features.get("error_rate_mean") or 0.0)
    timeouts = float(features.get("timeout_count_mean") or 0.0)
    if "memory_pressure" in flags or mem > 82:
        return "memory_leak"
    if "cpu_pressure" in flags or cpu > 82:
        return "cpu_starvation"
    if "network_pressure" in flags or timeouts > 0:
        return "network_latency"
    if "error_burst" in flags or err > 0.08:
        return "log_exception_storm"
    return "generic_anomaly"


def _predictive_actions(service: str, failure_type: str, score: float) -> List[Dict[str, Any]]:
    automatic = score >= SETTINGS.predictive_auto_action_threshold
    plans = {
        "memory_leak": [
            ("restart_service", "Refresh the workload before OOM kill and clear transient memory pressure."),
            ("isolate_service", "Contain repeat memory flaps if the service restarts but does not stabilize."),
        ],
        "cpu_starvation": [
            ("restart_service", "Recycle the hot workload and re-check CPU pressure on the next window."),
            ("reroute_service", "Shift demand only if a healthy alternative target exists."),
        ],
        "network_latency": [
            ("restart_dependency_chain", "Recover the suspected dependency path before the timeout spreads."),
            ("escalate_incident", "Escalate quickly if downstream services remain impacted."),
        ],
        "log_exception_storm": [
            ("restart_service", "Clear the failing process before exceptions propagate into user impact."),
            ("escalate_incident", "Escalate if the exception storm returns after one recovery attempt."),
        ],
        "generic_anomaly": [
            ("restart_service", "Apply the safest self-heal path before the anomaly hardens into a real outage."),
            ("escalate_incident", "Escalate if the predictive risk continues to rise."),
        ],
    }
    return [
        {
            "action": action,
            "summary": summary,
            "automatic": automatic and idx == 0,
            "target": service,
        }
        for idx, (action, summary) in enumerate(plans.get(failure_type, plans["generic_anomaly"]))
    ]


def _predictive_auto_action_allowed(snapshot: Dict[str, Any], failure_type: str, lstm_score: float) -> bool:
    if float(lstm_score) < SETTINGS.predictive_auto_action_threshold:
        return False
    if failure_type == "generic_anomaly":
        return False

    combined_score = float(snapshot.get("combined_score", 0.0) or 0.0)
    feature_flags = set(snapshot.get("feature_flags", []) or [])
    corroborating_flags = {
        "memory_pressure",
        "cpu_pressure",
        "network_pressure",
        "error_burst",
        "memory_high",
        "cpu_spike",
        "exceptions_detected",
        "error_rate_high",
    }
    return combined_score >= SETTINGS.predictive_alert_threshold and bool(feature_flags.intersection(corroborating_flags))


def _timeline_snapshot(limit: int = 10) -> List[Dict[str, Any]]:
    if state.system_store is None:
        return []
    return state.system_store.list_events(limit=limit)


def _has_usable_telemetry(features: Dict[str, Any], sequence_rows: List[Dict[str, Any]]) -> bool:
    if not sequence_rows:
        return False
    latest = sequence_rows[-1]
    signal_keys = [
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
        "total_log_lines",
        "trace_count",
    ]
    if any(float(latest.get(key, 0.0) or 0.0) > 0.0 for key in signal_keys):
        return True
    if float(features.get("cpu_percent_mean", 0.0) or 0.0) > 0.0:
        return True
    if float(features.get("mem_percent_mean", 0.0) or 0.0) > 0.0:
        return True
    if float(features.get("log_count_mean", 0.0) or 0.0) > 0.0:
        return True
    if float(latest.get("memory_limit_bytes", 0.0) or 0.0) > 0.0:
        return True
    if float(latest.get("trace_count", 0.0) or 0.0) > 0.0:
        return True
    return False


def compute_all_scores() -> Dict[str, Dict]:
    from anomaly_api.features import extract_features

    scores = {}
    state.current_model_insights = {}

    for svc in ALL_SERVICES:
        window = state.window_state.get_window(svc) if state.window_state else []
        features = extract_features(svc, window) if window else {}
        sequence_rows = build_sequence_rows(window, sequence_window=LSTM_SEQUENCE_WINDOW)
        sequence_array = rows_to_sequence_array(sequence_rows)
        if not len(sequence_rows):
            snapshot = {
                "if_score": None,
                "lstm_score": None,
                "combined_score": 0.0,
                "cpu_percent": 0.0,
                "mem_percent": 0.0,
                "feature_flags": [],
                "error_rate": 0.0,
                "warn_rate": 0.0,
                "log_count": 0.0,
                "model_state": "warming_up",
                "sequence_fill": 0.0,
            }
            state.current_model_insights[svc] = {
                "service": svc,
                "sequence_length": 0,
                "required_sequence_length": LSTM_SEQUENCE_WINDOW,
                "if_feature_count": len(IF_FEATURES),
                "sequence_feature_count": len(SEQUENCE_FEATURES),
                "status": "warming_up",
                "if_contributors": [],
                "sequence_highlights": [],
            }
            snapshot["status"] = "normal"
            scores[svc] = snapshot
            continue

        if not _has_usable_telemetry(features, sequence_rows):
            snapshot = {
                "if_score": None,
                "lstm_score": None,
                "combined_score": 0.0,
                "cpu_percent": features.get("cpu_percent_mean", 0.0),
                "mem_percent": features.get("mem_percent_mean", 0.0),
                "feature_flags": features.get("feature_flags", []),
                "error_rate": features.get("error_rate_mean", 0.0),
                "warn_rate": features.get("warn_rate_mean", 0.0),
                "log_count": features.get("log_count_mean", 0.0),
                "model_state": "warming_up",
                "sequence_fill": round(min(sequence_array.shape[0] / LSTM_SEQUENCE_WINDOW, 1.0), 3),
            }
            state.current_model_insights[svc] = {
                "service": svc,
                "sequence_length": int(sequence_array.shape[0]),
                "required_sequence_length": LSTM_SEQUENCE_WINDOW,
                "if_feature_count": len(IF_FEATURES),
                "sequence_feature_count": len(SEQUENCE_FEATURES),
                "status": "warming_up",
                "if_contributors": [],
                "sequence_highlights": top_sequence_features(sequence_rows[-1]) if sequence_rows else [],
                "latest_sequence_row": sequence_rows[-1] if sequence_rows else {},
            }
            snapshot["status"] = "normal"
            scores[svc] = snapshot
            continue

        if_vector = build_if_feature_vector(sequence_array)
        ordered_if_values = [if_vector[name] for name in IF_FEATURES]
        if_score = state.if_inference.score_vector(ordered_if_values)
        lstm_score = None
        if sequence_array.shape[0] >= LSTM_SEQUENCE_WINDOW:
            lstm_score = state.lstm_inference.predict(sequence_array[-LSTM_SEQUENCE_WINDOW:])
        combined = if_score if lstm_score is None else (0.45 * if_score + 0.55 * lstm_score)
        snapshot = {
            "if_score": round(if_score, 3),
            "lstm_score": round(lstm_score, 3) if lstm_score is not None else None,
            "combined_score": round(float(combined), 3),
            "cpu_percent": features.get("cpu_percent_mean", 0),
            "mem_percent": features.get("mem_percent_mean", 0),
            "feature_flags": features.get("feature_flags", []),
            "error_rate": features.get("error_rate_mean", 0),
            "warn_rate": features.get("warn_rate_mean", 0),
            "log_count": features.get("log_count_mean", 0),
            "model_state": "ready" if lstm_score is not None else "if_only",
            "sequence_fill": round(min(sequence_array.shape[0] / LSTM_SEQUENCE_WINDOW, 1.0), 3),
        }
        state.current_model_insights[svc] = {
            "service": svc,
            "sequence_length": int(sequence_array.shape[0]),
            "required_sequence_length": LSTM_SEQUENCE_WINDOW,
            "if_feature_count": len(IF_FEATURES),
            "sequence_feature_count": len(SEQUENCE_FEATURES),
            "status": snapshot["model_state"],
            "if_score": round(if_score, 4),
            "lstm_score": round(lstm_score, 4) if lstm_score is not None else None,
            "combined_score": round(float(combined), 4),
            "if_features": if_vector,
            "latest_sequence_row": sequence_rows[-1],
            "if_contributors": top_if_contributors(
                if_vector,
                state.if_inference.scaler_mean,
                state.if_inference.scaler_scale,
            ),
            "sequence_highlights": top_sequence_features(sequence_rows[-1]),
        }

        snapshot["status"] = _score_status(snapshot["combined_score"])
        scores[svc] = snapshot

    return scores


def get_root_cause_analysis(scores: Dict[str, Dict]) -> Dict:
    if state.correlation_engine is None:
        return {"root_cause": None, "confidence": 0.0, "failure_type": "none"}

    combined_scores = {svc: v["combined_score"] for svc, v in scores.items()}
    try:
        result = state.correlation_engine.analyze(combined_scores)
        return {
            "service": result.get("root_cause"),
            "confidence": result.get("confidence", 0.0),
            "failure_type": result.get("failure_type", "none"),
            "affected_services": result.get("affected_services", []),
            "propagation_path": result.get("propagation_path", []),
        }
    except Exception as exc:
        logger.error("Correlation engine error: %s", exc)
        return {"root_cause": None, "confidence": 0.0, "failure_type": "none"}


def get_recommendation(root_cause: Dict, scores: Dict) -> str:
    service = root_cause.get("service") or root_cause.get("root_cause")
    if not service:
        return "No anomalies detected. System operating normally."

    failure_type = root_cause.get("failure_type", "generic_anomaly")
    confidence = root_cause.get("confidence", 0.0)
    affected = root_cause.get("affected_services", [])

    recs = {
        "memory_leak": "Restart the leaking workload and contain repeat memory flaps if they recur.",
        "cpu_starvation": "Restart the saturated workload and monitor if CPU pressure remains elevated.",
        "network_latency": "Restart the dependency chain in order and escalate if downstream impact remains.",
        "generic_anomaly": "Run the staged remediation flow and fall back to containment on failure.",
        "none": "System operating normally.",
    }

    rec = recs.get(failure_type, recs["generic_anomaly"])
    if len(affected) > 1:
        rec += f" Affected services: {', '.join(affected[:3])}{'...' if len(affected) > 3 else ''}."
    rec += f" Confidence: {confidence:.0%}."
    return rec


def _recent_incident_map(limit: int = 25) -> Dict[str, Dict]:
    if state.remediation_engine is None:
        return {}
    latest: Dict[str, Dict] = {}
    for incident in state.remediation_engine.list_incident_history(limit=limit):
        service = incident["root_cause_service"]
        latest.setdefault(service, incident)
    return latest


def _build_evidence(service: str, failure_type: str, scores: Optional[Dict[str, Dict]] = None) -> Dict[str, Any]:
    from anomaly_api.features import extract_features

    scores = scores or state.current_scores or compute_all_scores()
    service_snapshot = dict(scores.get(service, {}))
    window = state.window_state.get_window(service) if state.window_state else []
    features = extract_features(service, window) if window else {}
    recent_logs = []
    if state.ingestion_pipeline and state.ingestion_pipeline._loki_cache:
        recent_logs = state.ingestion_pipeline._loki_cache.get(service, {}).get("recent_messages", [])[:3]

    summary = (
        f"Service {service} shows {failure_type}; score={service_snapshot.get('combined_score', 0):.3f}, "
        f"cpu={features.get('cpu_percent_mean', 0):.1f}, mem={features.get('mem_percent_mean', 0):.1f}."
    )

    return {
        "summary": summary,
        "service_snapshot": {
            **service_snapshot,
            "cpu_percent": features.get("cpu_percent_mean", service_snapshot.get("cpu_percent", 0)),
            "mem_percent": features.get("mem_percent_mean", service_snapshot.get("mem_percent", 0)),
            "error_rate_mean": features.get("error_rate_mean", service_snapshot.get("error_rate", 0)),
        },
        "feature_flags": features.get("feature_flags", []),
        "recent_logs": recent_logs,
    }


def _service_has_active_incident(service: str) -> bool:
    if state.remediation_engine is None:
        return False
    return any(incident.get("root_cause_service") == service for incident in state.remediation_engine.list_active_incidents())


def _runtime_failure_context(service: str, workload: Any, scores: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    snapshot = scores.get(service, {})
    metadata = workload.metadata or {}
    desired_replicas = int(metadata.get("desired_replicas", 0) or 0)
    ready_replicas = int(metadata.get("ready_replicas", 0) or 0)
    available_replicas = int(metadata.get("available_replicas", 0) or 0)
    if not workload.exists:
        degraded = True
        reasons = ["workload_missing"]
    else:
        degraded = False
        reasons = []
        if not workload.running:
            degraded = True
            reasons.append("workload_not_running")
        if not workload.healthy:
            degraded = True
            reasons.append("workload_unhealthy")
        if workload.oom_killed:
            degraded = True
            reasons.append("oom_killed")
        if int(workload.restart_count or 0) >= RUNTIME_RESTART_LOOP_THRESHOLD:
            degraded = True
            reasons.append("restart_loop_detected")

    if not degraded:
        return None

    feature_flags = list(snapshot.get("feature_flags", []) or [])
    affected_services = [service]
    if service in CRITICAL_SHARED_SERVICES:
        affected_services.extend(REVERSE_DEPENDENCY_GRAPH.get(service, []))
    affected_services = list(dict.fromkeys(affected_services))

    if service in CRITICAL_SHARED_SERVICES and len(affected_services) > 1:
        failure_type = "dependency_failure"
    elif workload.oom_killed or "memory_pressure" in feature_flags:
        failure_type = "memory_leak"
    elif "cpu_pressure" in feature_flags:
        failure_type = "cpu_starvation"
    elif "network_pressure" in feature_flags:
        failure_type = "network_latency"
    else:
        failure_type = "service_unhealthy"

    evidence = _build_evidence(service, failure_type, scores)
    runtime_snapshot = workload.to_dict()
    startup_grace = (
        desired_replicas > 0
        and workload.running
        and not workload.healthy
        and not workload.oom_killed
        and int(workload.restart_count or 0) == 0
        and ready_replicas < desired_replicas
        and available_replicas < desired_replicas
    )
    evidence["runtime_state"] = runtime_snapshot
    evidence["feature_flags"] = list(dict.fromkeys(feature_flags + reasons))
    if failure_type == "dependency_failure" and len(affected_services) > 1:
        downstream = ", ".join(affected_services[1:])
        evidence["summary"] = (
            f"Critical dependency {service} degraded and may impact downstream services: {downstream}."
        )
    else:
        evidence["summary"] = (
            f"Runtime health degraded on {service}: {', '.join(reasons)}; "
            f"status={runtime_snapshot.get('status')}, restarts={runtime_snapshot.get('restart_count', 0)}."
        )

    return {
        "failure_type": failure_type,
        "affected_services": affected_services,
        "evidence": evidence,
        "reasons": reasons,
        "workload": runtime_snapshot,
        "trigger_count": RUNTIME_STARTUP_GRACE_POLLS if startup_grace else RUNTIME_FAILURE_TRIGGER_COUNT,
        "startup_grace": startup_grace,
    }


async def monitor_runtime_workloads(scores: Dict[str, Dict]) -> None:
    if state.remediation_engine is None:
        return
    automation_warmed_up = (time.time() - state.started_at) >= RUNTIME_AUTOMATION_WARMUP_S

    for svc in ALL_SERVICES:
        try:
            workload = state.remediation_engine.orchestrator.inspect_service(svc)
        except Exception as exc:
            logger.debug("Runtime workload inspection failed for %s: %s", svc, exc)
            continue

        tracker = state.runtime_health.get(svc, {})
        context = _runtime_failure_context(svc, workload, scores)

        if context is None:
            if tracker.get("degraded"):
                resolved_at = utc_now_iso()
                closed_incident = None
                if tracker.get("incident_id") and state.remediation_engine is not None:
                    closed_incident = state.remediation_engine.close_recovered_incident(
                        svc,
                        note=(
                            f"Runtime health recovered automatically at {resolved_at}; "
                            f"workload status returned to {workload.status}."
                        ),
                    )
                emit_system_event(
                    event_type="runtime_recovered",
                    category="runtime",
                    severity="info",
                    title=f"Runtime recovered for {svc}",
                    message=(
                        f"{svc} recovered after {tracker.get('count', 1)} unhealthy polls. "
                        f"Current status is {workload.status}."
                    ),
                    service=svc,
                    status="closed",
                    payload={
                        "service": svc,
                        "resolved_at": resolved_at,
                        "previous_incident_id": tracker.get("incident_id"),
                        "closed_incident": closed_incident,
                        "workload": workload.to_dict(),
                    },
                )
            state.runtime_health.pop(svc, None)
            continue

        count = int(tracker.get("count", 0)) + 1 if tracker.get("degraded") else 1
        updated_tracker = {
            "degraded": True,
            "count": count,
            "first_detected_at": tracker.get("first_detected_at", utc_now_iso()),
            "updated_at": utc_now_iso(),
            "incident_triggered": bool(tracker.get("incident_triggered", False)),
            "incident_id": tracker.get("incident_id"),
            "failure_type": context["failure_type"],
            "reasons": context["reasons"],
        }

        if not tracker.get("degraded"):
            emit_system_event(
                event_type="runtime_degradation_detected",
                category="runtime",
                severity="critical" if context["failure_type"] == "dependency_failure" else "warning",
                title=f"Runtime degradation detected on {svc}",
                message=(
                    f"{svc} became unhealthy: {', '.join(context['reasons']) or 'runtime degradation detected'}."
                ),
                service=svc,
                status="open",
                payload={
                    "service": svc,
                    "failure_type": context["failure_type"],
                    "affected_services": context["affected_services"],
                    "workload": context["workload"],
                },
            )

        should_trigger = (
            automation_warmed_up
            and
            count >= int(context.get("trigger_count", RUNTIME_FAILURE_TRIGGER_COUNT))
            and not updated_tracker["incident_triggered"]
            and not _service_has_active_incident(svc)
        )
        if should_trigger:
            emit_system_event(
                event_type="runtime_auto_remediation_started",
                category="runtime",
                severity="warning",
                title=f"Runtime remediation started for {svc}",
                message=(
                    f"Persistent runtime degradation on {svc} triggered automated remediation "
                    f"for {context['failure_type']}."
                ),
                service=svc,
                status="open",
                payload={
                    "service": svc,
                    "failure_type": context["failure_type"],
                    "affected_services": context["affected_services"],
                    "reasons": context["reasons"],
                },
            )
            result = await asyncio.to_thread(
                state.remediation_engine.remediate,
                service=svc,
                failure_type=context["failure_type"],
                severity="critical" if context["failure_type"] == "dependency_failure" else "warning",
                affected_services=context["affected_services"],
                evidence=context["evidence"],
            )
            updated_tracker["incident_triggered"] = True
            updated_tracker["incident_id"] = result.get("incident_id")
            emit_system_event(
                event_type="runtime_auto_remediation_finished",
                category="runtime",
                severity="info" if result.get("status") == "resolved" else "warning",
                title=f"Runtime remediation finished for {svc}",
                message=result.get("operator_summary") or f"Automated remediation finished for {svc}.",
                service=svc,
                status="closed" if result.get("status") == "resolved" else "open",
                payload={
                    "service": svc,
                    "failure_type": context["failure_type"],
                    "result": result,
                },
            )

        state.runtime_health[svc] = updated_tracker


async def process_predictive_alerts(scores: Dict[str, Dict]) -> None:
    from anomaly_api.features import extract_features

    now = time.time()
    next_alerts: Dict[str, Dict[str, Any]] = {}

    for svc, snapshot in scores.items():
        lstm_score = snapshot.get("lstm_score")
        runtime_ready = True
        if state.remediation_engine is not None:
            try:
                workload = state.remediation_engine.orchestrator.inspect_service(svc)
                runtime_ready = bool(workload.running and workload.healthy)
            except Exception as exc:
                logger.debug("Predictive runtime check failed for %s: %s", svc, exc)
        if snapshot.get("model_state") != "ready" or lstm_score is None:
            existing = state.predictive_alerts.get(svc)
            if existing and existing.get("status") != "resolved":
                resolved = {
                    **existing,
                    "status": "resolved",
                    "resolved_at": utc_now_iso(),
                    "message": "Predictive window cooled down before a hard failure formed.",
                }
                next_alerts[svc] = resolved
                emit_system_event(
                    event_type="predictive_alert_resolved",
                    category="prediction",
                    severity="info",
                    title=f"Predictive risk cleared for {svc}",
                    message=resolved["message"],
                    service=svc,
                    status="closed",
                    payload=resolved,
                )
            continue

        if not runtime_ready:
            existing = state.predictive_alerts.get(svc)
            if existing and existing.get("status") != "resolved":
                resolved = {
                    **existing,
                    "status": "resolved",
                    "resolved_at": utc_now_iso(),
                    "message": "Predictive alerts are suppressed while the workload is not yet healthy.",
                }
                next_alerts[svc] = resolved
                emit_system_event(
                    event_type="predictive_alert_resolved",
                    category="prediction",
                    severity="info",
                    title=f"Predictive risk gated for {svc}",
                    message=resolved["message"],
                    service=svc,
                    status="closed",
                    payload=resolved,
                )
            continue

        if float(lstm_score) < SETTINGS.predictive_alert_threshold * 0.85:
            existing = state.predictive_alerts.get(svc)
            if existing and existing.get("status") != "resolved":
                resolved = {
                    **existing,
                    "status": "resolved",
                    "resolved_at": utc_now_iso(),
                    "message": "LSTM risk dropped below the pre-failure threshold.",
                }
                next_alerts[svc] = resolved
                emit_system_event(
                    event_type="predictive_alert_resolved",
                    category="prediction",
                    severity="info",
                    title=f"Predictive risk cooled for {svc}",
                    message=resolved["message"],
                    service=svc,
                    status="closed",
                    payload=resolved,
                )
            continue

        window = state.window_state.get_window(svc) if state.window_state else []
        features = extract_features(svc, window) if window else {}
        failure_type = _predict_failure_type(snapshot, features)
        actions = _predictive_actions(svc, failure_type, float(lstm_score))
        severity = "critical" if float(lstm_score) >= SETTINGS.predictive_auto_action_threshold else "warning"
        existing = state.predictive_alerts.get(svc)
        auto_action = actions[0]["action"] if actions else "restart_service"
        cooldown_until = state.predictive_cooldowns.get(svc, 0.0)
        can_auto_act = (
            _predictive_auto_action_allowed(snapshot, failure_type, float(lstm_score))
            and now >= cooldown_until
            and not _service_has_active_incident(svc)
            and state.remediation_engine is not None
        )

        alert = {
            "service": svc,
            "status": "mitigating" if can_auto_act else "active",
            "severity": severity,
            "failure_type": failure_type,
            "lstm_score": round(float(lstm_score), 4),
            "combined_score": round(float(snapshot.get("combined_score", 0.0)), 4),
            "predicted_window": f"next ~{LSTM_SEQUENCE_WINDOW * 5} seconds",
            "detected_at": existing.get("detected_at") if existing else utc_now_iso(),
            "updated_at": utc_now_iso(),
            "feature_flags": snapshot.get("feature_flags", []),
            "preventive_actions": actions,
            "message": (
                f"LSTM predicts a likely {failure_type.replace('_', ' ')} on {svc}. "
                f"Risk is {round(float(lstm_score) * 100)}% before the service crosses the incident threshold."
            ),
            "auto_action": {
                "eligible": can_auto_act,
                "action": auto_action,
                "cooldown_until": existing.get("auto_action", {}).get("cooldown_until") if existing else None,
                "last_result": existing.get("auto_action", {}).get("last_result") if existing else None,
            },
        }

        is_new_or_changed = (
            existing is None
            or existing.get("failure_type") != failure_type
            or abs(float(existing.get("lstm_score", 0.0)) - float(lstm_score)) >= 0.05
            or existing.get("status") == "resolved"
        )
        if is_new_or_changed:
            emit_system_event(
                event_type="predictive_alert",
                category="prediction",
                severity=severity,
                title=f"Pre-failure alert on {svc}",
                message=alert["message"],
                service=svc,
                status="open",
                payload=alert,
            )

        if can_auto_act:
            state.predictive_cooldowns[svc] = now + SETTINGS.predictive_action_cooldown_s
            alert["auto_action"]["cooldown_until"] = datetime.fromtimestamp(
                state.predictive_cooldowns[svc], tz=timezone.utc
            ).isoformat()
            emit_system_event(
                event_type="preventive_action_started",
                category="prediction",
                severity="warning",
                title=f"Preventive action started for {svc}",
                message=f"Executing {auto_action} before the predicted failure hardens.",
                service=svc,
                status="open",
                payload={"service": svc, "action": auto_action, "failure_type": failure_type},
            )
            proposal = ActionProposal(
                source="rule",
                proposed_action=auto_action,
                target=svc,
                confidence=float(lstm_score),
                rationale=f"Predictive prevention for {failure_type}",
            )
            result = await asyncio.to_thread(
                state.remediation_engine.remediate,
                service=svc,
                failure_type=failure_type,
                severity="warning",
                affected_services=[svc],
                evidence=_build_evidence(svc, failure_type, scores),
                proposal=proposal,
            )
            alert["status"] = "mitigated" if result.get("status") == "resolved" else "manual_required"
            alert["auto_action"]["last_result"] = {
                "status": result.get("status"),
                "incident_id": result.get("incident_id"),
                "operator_summary": result.get("operator_summary"),
            }
            emit_system_event(
                event_type="preventive_action_finished",
                category="prediction",
                severity="info" if result.get("status") == "resolved" else "warning",
                title=f"Preventive action finished for {svc}",
                message=result.get("operator_summary") or f"{auto_action} completed for {svc}",
                service=svc,
                status="closed" if result.get("status") == "resolved" else "open",
                payload={"service": svc, "action": auto_action, "result": result},
            )

        next_alerts[svc] = alert

    state.predictive_alerts = next_alerts


async def update_scores_loop():
    while True:
        try:
            scores = compute_all_scores()
            state.current_scores = scores
            state.last_update = time.time()
            await process_predictive_alerts(scores)
            await monitor_runtime_workloads(scores)

            state.history.append(
                {
                    "timestamp": utc_now_iso(),
                    "ts_epoch": time.time(),
                    "scores": {svc: v["combined_score"] for svc, v in scores.items()},
                }
            )
        except Exception as exc:
            logger.error("Score update error: %s", exc)

        await asyncio.sleep(2)


app = FastAPI(
    title="AI Observability Platform",
    description="Anomaly detection and self-healing for microservices",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=SETTINGS.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Observability Platform...")
    state.started_at = time.time()
    if SETTINGS.auth_enabled and not SETTINGS.api_token:
        raise RuntimeError("AEGIS auth is enabled but AEGIS_API_TOKEN is not configured")
    init_system_store()
    emit_system_event(
        event_type="platform_start",
        category="system",
        severity="info",
        title="AEGIS startup",
        message="Backend startup sequence started.",
        status="closed",
        payload={"runtime_mode": SETTINGS.runtime_mode, "environment": SETTINGS.environment_name},
    )
    load_models()

    from anomaly_api.ingestion import SlidingWindowState, IngestionPipeline

    state.window_state = SlidingWindowState()
    state.ingestion_pipeline = IngestionPipeline(state.window_state)
    state.ingestion_pipeline.start()

    asyncio.create_task(update_scores_loop())
    logger.info("Platform started. models_loaded=%s", state.models_loaded)
    emit_system_event(
        event_type="platform_ready",
        category="system",
        severity="info",
        title="AEGIS ready",
        message="Backend started, models loaded, and ingestion loop is running.",
        status="closed",
        payload={"models_loaded": state.models_loaded, "orchestrator": SETTINGS.orchestrator_target},
    )


def require_operator_access(x_aegis_token: str = Header(default="")) -> None:
    require_operator_token(SETTINGS, x_aegis_token)


class IngestPayload(BaseModel):
    metrics: List[Dict[str, Any]] = Field(default_factory=list)
    logs: List[Dict[str, Any]] = Field(default_factory=list)


class ActionProposalPayload(BaseModel):
    source: str = "ai"
    proposed_action: str
    target: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    rationale: str = ""
    containment_preference: Optional[str] = None

    def to_action_proposal(self) -> ActionProposal:
        return ActionProposal(
            source=self.source,
            proposed_action=self.proposed_action,
            target=self.target,
            parameters=self.parameters,
            confidence=self.confidence,
            rationale=self.rationale,
            containment_preference=self.containment_preference,
        )


class RemediatePayload(BaseModel):
    service: str
    failure_type: str = "generic_anomaly"
    severity: str = "warning"
    affected_services: List[str] = Field(default_factory=list)
    evidence: Dict[str, Any] = Field(default_factory=dict)
    proposal: Optional[ActionProposalPayload] = None


class DemoRunPayload(BaseModel):
    service: str = "recommendationservice"
    owner: str = "operator"


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "runtime_mode": SETTINGS.runtime_mode,
        "environment": SETTINGS.environment_name,
        "orchestrator": state.remediation_engine.orchestrator.platform if state.remediation_engine else None,
        "models_loaded": state.models_loaded,
        "model_dir": SETTINGS.model_dir,
        "system_db": SETTINGS.system_db_path,
        "services_tracked": len(ALL_SERVICES),
        "last_update": datetime.fromtimestamp(state.last_update, tz=timezone.utc).isoformat() if state.last_update else None,
        "active_incidents": len(state.remediation_engine.list_active_incidents()) if state.remediation_engine else 0,
    }


@app.get("/status")
async def status():
    scores = state.current_scores or compute_all_scores()
    root_cause = get_root_cause_analysis(scores)
    recommendation = get_recommendation(root_cause, scores)

    alerts = [
        {
            "service": svc,
            "score": v["combined_score"],
            "status": v["status"],
            "if_score": v["if_score"],
            "lstm_score": v["lstm_score"],
            "timestamp": utc_now_iso(),
        }
        for svc, v in scores.items()
        if v["combined_score"] > 0.7
    ]

    return {
        "timestamp": utc_now_iso(),
        "services": scores,
        "root_cause": root_cause,
        "alerts": alerts,
        "predictive_alerts": list(state.predictive_alerts.values()),
        "timeline": _timeline_snapshot(limit=8),
        "demo_run": latest_demo_run(),
        "recommendation": recommendation,
        "active_incidents": state.remediation_engine.list_active_incidents() if state.remediation_engine else [],
        "recent_incidents": state.remediation_engine.list_incident_history(limit=10) if state.remediation_engine else [],
    }


@app.post("/ingest", dependencies=[Depends(require_operator_access)])
async def ingest(payload: IngestPayload):
    from anomaly_api.ingestion import Observation

    updated = 0

    for metric in payload.metrics:
        svc = metric.get("service_name") or metric.get("service")
        if not svc or svc not in ALL_SERVICES:
            continue

        observation = Observation(
            timestamp=time.time(),
            service=svc,
            cpu_percent=float(metric.get("cpu_percent", metric.get("cpu_usage_percent", 0.0))),
            mem_percent=float(metric.get("mem_percent", metric.get("memory_usage_percent", 0.0))),
            mem_bytes=float(metric.get("mem_bytes", metric.get("memory_usage_bytes", 0.0))),
            mem_limit_bytes=float(metric.get("mem_limit_bytes", metric.get("memory_limit_bytes", 0.0))),
            net_rx_mbps=float(metric.get("net_rx_mbps", metric.get("network_rx_bytes_per_sec", 0.0))) / 1e6,
            net_tx_mbps=float(metric.get("net_tx_mbps", metric.get("network_tx_bytes_per_sec", 0.0))) / 1e6,
            block_read_mbps=float(metric.get("block_read_mbps", metric.get("fs_reads_per_sec", 0.0))) / 1e6,
            block_write_mbps=float(metric.get("block_write_mbps", metric.get("fs_writes_per_sec", 0.0))) / 1e6,
            log_count=int(metric.get("log_count", metric.get("total_log_lines", 0))),
            error_count=int(metric.get("error_count", 0)),
            warn_count=int(metric.get("warn_count", metric.get("warning_count", 0))),
            info_count=int(metric.get("info_count", 0)),
            error_rate=float(metric.get("error_rate", metric.get("error_rate_logs", 0.0))),
            warn_rate=float(metric.get("warn_rate", metric.get("warning_rate_logs", 0.0))),
            exception_count=int(metric.get("exception_count", 0)),
            timeout_count=int(metric.get("timeout_count", 0)),
            template_entropy=float(metric.get("template_entropy", 0.0)),
            log_volume_per_sec=float(metric.get("log_volume_per_sec", 0.0)),
            unique_templates=int(metric.get("unique_templates", 0)),
            new_templates_seen=int(metric.get("new_templates_seen", 0)),
            oom_mention_count=int(metric.get("oom_mention_count", 0)),
            avg_message_length=float(metric.get("avg_message_length", 0.0)),
            log_volume_change_pct=float(metric.get("log_volume_change_pct", 0.0)),
            trace_count=int(metric.get("trace_count", 0)),
            trace_error_count=int(metric.get("trace_error_count", 0)),
            trace_duration_mean=float(metric.get("trace_duration_mean", 0.0)),
        )
        if state.window_state:
            state.window_state.push(observation)
        updated += 1

    if updated:
        state.current_scores = compute_all_scores()

    return {"status": "ok", "updated_services": updated}


@app.post("/decision/validate", dependencies=[Depends(require_operator_access)])
async def validate_decision(payload: RemediatePayload):
    if state.remediation_engine is None:
        raise HTTPException(503, "Remediation engine is not available")

    proposal = payload.proposal.to_action_proposal() if payload.proposal else ActionProposal(
        source="rule",
        proposed_action="restart_service",
        target=payload.service,
        rationale="Fallback deterministic action",
    )
    evidence = _build_evidence(payload.service, payload.failure_type, state.current_scores)
    evidence.update(payload.evidence)
    return state.remediation_engine.validate_proposal(
        service=payload.service,
        failure_type=payload.failure_type,
        proposal=proposal,
        severity=payload.severity,
        affected_services=payload.affected_services or [payload.service],
        evidence=evidence,
    )


@app.post("/remediate", dependencies=[Depends(require_operator_access)])
async def remediate(payload: RemediatePayload):
    if state.remediation_engine is None:
        raise HTTPException(503, "Remediation engine is not available")

    proposal = payload.proposal.to_action_proposal() if payload.proposal else None
    evidence = _build_evidence(payload.service, payload.failure_type, state.current_scores)
    evidence.update(payload.evidence)
    result = state.remediation_engine.remediate(
        service=payload.service,
        failure_type=payload.failure_type,
        severity=payload.severity,
        affected_services=payload.affected_services or [payload.service],
        evidence=evidence,
        proposal=proposal,
    )
    emit_system_event(
        event_type="manual_remediation",
        category="remediation",
        severity="info" if result.get("status") == "resolved" else "warning",
        title=f"Remediation finished for {payload.service}",
        message=result.get("operator_summary") or f"Remediation finished for {payload.service}",
        service=payload.service,
        status="closed" if result.get("status") == "resolved" else "open",
        payload={"service": payload.service, "failure_type": payload.failure_type, "result": result},
    )

    return {
        "service": payload.service,
        "failure_type": payload.failure_type,
        "severity": payload.severity,
        "result": result,
        "timestamp": utc_now_iso(),
    }


@app.post("/demo/run", dependencies=[Depends(require_operator_access)])
async def demo_run(payload: DemoRunPayload):
    if state.remediation_engine is None or state.system_store is None:
        raise HTTPException(503, "Demo control plane is not available")
    if payload.service not in ALL_SERVICES:
        raise HTTPException(404, f"Unknown service: {payload.service}")

    latest = latest_demo_run()
    if state.demo_task is not None and not state.demo_task.done():
        raise HTTPException(409, "A demo run is already active")
    if latest and latest.get("status") == "running":
        raise HTTPException(409, "The latest demo run is still in progress")

    run = state.system_store.start_demo_run(
        service=payload.service,
        platform=state.remediation_engine.orchestrator.platform,
        started_by=payload.owner,
        attack_action="stop_service",
    )
    state.demo_task = asyncio.create_task(run_autonomous_demo(run["id"], payload.service, payload.owner))
    return {"demo_run": run, "timestamp": utc_now_iso()}


@app.get("/demo/latest")
async def demo_latest():
    return {"demo_run": latest_demo_run(), "timestamp": utc_now_iso()}


@app.get("/demo/report/{run_id}")
async def demo_report(run_id: int, format: str = Query(default="markdown", pattern="^(markdown|json)$")):
    run = latest_demo_run() if run_id == -1 else (state.system_store.get_demo_run(run_id) if state.system_store else None)
    if run is None:
        raise HTTPException(404, f"Demo run {run_id} not found")
    if format == "json":
        return run.get("report_json") or {"summary": run.get("summary_json", {})}
    return PlainTextResponse(run.get("report_markdown") or run.get("summary_text", "Demo report unavailable.\n"), media_type="text/markdown")


@app.get("/incidents/active")
async def active_incidents():
    incidents = state.remediation_engine.list_active_incidents() if state.remediation_engine else []
    return {"count": len(incidents), "incidents": incidents, "timestamp": utc_now_iso()}


@app.get("/incidents/history")
async def incident_history(limit: int = Query(default=20, ge=1, le=100)):
    incidents = state.remediation_engine.list_incident_history(limit=limit) if state.remediation_engine else []
    return {"count": len(incidents), "incidents": incidents, "timestamp": utc_now_iso()}


@app.post("/incidents/{incident_id}/acknowledge", dependencies=[Depends(require_operator_access)])
async def acknowledge_incident(incident_id: str, owner: str = Query(default="operator")):
    if state.remediation_engine is None:
        raise HTTPException(503, "Remediation engine is not available")
    try:
        incident = state.remediation_engine.acknowledge_incident(incident_id, owner=owner)
    except KeyError as exc:
        raise HTTPException(404, str(exc))
    emit_system_event(
        event_type="incident_acknowledged",
        category="remediation",
        severity="info",
        title=f"Incident acknowledged by {owner}",
        message=f"Incident {incident_id} is now owned by {owner}.",
        service=incident.get("root_cause_service"),
        status="closed",
        payload=incident,
    )
    return {"incident": incident, "timestamp": utc_now_iso()}


@app.get("/incidents/similar")
async def similar_incidents(service: str, failure_type: str, limit: int = Query(default=5, ge=1, le=20)):
    if state.remediation_engine is None:
        raise HTTPException(503, "Remediation engine is not available")

    evidence = _build_evidence(service, failure_type, state.current_scores)
    matches = state.remediation_engine.similar_incidents(
        service=service,
        failure_type=failure_type,
        feature_flags=evidence.get("feature_flags", []),
        metric_signature=evidence.get("service_snapshot", {}),
        evidence_summary=evidence.get("summary", ""),
        limit=limit,
    )
    return {"count": len(matches), "matches": matches, "timestamp": utc_now_iso()}


@app.get("/history")
async def history():
    return {"count": len(state.history), "snapshots": list(state.history)}


@app.get("/alerts")
async def alerts():
    if not state.current_scores:
        return {"alerts": [], "count": 0}

    active_alerts = [
        {
            "service": svc,
            "score": v["combined_score"],
            "status": v["status"],
            "if_score": v["if_score"],
            "lstm_score": v["lstm_score"],
            "timestamp": utc_now_iso(),
        }
        for svc, v in state.current_scores.items()
        if v["combined_score"] > 0.7
    ]
    active_alerts.sort(key=lambda x: x["score"], reverse=True)

    return {"alerts": active_alerts, "count": len(active_alerts), "timestamp": utc_now_iso()}


@app.get("/topology")
async def topology():
    from anomaly_api.features import extract_features

    scores = state.current_scores or compute_all_scores()
    avg_score = sum(v["combined_score"] for v in scores.values()) / max(len(scores), 1)
    health_score = round(100 - avg_score * 100)

    momentum = 0.0
    if len(state.history) >= 2:
        recent = list(state.history)[-10:]
        if len(recent) >= 2:
            first_avg = sum(recent[0]["scores"].values()) / max(len(recent[0]["scores"]), 1)
            last_avg = sum(recent[-1]["scores"].values()) / max(len(recent[-1]["scores"]), 1)
            dt_minutes = (
                recent[-1].get("ts_epoch", time.time()) - recent[0].get("ts_epoch", time.time())
            ) / 60.0
            if dt_minutes > 0:
                momentum = round((last_avg - first_avg) / dt_minutes * 100, 2)

    recent_incident_map = _recent_incident_map()
    service_data = {}
    for svc in ALL_SERVICES:
        snapshot = scores.get(svc, {})
        window = state.window_state.get_window(svc) if state.window_state else []
        features = extract_features(svc, window) if window else {}

        recent_logs = []
        if state.ingestion_pipeline and state.ingestion_pipeline._loki_cache:
            recent_logs = state.ingestion_pipeline._loki_cache.get(svc, {}).get("recent_messages", [])[:3]

        similar = []
        if state.remediation_engine is not None:
            similar = state.remediation_engine.similar_incidents(
                service=svc,
                failure_type=snapshot.get("failure_type", "generic_anomaly"),
                feature_flags=features.get("feature_flags", []),
                metric_signature={
                    "combined_score": snapshot.get("combined_score", 0.0),
                    "cpu_percent": features.get("cpu_percent_mean", 0.0),
                    "mem_percent": features.get("mem_percent_mean", 0.0),
                },
                evidence_summary=" ".join(recent_logs),
                limit=3,
            )

        service_data[svc] = {
            **snapshot,
            "cpu_mean": round(features.get("cpu_percent_mean", 0), 2),
            "cpu_max": round(features.get("cpu_percent_max", 0), 2),
            "cpu_std": round(features.get("cpu_percent_std", 0), 2),
            "cpu_slope": round(features.get("cpu_percent_slope", 0), 4),
            "mem_mean": round(features.get("mem_percent_mean", 0), 2),
            "mem_max": round(features.get("mem_percent_max", 0), 2),
            "net_rx_mean": round(features.get("net_rx_mbps_mean", 0), 4),
            "net_tx_mean": round(features.get("net_tx_mbps_mean", 0), 4),
            "error_rate_mean": round(features.get("error_rate_mean", 0), 4),
            "error_rate_slope": round(features.get("error_rate_slope", 0), 6),
            "warn_rate_mean": round(features.get("warn_rate_mean", 0), 4),
            "log_count_mean": round(features.get("log_count_mean", 0), 1),
            "log_volume_per_sec": round(features.get("log_volume_per_sec_mean", 0), 2),
            "exception_count_mean": round(features.get("exception_count_mean", 0), 2),
            "template_entropy_mean": round(features.get("template_entropy_mean", 0), 3),
            "cpu_pressure": round(features.get("cpu_pressure", 0), 3),
            "memory_pressure": round(features.get("memory_pressure", 0), 3),
            "network_pressure": round(features.get("network_pressure", 0), 4),
            "error_momentum": round(features.get("error_momentum", 0), 6),
            "log_anomaly_score": round(features.get("log_anomaly_score", 0), 4),
            "io_pressure": round(features.get("io_pressure", 0), 4),
            "window_size": len(window),
            "window_filled": len(window) >= 20,
            "feature_flags": features.get("feature_flags", []),
            "recent_logs": recent_logs,
            "latest_incident": recent_incident_map.get(svc),
            "similar_incidents": similar,
            "predictive_alert": state.predictive_alerts.get(svc),
            "ml": state.current_model_insights.get(svc, {}),
        }

    root_cause = get_root_cause_analysis(scores)
    recommendation = get_recommendation(root_cause, scores)

    return {
        "timestamp": utc_now_iso(),
        "environment": SETTINGS.environment_name,
        "runtime_mode": SETTINGS.runtime_mode,
        "health_score": health_score,
        "failure_momentum": momentum,
        "services": service_data,
        "dependency_graph": DEPENDENCY_GRAPH,
        "root_cause": root_cause,
        "alerts": [{"service": svc, **v} for svc, v in scores.items() if v.get("combined_score", 0) > 0.7],
        "predictive_alerts": list(state.predictive_alerts.values()),
        "timeline": _timeline_snapshot(limit=12),
        "demo_run": latest_demo_run(),
        "system_summary": state.system_store.summarize() if state.system_store else {},
        "recommendation": recommendation,
        "active_incidents": state.remediation_engine.list_active_incidents() if state.remediation_engine else [],
        "recent_incidents": state.remediation_engine.list_incident_history(limit=12) if state.remediation_engine else [],
    }


@app.get("/infrastructure")
async def infrastructure():
    topology_payload = await topology()
    history_payload = list(state.history)
    payload = build_infrastructure_payload(
        settings=SETTINGS,
        topology=topology_payload,
        history=history_payload,
        remediation_engine=state.remediation_engine,
    )
    payload["timestamp"] = utc_now_iso()
    return payload


@app.get("/events")
async def events(limit: int = Query(default=100, ge=1, le=500), category: Optional[str] = Query(default=None)):
    events_payload = state.system_store.list_events(limit=limit, category=category) if state.system_store else []
    return {"count": len(events_payload), "events": events_payload, "timestamp": utc_now_iso()}


@app.get("/logs")
async def logs(
    limit: int = Query(default=200, ge=1, le=1000),
    level: Optional[str] = Query(default=None),
    query: str = Query(default=""),
):
    logs_payload = state.system_store.list_logs(limit=limit, level=level, query=query) if state.system_store else []
    return {"count": len(logs_payload), "logs": logs_payload, "timestamp": utc_now_iso()}


@app.get("/logs/report")
async def logs_report(
    format: str = Query(default="markdown", pattern="^(markdown|json)$"),
    event_limit: int = Query(default=160, ge=10, le=500),
    log_limit: int = Query(default=240, ge=10, le=1000),
):
    if state.system_store is None:
        if format == "json":
            return {"generated_at": utc_now_iso(), "summary": {}, "events": [], "logs": []}
        return PlainTextResponse("AEGIS report unavailable: system store is not initialized.\n", media_type="text/markdown")

    if format == "json":
        return state.system_store.build_report(event_limit=event_limit, log_limit=log_limit)

    return PlainTextResponse(
        state.system_store.render_markdown_report(event_limit=event_limit, log_limit=log_limit),
        media_type="text/markdown",
    )


@app.get("/ml/insights")
async def ml_insights():
    scores = state.current_scores or compute_all_scores()
    services = []
    history_tail = list(state.history)[-30:]
    score_history: Dict[str, List[Dict[str, Any]]] = {svc: [] for svc in ALL_SERVICES}
    for svc in ALL_SERVICES:
        snapshot = scores.get(svc, {})
        insight = state.current_model_insights.get(svc, {})
        predictive_alert = state.predictive_alerts.get(svc)
        for item in history_tail:
            score_history[svc].append(
                {
                    "timestamp": item.get("timestamp"),
                    "score": item.get("scores", {}).get(svc, 0),
                }
            )
        services.append(
            {
                "service": svc,
                "status": snapshot.get("status", "unknown"),
                "model_state": snapshot.get("model_state", "unknown"),
                "if_score": snapshot.get("if_score"),
                "lstm_score": snapshot.get("lstm_score"),
                "combined_score": snapshot.get("combined_score"),
                "sequence_fill": snapshot.get("sequence_fill", 0.0),
                "feature_flags": snapshot.get("feature_flags", []),
                "if_contributors": insight.get("if_contributors", []),
                "sequence_highlights": insight.get("sequence_highlights", []),
                "latest_sequence_row": insight.get("latest_sequence_row", {}),
                "predictive_alert": predictive_alert,
                "score_history": score_history[svc],
            }
        )
    services.sort(key=lambda item: item.get("combined_score", 0) or 0, reverse=True)
    ready_services = [service for service in services if service.get("model_state") == "ready"]
    lstm_ready = [service for service in services if isinstance(service.get("lstm_score"), (float, int))]
    if_ready = [service for service in services if isinstance(service.get("if_score"), (float, int))]
    top_lstm = max(lstm_ready, key=lambda item: item.get("lstm_score", 0), default=None)
    top_if = max(if_ready, key=lambda item: item.get("if_score", 0), default=None)
    aggregate_contributors: Dict[str, float] = {}
    for service in services:
        for contributor in service.get("if_contributors", [])[:5]:
            feature = contributor.get("feature")
            z_score = float(contributor.get("z_score", 0.0) or 0.0)
            if feature:
                aggregate_contributors[feature] = aggregate_contributors.get(feature, 0.0) + abs(z_score)
    dominant_features = [
        {"feature": feature, "weight": round(weight, 3)}
        for feature, weight in sorted(aggregate_contributors.items(), key=lambda item: item[1], reverse=True)[:10]
    ]
    return {
        "timestamp": utc_now_iso(),
        "models": {
            "isolation_forest": state.if_inference.metadata() if state.if_inference else {"loaded": False},
            "lstm": state.lstm_inference.metadata() if state.lstm_inference else {"loaded": False},
        },
        "required_sequence_length": LSTM_SEQUENCE_WINDOW,
        "summary": {
            "service_count": len(services),
            "ready_service_count": len(ready_services),
            "predictive_alert_count": len(state.predictive_alerts),
            "highest_combined_service": services[0]["service"] if services else None,
            "highest_combined_score": services[0].get("combined_score") if services else None,
            "highest_lstm_service": top_lstm["service"] if top_lstm else None,
            "highest_lstm_score": top_lstm.get("lstm_score") if top_lstm else None,
            "highest_if_service": top_if["service"] if top_if else None,
            "highest_if_score": top_if.get("if_score") if top_if else None,
        },
        "predictive_alerts": list(state.predictive_alerts.values()),
        "dominant_features": dominant_features,
        "services": services,
    }


@app.get("/window/{service}")
async def get_window(service: str):
    if service not in ALL_SERVICES:
        raise HTTPException(404, f"Unknown service: {service}")

    window = state.window_state.get_window(service) if state.window_state else []
    return {
        "service": service,
        "observations": [
            {
                "timestamp": obs.timestamp,
                "cpu_percent": obs.cpu_percent,
                "mem_percent": obs.mem_percent,
                "net_rx_mbps": obs.net_rx_mbps,
                "net_tx_mbps": obs.net_tx_mbps,
                "error_rate": obs.error_rate,
                "log_count": obs.log_count,
                "exception_count": obs.exception_count,
            }
            for obs in window
        ],
        "count": len(window),
        "filled": len(window) >= 20,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=SETTINGS.api_host, port=SETTINGS.api_port, reload=False)
