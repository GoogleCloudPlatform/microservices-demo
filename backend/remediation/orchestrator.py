from __future__ import annotations

import logging
from datetime import datetime, timezone
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

    def cluster_overview(self) -> Dict:
        return {
            "available": False,
            "platform": self.platform,
            "status": "unavailable",
            "summary": "Cluster overview is not available for this orchestrator",
        }


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

    def cluster_overview(self) -> Dict:
        if not self._available or self._client is None:
            return {
                "available": False,
                "platform": self.platform,
                "status": "unavailable",
                "summary": "Docker is not available",
            }
        try:
            containers = list(self._client.containers.list(all=True))
            running = sum(1 for container in containers if container.status == "running")
            unhealthy = 0
            for container in containers:
                health = ((container.attrs or {}).get("State", {}).get("Health") or {}).get("Status")
                if health and health != "healthy":
                    unhealthy += 1
            status = "healthy" if unhealthy == 0 else "degraded"
            return {
                "available": True,
                "platform": self.platform,
                "status": status,
                "summary": f"{running}/{len(containers)} containers running, {unhealthy} unhealthy",
                "containers": {
                    "total": len(containers),
                    "running": running,
                    "unhealthy": unhealthy,
                },
            }
        except Exception as exc:
            return {
                "available": False,
                "platform": self.platform,
                "status": "error",
                "summary": str(exc),
            }

    @property
    def available(self) -> bool:
        return self._available

    @property
    def platform(self) -> str:
        return "docker"


