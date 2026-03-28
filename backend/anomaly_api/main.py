"""
AI Observability Platform - FastAPI Backend

Port: 8001
- /health       GET  System health check
- /status       GET  Full system status with anomaly scores
- /ingest       POST Accept live metrics/logs, update scores
- /remediate    POST Trigger remediation for a service
- /history      GET  Last 100 score snapshots
- /alerts       GET  Active alerts (score > 0.7)
"""

import asyncio
import json
import math
import sys
import os
import time
import logging
from datetime import datetime, timezone
from collections import deque
from typing import Any, Dict, List, Optional

# Add repo root and backend to sys.path for imports
_file = os.path.abspath(__file__)
_backend = os.path.dirname(os.path.dirname(_file))
_repo_root = os.path.dirname(_backend)
for _p in [_backend, _repo_root]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================
# Service list (Online Boutique)
# =============================================
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

# Demo mode phase offsets for sinusoidal scores
DEMO_PHASES = {svc: i * 0.6 for i, svc in enumerate(ALL_SERVICES)}

# =============================================
# App state
# =============================================

class AppState:
    def __init__(self):
        self.demo_mode = True
        self.models_loaded = False
        self.if_inference = None
        self.lstm_inference = None
        self.correlation_engine = None
        self.remediation_engine = None

        # Live score store: service -> {if_score, lstm_score, combined_score}
        self.current_scores: Dict[str, Dict] = {}

        # History: deque of score snapshots
        self.history: deque = deque(maxlen=100)

        # Last update time
        self.last_update: float = 0.0

        # Demo tick counter
        self._demo_tick: float = 0.0


state = AppState()

# =============================================
# Model loading
# =============================================

def load_models():
    """Try to load IF and LSTM models. Sets demo_mode if either fails."""
    loaded_if = False
    loaded_lstm = False

    try:
        from ml.isolation_forest.inference import IFInference
        inf = IFInference()
        if inf.load():
            state.if_inference = inf
            loaded_if = True
            logger.info("IF model loaded")
    except Exception as e:
        logger.warning(f"IF model load failed: {e}")

    try:
        from ml.lstm.inference import LSTMInference
        lstm = LSTMInference()
        if lstm.load():
            state.lstm_inference = lstm
            loaded_lstm = True
            logger.info("LSTM model loaded")
    except Exception as e:
        logger.warning(f"LSTM model load failed: {e}")

    state.models_loaded = loaded_if and loaded_lstm
    state.demo_mode = not state.models_loaded

    if state.demo_mode:
        logger.info("Running in DEMO MODE (sinusoidal scores)")

    # Load correlation engine (always available)
    try:
        from anomaly_api.correlation import CorrelationEngine
        state.correlation_engine = CorrelationEngine()
        logger.info("Correlation engine loaded")
    except Exception as e:
        logger.warning(f"Correlation engine load failed: {e}")

    # Load remediation engine
    try:
        from remediation.engine import RemediationEngine
        state.remediation_engine = RemediationEngine(
            target_seconds=15,
            demo_mode=state.demo_mode
        )
        logger.info("Remediation engine loaded")
    except Exception as e:
        logger.warning(f"Remediation engine load failed: {e}")


# =============================================
# Score computation
# =============================================

def _demo_score(service: str, t: float = None) -> Dict:
    """Generate sinusoidal demo scores for a service."""
    if t is None:
        t = time.time()
    phase_offset = DEMO_PHASES.get(service, 0.0)

    # Different frequencies for IF and LSTM to make it interesting
    if_phase = (t / 30.0 + phase_offset) * 2 * math.pi
    lstm_phase = (t / 45.0 + phase_offset + 0.5) * 2 * math.pi

    # Add a slow "incident" wave every 3 minutes
    incident_phase = (t / 180.0 + phase_offset * 0.3) * 2 * math.pi
    incident_boost = max(0, math.sin(incident_phase)) * 0.3

    if_score = float(max(0, min(1, 0.2 + 0.15 * math.sin(if_phase) + incident_boost)))
    lstm_score = float(max(0, min(1, 0.2 + 0.15 * math.sin(lstm_phase) + incident_boost)))
    combined = 0.6 * lstm_score + 0.4 * if_score

    return {
        "if_score": round(if_score, 3),
        "lstm_score": round(lstm_score, 3),
        "combined_score": round(combined, 3),
    }


