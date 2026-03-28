from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_csv(name: str, default: str) -> List[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    runtime_mode: str
    environment_name: str
    cluster_name: str
    api_host: str
    api_port: int
    cors_origins: List[str]
    auth_enabled: bool
    api_token: str
    orchestrator_target: str
    prometheus_url: str
    loki_url: str
    promtail_url: str
    jaeger_url: str
    grafana_url: str
    otel_collector_url: str
    k8s_namespace: str
    incident_memory_db: str
    incident_memory_limit: int
    incident_memory_retention_days: int
    remediation_cooldown_s: float
    remediation_lock_timeout_s: float
    infrastructure_collectors_enabled: bool
    model_dir: str
    system_db_path: str
    predictive_alert_threshold: float
    predictive_auto_action_threshold: float
    predictive_action_cooldown_s: float

    @property
    def is_production(self) -> bool:
        return self.runtime_mode == "production"


def load_settings() -> Settings:
    runtime_mode = os.getenv("AEGIS_RUNTIME_MODE", "dev").strip().lower()
    if runtime_mode not in {"dev", "production"}:
        runtime_mode = "dev"

    default_origins = "http://localhost:5173,http://127.0.0.1:5173"
    auth_default = runtime_mode == "production"

    return Settings(
        runtime_mode=runtime_mode,
        environment_name=os.getenv("AEGIS_ENVIRONMENT", "local"),
        cluster_name=os.getenv("AEGIS_CLUSTER_NAME", "online-boutique"),
        api_host=os.getenv("AEGIS_API_HOST", "0.0.0.0"),
        api_port=_env_int("AEGIS_API_PORT", 8001),
        cors_origins=_env_csv("AEGIS_ALLOWED_ORIGINS", default_origins),
        auth_enabled=_env_bool("AEGIS_AUTH_ENABLED", auth_default),
        api_token=os.getenv("AEGIS_API_TOKEN", ""),
        orchestrator_target=os.getenv("AEGIS_ORCHESTRATOR", "auto").strip().lower(),
        prometheus_url=os.getenv("AEGIS_PROMETHEUS_URL", "http://localhost:9090"),
        loki_url=os.getenv("AEGIS_LOKI_URL", "http://localhost:3100"),
        promtail_url=os.getenv("AEGIS_PROMTAIL_URL", "http://localhost:9080"),
        jaeger_url=os.getenv("AEGIS_JAEGER_URL", "http://localhost:16686"),
        grafana_url=os.getenv("AEGIS_GRAFANA_URL", "http://localhost:3000"),
        otel_collector_url=os.getenv("AEGIS_OTEL_COLLECTOR_URL", "http://localhost:8889"),
        k8s_namespace=os.getenv("AEGIS_K8S_NAMESPACE", "default"),
        incident_memory_db=os.getenv("INCIDENT_MEMORY_DB", "backend/.runtime/incident_memory.db"),
        incident_memory_limit=_env_int("AEGIS_INCIDENT_MEMORY_LIMIT", 5000),
        incident_memory_retention_days=_env_int("AEGIS_INCIDENT_MEMORY_RETENTION_DAYS", 30),
        remediation_cooldown_s=_env_float("AEGIS_REMEDIATION_COOLDOWN_S", 30.0),
        remediation_lock_timeout_s=_env_float("AEGIS_REMEDIATION_LOCK_TIMEOUT_S", 300.0),
        infrastructure_collectors_enabled=_env_bool("AEGIS_INFRA_COLLECTORS_ENABLED", True),
        model_dir=os.getenv("AEGIS_MODEL_DIR", "models/aegis_models"),
        system_db_path=os.getenv("AEGIS_SYSTEM_DB", "backend/.runtime/aegis_system.db"),
        predictive_alert_threshold=_env_float("AEGIS_PREDICTIVE_ALERT_THRESHOLD", 0.68),
        predictive_auto_action_threshold=_env_float("AEGIS_PREDICTIVE_AUTO_ACTION_THRESHOLD", 0.88),
        predictive_action_cooldown_s=_env_float("AEGIS_PREDICTIVE_ACTION_COOLDOWN_S", 300.0),
    )
