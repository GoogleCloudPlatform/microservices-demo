from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from remediation.models import WorkloadState

logger = logging.getLogger(__name__)


class OrchestratorAdapter(ABC):
    @abstractmethod
    def inspect_service(self, service_name: str) -> WorkloadState:
        raise NotImplementedError

    @abstractmethod
    def restart_service(self, service_name: str) -> Tuple[bool, str, Dict]:
        raise NotImplementedError

    @abstractmethod
    def stop_service(self, service_name: str) -> Tuple[bool, str, Dict]:
        raise NotImplementedError

    @abstractmethod
    def start_service(self, service_name: str) -> Tuple[bool, str, Dict]:
        raise NotImplementedError

    @abstractmethod
    def isolate_service(self, service_name: str) -> Tuple[bool, str, Dict]:
        raise NotImplementedError

    @abstractmethod
    def discover_healthy_alternatives(self, service_name: str) -> List[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def available(self) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def platform(self) -> str:
        raise NotImplementedError


class DockerOrchestratorAdapter(OrchestratorAdapter):
    COMPOSE_PREFIXES = [
        "microservices-demo_",
        "microservices_demo_",
        "microservicesdemo_",
        "demo_",
        "",
    ]

    def __init__(self) -> None:
        self._client = None
        self._available = False
        self._init_client()

    def _init_client(self) -> None:
        try:
            import docker

            self._client = docker.from_env()
            self._client.ping()
            self._available = True
        except Exception as exc:
            logger.warning("Docker orchestrator unavailable: %s", exc)
            self._available = False

    def _find_container(self, service_name: str, all_containers: bool = True):
        if not self._available or self._client is None:
            return None

        try:
            containers = self._client.containers.list(all=all_containers)
        except Exception as exc:
            logger.error("Failed to list containers: %s", exc)
            return None

        candidates = []
        for prefix in self.COMPOSE_PREFIXES:
            candidates.extend(
                [
                    f"{prefix}{service_name}",
                    f"{prefix}{service_name}_1",
                    f"{prefix}{service_name}-1",
                ]
            )

        for container in containers:
            name = container.name
            if name in candidates or any(name.startswith(candidate) for candidate in candidates):
                return container
            labels = container.labels or {}
            if labels.get("com.docker.compose.service") == service_name:
                return container
        return None

    def _inspect_container(self, service_name: str) -> WorkloadState:
        container = self._find_container(service_name, all_containers=True)
        if container is None:
            return WorkloadState(
                service=service_name,
                exists=False,
                running=False,
                healthy=False,
                status="not_found",
                message="Container not found",
            )

        try:
            container.reload()
            attrs = container.attrs or {}
            state = attrs.get("State", {})
            health = (state.get("Health") or {}).get("Status")
            running = bool(state.get("Running", False))
            status = state.get("Status", container.status or "unknown")
            restart_count = int(attrs.get("RestartCount", 0))
            oom_killed = bool(state.get("OOMKilled", False))
            exit_code = state.get("ExitCode")
            healthy = running and health in (None, "", "healthy")

            return WorkloadState(
                service=service_name,
                exists=True,
                running=running,
                healthy=healthy,
                status=status,
                restart_count=restart_count,
                exit_code=exit_code,
                oom_killed=oom_killed,
                message=f"docker:{container.name}",
                alternatives=self.discover_healthy_alternatives(service_name),
                metadata={
                    "health_status": health,
                    "container_name": container.name,
                    "image": attrs.get("Config", {}).get("Image"),
                    "started_at": state.get("StartedAt"),
                    "finished_at": state.get("FinishedAt"),
                },
            )
        except Exception as exc:
            return WorkloadState(
                service=service_name,
                exists=True,
                running=False,
                healthy=False,
                status="inspect_error",
                message=str(exc),
            )

    def inspect_service(self, service_name: str) -> WorkloadState:
        return self._inspect_container(service_name)

    def _run_action(self, service_name: str, action: str) -> Tuple[bool, str, Dict]:
        container = self._find_container(service_name, all_containers=True)
        if container is None:
            return False, "Container not found", {}

        try:
            if action == "restart":
                container.restart(timeout=30)
            elif action == "stop":
                container.stop(timeout=20)
            elif action == "start":
                container.start()
            else:
                return False, f"Unsupported docker action: {action}", {}

            state = self._inspect_container(service_name)
            return True, f"{action} completed", state.to_dict()
        except Exception as exc:
            return False, str(exc), {}

    def restart_service(self, service_name: str) -> Tuple[bool, str, Dict]:
        return self._run_action(service_name, "restart")

    def stop_service(self, service_name: str) -> Tuple[bool, str, Dict]:
        return self._run_action(service_name, "stop")

    def start_service(self, service_name: str) -> Tuple[bool, str, Dict]:
        return self._run_action(service_name, "start")

    def isolate_service(self, service_name: str) -> Tuple[bool, str, Dict]:
        ok, message, details = self.stop_service(service_name)
        if ok:
            message = f"Service isolated by stopping workload: {service_name}"
        return ok, message, details

    def discover_healthy_alternatives(self, service_name: str) -> List[str]:
        # Docker Compose stack runs single-instance workloads, so reroute is best-effort only.
        return []

    @property
    def available(self) -> bool:
        return self._available

    @property
    def platform(self) -> str:
        return "docker"


class KubernetesOrchestratorAdapter(OrchestratorAdapter):
    def __init__(self) -> None:
        self._available = False

    def inspect_service(self, service_name: str) -> WorkloadState:
        return WorkloadState(
            service=service_name,
            exists=False,
            running=False,
            healthy=False,
            status="unsupported",
            message="Kubernetes executor scaffold is not configured in this environment",
        )

    def restart_service(self, service_name: str) -> Tuple[bool, str, Dict]:
        return False, "Kubernetes executor is not configured", {}

    def stop_service(self, service_name: str) -> Tuple[bool, str, Dict]:
        return False, "Kubernetes executor is not configured", {}

    def start_service(self, service_name: str) -> Tuple[bool, str, Dict]:
        return False, "Kubernetes executor is not configured", {}

    def isolate_service(self, service_name: str) -> Tuple[bool, str, Dict]:
        return False, "Kubernetes executor is not configured", {}

    def discover_healthy_alternatives(self, service_name: str) -> List[str]:
        return []

    @property
    def available(self) -> bool:
        return self._available

    @property
    def platform(self) -> str:
        return "kubernetes"