def _score_status(combined: float) -> str:
    if combined < 0.4:
        return "normal"
    elif combined < 0.7:
        return "warning"
    else:
        return "critical"


def compute_all_scores() -> Dict[str, Dict]:
    """Compute scores for all services."""
    t = time.time()
    scores = {}

    for svc in ALL_SERVICES:
        if state.demo_mode:
            s = _demo_score(svc, t)
        else:
            # Use loaded models
            dummy_features = {
                "cpu_percent": 0.5,
                "mem_percent": 0.5,
                "net_rx_mb": 0.1,
                "net_tx_mb": 0.1,
                "block_read_mb": 0.01,
                "block_write_mb": 0.01,
                "log_count": 10.0,
                "error_rate": 0.01,
                "warn_rate": 0.02,
                "template_entropy": 1.5,
            }
            if_score = state.if_inference.score(dummy_features) if state.if_inference else _demo_score(svc, t)["if_score"]
            lstm_score = state.lstm_inference._demo_score() if state.lstm_inference else _demo_score(svc, t)["lstm_score"]
            combined = 0.6 * lstm_score + 0.4 * if_score
            s = {
                "if_score": round(if_score, 3),
                "lstm_score": round(lstm_score, 3),
                "combined_score": round(combined, 3),
            }

        s["status"] = _score_status(s["combined_score"])
        scores[svc] = s

    return scores


def get_root_cause_analysis(scores: Dict[str, Dict]) -> Dict:
    """Run correlation engine on current scores."""
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
    except Exception as e:
        logger.error(f"Correlation engine error: {e}")
        return {"root_cause": None, "confidence": 0.0, "failure_type": "none"}


def get_recommendation(root_cause: Dict, scores: Dict) -> str:
    """Generate human-readable recommendation."""
    service = root_cause.get("service") or root_cause.get("root_cause")
    if not service:
        return "No anomalies detected. System operating normally."

    failure_type = root_cause.get("failure_type", "generic_anomaly")
    confidence = root_cause.get("confidence", 0.0)
    affected = root_cause.get("affected_services", [])

    recs = {
        "memory_leak": f"Memory leak detected in {service}. Recommend restart to reclaim memory.",
        "cpu_starvation": f"CPU starvation in {service}. Consider scaling up or restarting.",
        "network_latency": f"Network latency in {service}. Check upstream dependencies and restart if needed.",
        "generic_anomaly": f"Anomaly detected in {service}. Recommend investigating logs and restarting.",
        "none": "System operating normally.",
    }

    rec = recs.get(failure_type, recs["generic_anomaly"])
    if len(affected) > 1:
        rec += f" Affected services: {', '.join(affected[:3])}{'...' if len(affected) > 3 else ''}."
    rec += f" Confidence: {confidence:.0%}."
    return rec


# =============================================
# Background task
# =============================================

async def update_scores_loop():
    """Background task that updates demo scores every 2 seconds."""
    while True:
        try:
            scores = compute_all_scores()
            state.current_scores = scores
            state.last_update = time.time()

            # Add to history
            snapshot = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "scores": {svc: v["combined_score"] for svc, v in scores.items()},
            }
            state.history.append(snapshot)

        except Exception as e:
            logger.error(f"Score update error: {e}")

        await asyncio.sleep(2)


# =============================================
# FastAPI App
# =============================================

app = FastAPI(
    title="AI Observability Platform",
    description="Anomaly detection and self-healing for microservices",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Observability Platform...")
    load_models()
    # Start background score update loop
    asyncio.create_task(update_scores_loop())
    logger.info(f"Platform started. demo_mode={state.demo_mode}")


# =============================================
# Pydantic models
# =============================================

class IngestPayload(BaseModel):
    metrics: List[Dict[str, Any]] = []
    logs: List[Dict[str, Any]] = []


class RemediatePayload(BaseModel):
    service: str
    failure_type: str = "generic_anomaly"


# =============================================
# Endpoints
# =============================================

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "demo_mode": state.demo_mode,
        "models_loaded": state.models_loaded,
        "services_tracked": len(ALL_SERVICES),
        "last_update": datetime.fromtimestamp(state.last_update, tz=timezone.utc).isoformat() if state.last_update else None,
    }


