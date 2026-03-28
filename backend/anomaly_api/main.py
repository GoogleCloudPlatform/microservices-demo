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
from remediation.engine import RemediationEngine
from remediation.models import ActionProposal
from remediation.policy import DEPENDENCY_GRAPH

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


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AppState:
    def __init__(self):
        self.models_loaded = False
        self.if_inference = None
        self.lstm_inference = None
        self.correlation_engine = None
        self.remediation_engine: Optional[RemediationEngine] = None

        self.current_scores: Dict[str, Dict] = {}
        self.current_model_insights: Dict[str, Dict] = {}
        self.history: deque = deque(maxlen=100)
        self.last_update: float = 0.0

        self.window_state = None
        self.ingestion_pipeline = None


state = AppState()


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


async def update_scores_loop():
    while True:
        try:
            scores = compute_all_scores()
            state.current_scores = scores
            state.last_update = time.time()

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
    if SETTINGS.auth_enabled and not SETTINGS.api_token:
        raise RuntimeError("AEGIS auth is enabled but AEGIS_API_TOKEN is not configured")
    load_models()

    from anomaly_api.ingestion import SlidingWindowState, IngestionPipeline

    state.window_state = SlidingWindowState()
    state.ingestion_pipeline = IngestionPipeline(state.window_state)
    state.ingestion_pipeline.start()

    asyncio.create_task(update_scores_loop())
    logger.info("Platform started. models_loaded=%s", state.models_loaded)


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


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "runtime_mode": SETTINGS.runtime_mode,
        "environment": SETTINGS.environment_name,
        "orchestrator": state.remediation_engine.orchestrator.platform if state.remediation_engine else None,
        "models_loaded": state.models_loaded,
        "model_dir": SETTINGS.model_dir,
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

    return {
        "service": payload.service,
        "failure_type": payload.failure_type,
        "severity": payload.severity,
        "result": result,
        "timestamp": utc_now_iso(),
    }


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


@app.get("/ml/insights")
async def ml_insights():
    scores = state.current_scores or compute_all_scores()
    services = []
    for svc in ALL_SERVICES:
        snapshot = scores.get(svc, {})
        insight = state.current_model_insights.get(svc, {})
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
            }
        )
    services.sort(key=lambda item: item.get("combined_score", 0) or 0, reverse=True)
    return {
        "timestamp": utc_now_iso(),
        "models": {
            "isolation_forest": state.if_inference.metadata() if state.if_inference else {"loaded": False},
            "lstm": state.lstm_inference.metadata() if state.lstm_inference else {"loaded": False},
        },
        "required_sequence_length": LSTM_SEQUENCE_WINDOW,
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