class KubernetesOrchestratorAdapter(OrchestratorAdapter):
    def __init__(self, namespace: str = "default") -> None:
        self.namespace = namespace
        self._available = False
        self._apps = None
        self._core = None
        self._policy = None
        self._init_client()

    def _init_client(self) -> None:
        try:
            from kubernetes import client, config

            try:
                config.load_incluster_config()
            except Exception:
                config.load_kube_config()

            self._apps = client.AppsV1Api()
            self._core = client.CoreV1Api()
            self._policy = client.PolicyV1Api()
            self._available = True
        except Exception as exc:
            logger.warning("Kubernetes orchestrator unavailable: %s", exc)
            self._available = False

    def _read_deployment(self, service_name: str):
        if not self._available or self._apps is None:
            return None
        try:
            return self._apps.read_namespaced_deployment(service_name, self.namespace)
        except Exception:
            return None

    def _list_pods(self, service_name: str):
        if not self._available or self._core is None:
            return []
        try:
            pods = self._core.list_namespaced_pod(
                self.namespace,
                label_selector=f"app={service_name}",
            )
            return list(pods.items or [])
        except Exception:
            return []

    def _collect_pod_runtime(self, pods: List) -> Dict:
        ready = 0
        running = 0
        restart_count = 0
        oom_killed = False
        pod_names = []
        statuses = []

        for pod in pods:
            pod_names.append(pod.metadata.name)
            phase = (pod.status.phase or "").lower()
            statuses.append(phase)
            if phase == "running":
                running += 1
            container_statuses = list(pod.status.container_statuses or [])
            for container_status in container_statuses:
                restart_count += int(container_status.restart_count or 0)
                if container_status.ready:
                    ready += 1
                last_state = getattr(container_status, "last_state", None)
                terminated = getattr(last_state, "terminated", None) if last_state else None
                current_state = getattr(container_status, "state", None)
                current_terminated = getattr(current_state, "terminated", None) if current_state else None
                for term in [terminated, current_terminated]:
                    if term and getattr(term, "reason", "") == "OOMKilled":
                        oom_killed = True

        return {
            "ready_containers": ready,
            "running_pods": running,
            "restart_count": restart_count,
            "oom_killed": oom_killed,
            "pod_names": pod_names,
            "pod_statuses": statuses,
        }

    def inspect_service(self, service_name: str) -> WorkloadState:
        if not self._available:
            return WorkloadState(
                service=service_name,
                exists=False,
                running=False,
                healthy=False,
                status="unsupported",
                message="Kubernetes executor scaffold is not configured in this environment",
            )

        deployment = self._read_deployment(service_name)
        pods = self._list_pods(service_name)
        if deployment is None:
            return WorkloadState(
                service=service_name,
                exists=False,
                running=False,
                healthy=False,
                status="not_found",
                message=f"Deployment {service_name} not found in namespace {self.namespace}",
            )

        desired = int(deployment.spec.replicas or 0)
        status = deployment.status
        ready_replicas = int(status.ready_replicas or 0)
        available_replicas = int(status.available_replicas or 0)
        unavailable_replicas = int(status.unavailable_replicas or 0)
        pod_runtime = self._collect_pod_runtime(pods)
        isolated = desired == 0
        healthy = (ready_replicas >= desired and available_replicas >= desired and unavailable_replicas == 0) if not isolated else False
        running = pod_runtime["running_pods"] >= max(desired, 1) if not isolated else False
        rollout_status = "isolated" if isolated else ("healthy" if healthy else "degraded")

        return WorkloadState(
            service=service_name,
            exists=True,
            running=running,
            healthy=healthy,
            status=rollout_status,
            restart_count=pod_runtime["restart_count"],
            oom_killed=pod_runtime["oom_killed"],
            message=f"kubernetes:{service_name}",
            metadata={
                "namespace": self.namespace,
                "desired_replicas": desired,
                "ready_replicas": ready_replicas,
                "available_replicas": available_replicas,
                "unavailable_replicas": unavailable_replicas,
                "observed_generation": status.observed_generation,
                "pod_names": pod_runtime["pod_names"],
                "pod_statuses": pod_runtime["pod_statuses"],
            },
        )

    def restart_service(self, service_name: str) -> Tuple[bool, str, Dict]:
        if not self._available or self._apps is None:
            return False, "Kubernetes executor is not configured", {}
        deployment = self._read_deployment(service_name)
        if deployment is None:
            return False, f"Deployment {service_name} not found", {}
        try:
            annotations = dict((deployment.spec.template.metadata.annotations or {}))
            annotations["kubectl.kubernetes.io/restartedAt"] = datetime.now(timezone.utc).isoformat()
            body = {"spec": {"template": {"metadata": {"annotations": annotations}}}}
            self._apps.patch_namespaced_deployment(service_name, self.namespace, body)
            state = self.inspect_service(service_name)
            return True, f"Rollout restart triggered for {service_name}", state.to_dict()
        except Exception as exc:
            return False, str(exc), {}

    def stop_service(self, service_name: str) -> Tuple[bool, str, Dict]:
        return self._scale_service(service_name, 0, reason="stopped_by_aegis")

    def start_service(self, service_name: str) -> Tuple[bool, str, Dict]:
        deployment = self._read_deployment(service_name)
        if deployment is None:
            return False, f"Deployment {service_name} not found", {}
        annotations = deployment.metadata.annotations or {}
        replicas = int(annotations.get("aegis.dev/previous-replicas", "1"))
        return self._scale_service(service_name, max(replicas, 1), reason="restarted_by_aegis")

    def isolate_service(self, service_name: str) -> Tuple[bool, str, Dict]:
        return self._scale_service(service_name, 0, reason="isolated_by_aegis")

    def discover_healthy_alternatives(self, service_name: str) -> List[str]:
        return []

    def _scale_service(self, service_name: str, replicas: int, reason: str) -> Tuple[bool, str, Dict]:
        if not self._available or self._apps is None:
            return False, "Kubernetes executor is not configured", {}
        deployment = self._read_deployment(service_name)
        if deployment is None:
            return False, f"Deployment {service_name} not found", {}
        current_replicas = int(deployment.spec.replicas or 0)
        try:
            metadata_annotations = dict(deployment.metadata.annotations or {})
            if current_replicas > 0:
                metadata_annotations["aegis.dev/previous-replicas"] = str(current_replicas)
            metadata_annotations["aegis.dev/last-scale-reason"] = reason
            body = {
                "metadata": {"annotations": metadata_annotations},
                "spec": {"replicas": replicas},
            }
            self._apps.patch_namespaced_deployment(service_name, self.namespace, body)
            state = self.inspect_service(service_name)
            return True, f"Scaled {service_name} to {replicas}", state.to_dict()
        except Exception as exc:
            return False, str(exc), {}

    def cluster_overview(self) -> Dict:
        if not self._available or self._apps is None or self._core is None:
            return {
                "available": False,
                "platform": self.platform,
                "status": "unavailable",
                "summary": "Kubernetes client is not configured",
            }
        try:
            nodes = list(self._core.list_node().items or [])
            pods = list(self._core.list_namespaced_pod(self.namespace).items or [])
            deployments = list(self._apps.list_namespaced_deployment(self.namespace).items or [])
            ready_nodes = 0
            for node in nodes:
                for condition in node.status.conditions or []:
                    if condition.type == "Ready" and condition.status == "True":
                        ready_nodes += 1
                        break
            unavailable = sum(1 for dep in deployments if int(dep.status.unavailable_replicas or 0) > 0)
            return {
                "available": True,
                "platform": self.platform,
                "status": "healthy" if unavailable == 0 else "degraded",
                "namespace": self.namespace,
                "nodes": {
                    "total": len(nodes),
                    "ready": ready_nodes,
                },
                "pods": {
                    "total": len(pods),
                    "running": sum(1 for pod in pods if (pod.status.phase or "").lower() == "running"),
                    "pending": sum(1 for pod in pods if (pod.status.phase or "").lower() == "pending"),
                    "failed": sum(1 for pod in pods if (pod.status.phase or "").lower() == "failed"),
                },
                "deployments": {
                    "total": len(deployments),
                    "unavailable": unavailable,
                },
                "summary": f"{ready_nodes}/{len(nodes)} nodes ready, {unavailable} deployments unavailable",
            }
        except Exception as exc:
            return {
                "available": False,
                "platform": self.platform,
                "status": "error",
                "summary": str(exc),
            }

    @property
    def available(self) -> bool:
        return self._available

    @property
    def platform(self) -> str:
        return "kubernetes"