@app.get("/status")
async def status():
    # Use cached scores or compute fresh
    if not state.current_scores:
        scores = compute_all_scores()
        state.current_scores = scores
    else:
        scores = state.current_scores

    root_cause = get_root_cause_analysis(scores)
    recommendation = get_recommendation(root_cause, scores)

    # Active alerts
    alerts = [
        {
            "service": svc,
            "score": v["combined_score"],
            "status": v["status"],
            "if_score": v["if_score"],
            "lstm_score": v["lstm_score"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        for svc, v in scores.items()
        if v["combined_score"] > 0.7
    ]

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "demo_mode": state.demo_mode,
        "services": scores,
        "root_cause": root_cause,
        "alerts": alerts,
        "recommendation": recommendation,
    }


@app.post("/ingest")
async def ingest(payload: IngestPayload):
    """Accept live metrics/logs and update scores."""
    updated = 0

    # Process metrics
    for metric in payload.metrics:
        svc = metric.get("service_name") or metric.get("service")
        if not svc:
            continue

        if svc not in ALL_SERVICES:
            continue

        # Extract features
        features = {
            "cpu_percent": float(metric.get("cpu_percent", metric.get("cpu_usage_percent", 0))),
            "mem_percent": float(metric.get("mem_percent", metric.get("memory_usage_percent", 0))),
            "net_rx_mb": float(metric.get("net_rx_mb", 0)),
            "net_tx_mb": float(metric.get("net_tx_mb", 0)),
            "block_read_mb": float(metric.get("block_read_mb", 0)),
            "block_write_mb": float(metric.get("block_write_mb", 0)),
            "log_count": float(metric.get("log_count", 0)),
            "error_rate": float(metric.get("error_rate", 0)),
            "warn_rate": float(metric.get("warn_rate", 0)),
            "template_entropy": float(metric.get("template_entropy", 0)),
        }

        if not state.demo_mode and state.if_inference:
            if_score = state.if_inference.score(features)
            lstm_score = 0.2  # Default until buffer fills
            if state.lstm_inference:
                result = state.lstm_inference.predict_from_features(features)
                if result is not None:
                    lstm_score = result

            combined = 0.6 * lstm_score + 0.4 * if_score
            state.current_scores[svc] = {
                "if_score": round(if_score, 3),
                "lstm_score": round(lstm_score, 3),
                "combined_score": round(combined, 3),
                "status": _score_status(combined),
            }
            updated += 1

    return {
        "status": "ok",
        "updated_services": updated,
        "demo_mode": state.demo_mode,
    }


@app.post("/remediate")
async def remediate(payload: RemediatePayload):
    """Trigger remediation for a service."""
    if state.remediation_engine is None:
        # Fallback: create a demo engine
        from remediation.engine import RemediationEngine
        engine = RemediationEngine(target_seconds=15, demo_mode=True)
    else:
        engine = state.remediation_engine

    logger.info(f"Remediation requested: service={payload.service}, type={payload.failure_type}")

    result = engine.remediate(payload.service, payload.failure_type)

    return {
        "service": payload.service,
        "failure_type": payload.failure_type,
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/history")
async def history():
    """Return last 100 score snapshots."""
    return {
        "count": len(state.history),
        "snapshots": list(state.history),
    }


@app.get("/alerts")
async def alerts():
    """Return active alerts (combined_score > 0.7)."""
    if not state.current_scores:
        return {"alerts": [], "count": 0}

    active_alerts = [
        {
            "service": svc,
            "score": v["combined_score"],
            "status": v["status"],
            "if_score": v["if_score"],
            "lstm_score": v["lstm_score"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        for svc, v in state.current_scores.items()
        if v["combined_score"] > 0.7
    ]

    active_alerts.sort(key=lambda x: x["score"], reverse=True)

    return {
        "alerts": active_alerts,
        "count": len(active_alerts),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
