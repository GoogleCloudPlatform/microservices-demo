from __future__ import annotations

import time
from typing import Any, Dict, List

import requests

from anomaly_api.settings import Settings


def _safe_json(url: str, timeout: float = 3.0) -> Dict[str, Any]:
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        try:
            payload = response.json()
        except ValueError:
            payload = {"text": response.text[:500]}
        return {"ok": True, "status_code": response.status_code, "json": payload}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "json": {}}


def _service_workload(
    service: str,
    snapshot: Dict[str, Any],
    workload: Dict[str, Any],
    active_incident: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    metadata = workload.get("metadata", {})
    status = snapshot.get("status", "unknown")
    if not workload.get("exists", False) or not workload.get("running", False):
        status = "critical"
    elif not workload.get("healthy", False):
        status = "warning"
    return {
        "service": service,
        "status": status,
        "combined_score": snapshot.get("combined_score", 0.0),
        "cpu_percent": snapshot.get("cpu_mean", snapshot.get("cpu_percent", 0.0)),
        "memory_percent": snapshot.get("mem_mean", snapshot.get("mem_percent", 0.0)),
        "network_rx_mbps": snapshot.get("net_rx_mean", 0.0),
        "network_tx_mbps": snapshot.get("net_tx_mean", 0.0),
        "feature_flags": snapshot.get("feature_flags", []),
        "runtime": {
            "exists": workload.get("exists", False),
            "running": workload.get("running", False),
            "healthy": workload.get("healthy", False),
            "status": workload.get("status", "unknown"),
            "restart_count": workload.get("restart_count", 0),
            "exit_code": workload.get("exit_code"),
            "oom_killed": workload.get("oom_killed", False),
            "alternatives": workload.get("alternatives", []),
            "message": workload.get("message", ""),
            "metadata": metadata,
        },
        "active_incident": active_incident,
        "latest_incident": active_incident or snapshot.get("latest_incident"),
        "memory_matches": snapshot.get("similar_incidents", []),
    }


def build_infrastructure_payload(
    *,
    settings: Settings,
    topology: Dict[str, Any],
    history: List[Dict[str, Any]],
    remediation_engine: Any,
) -> Dict[str, Any]:
    services = topology.get("services", {})
    active_incidents = topology.get("active_incidents", [])
    recent_incidents = topology.get("recent_incidents", [])
    active_incident_by_service = {
        incident.get("root_cause_service"): incident
        for incident in active_incidents
        if incident.get("root_cause_service")
    }
    service_names = list(services.keys())

    prometheus = _safe_json(f"{settings.prometheus_url}/api/v1/targets")
    loki_ready = _safe_json(f"{settings.loki_url}/ready")
    grafana_health = _safe_json(f"{settings.grafana_url}/api/health")
    jaeger_services = _safe_json(f"{settings.jaeger_url}/api/services")
    promtail_ready = _safe_json(f"{settings.promtail_url}/ready")
    otel_metrics = (
        _safe_json(f"{settings.otel_collector_url}/metrics")
        if settings.infrastructure_collectors_enabled and settings.otel_collector_url
        else {"ok": False, "error": None, "json": {}, "configured": False}
    )

    workloads = []
    cluster_summary: Dict[str, Any] = {
        "available": False,
        "platform": remediation_engine.orchestrator.platform if remediation_engine else "unknown",
        "status": "unavailable",
        "summary": "Cluster telemetry unavailable in current runtime",
    }
    if remediation_engine is not None:
        for service in service_names:
            inspected = remediation_engine.orchestrator.inspect_service(service).to_dict()
            workloads.append(
                _service_workload(
                    service,
                    services.get(service, {}),
                    inspected,
                    active_incident=active_incident_by_service.get(service),
                )
            )
        cluster_summary = remediation_engine.orchestrator.cluster_overview()

    memory_recent = remediation_engine.memory_store.list_recent(limit=10) if remediation_engine else []

    healthy = sum(1 for item in workloads if item.get("status") == "normal")
    warning = sum(1 for item in workloads if item.get("status") == "warning")
    critical = sum(1 for item in workloads if item.get("status") == "critical")
    isolated = sum(
        1
        for item in workloads
        if (item.get("active_incident") or {}).get("containment", {}).get("containment_mode") == "isolate"
    )
    manual_required = sum(
        1
        for item in workloads
        if (item.get("active_incident") or {}).get("containment", {}).get("manual_required")
    )

    targets = prometheus.get("json", {}).get("data", {}).get("activeTargets", [])
    active_targets = len(targets)
    healthy_targets = sum(1 for target in targets if target.get("health") == "up")

    return {
        "timestamp": topology.get("timestamp"),
        "environment": {
            "mode": settings.runtime_mode,
            "environment": settings.environment_name,
            "cluster_name": settings.cluster_name,
            "namespace": settings.k8s_namespace,
            "orchestrator": remediation_engine.orchestrator.platform if remediation_engine else "unknown",
            "collector_ready": settings.infrastructure_collectors_enabled,
            "history_points": len(history),
        },
        "fleet_summary": {
            "services_tracked": len(service_names),
            "healthy": healthy,
            "warning": warning,
            "critical": critical,
            "isolated": isolated,
            "manual_required": manual_required,
            "active_incidents": len(active_incidents),
        },
        "workloads": workloads,
        "observability": {
            "prometheus": {
                "available": prometheus["ok"],
                "healthy_targets": healthy_targets,
                "active_targets": active_targets,
                "error": prometheus.get("error"),
            },
            "loki": {
                "available": loki_ready["ok"],
                "error": loki_ready.get("error"),
            },
            "promtail": {
                "available": promtail_ready["ok"],
                "configured": True,
                "error": promtail_ready.get("error"),
            },
            "grafana": {
                "available": grafana_health["ok"],
                "details": grafana_health.get("json", {}),
                "error": grafana_health.get("error"),
            },
            "jaeger": {
                "available": jaeger_services["ok"],
                "service_count": len(jaeger_services.get("json", {}).get("data", []) or []),
                "error": jaeger_services.get("error"),
            },
            "otel_collector": {
                "available": otel_metrics["ok"],
                "configured": settings.infrastructure_collectors_enabled and bool(settings.otel_collector_url),
                "error": otel_metrics.get("error"),
            },
        },
        "cluster": cluster_summary,
        "remediation": {
            "active_incidents": active_incidents,
            "recent_incidents": recent_incidents,
            "predictive_alerts": topology.get("predictive_alerts", []),
            "timeline": topology.get("timeline", []),
            "cooldowns": remediation_engine.cooldown_snapshot() if remediation_engine else {},
            "leases": remediation_engine.lease_snapshot() if remediation_engine else {},
            "target_seconds": remediation_engine.target_seconds if remediation_engine else None,
        },
        "memory": {
            "recent": memory_recent,
            "count": len(memory_recent),
        },
        "system": {
            "summary": topology.get("system_summary", {}),
        },
    }
