"""
DockerActions: Wraps Docker SDK to restart/scale services.
"""

import time
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Common prefixes used by docker-compose projects
COMPOSE_PREFIXES = [
    "microservices-demo_",
    "microservices_demo_",
    "microservicesdemo_",
    "demo_",
    "",  # bare name last
]


class DockerActions:
    def __init__(self):
        self._client = None
        self._available = False
        self._init_client()

    def _init_client(self):
        try:
            import docker
            self._client = docker.from_env()
            self._client.ping()
            self._available = True
            logger.info("Docker client connected")
        except Exception as e:
            logger.warning(f"Docker not available: {e}")
            self._available = False

    def _find_container(self, service_name: str):
        """Find container by service name, trying several naming conventions."""
        if not self._available or self._client is None:
            return None

        try:
            containers = self._client.containers.list(all=False)
        except Exception as e:
            logger.error(f"Failed to list containers: {e}")
            return None

        # Build candidate names
        candidates = []
        for prefix in COMPOSE_PREFIXES:
            candidates.append(f"{prefix}{service_name}")
            candidates.append(f"{prefix}{service_name}_1")
            candidates.append(f"{prefix}{service_name}-1")

        for container in containers:
            name = container.name
            for candidate in candidates:
                if name == candidate or name.startswith(candidate):
                    return container
            # Also check labels
            labels = container.labels
            if labels.get("com.docker.compose.service") == service_name:
                return container

        return None

    def restart_service(self, service_name: str) -> bool:
        """
        Restart a service container.
        Returns True if found and restarted, False otherwise.
        """
        if not self._available:
            logger.warning(f"Docker not available, cannot restart {service_name}")
            return False

        container = self._find_container(service_name)
        if container is None:
            logger.warning(f"Container for service '{service_name}' not found")
            return False

        try:
            logger.info(f"Restarting container: {container.name}")
            container.restart(timeout=30)
            logger.info(f"Container {container.name} restarted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to restart {container.name}: {e}")
            return False

    def scale_service(self, service_name: str, replicas: int) -> bool:
        """
        Scale a service. For demo purposes, restarts if replicas > 1.
        Returns True if action was taken.
        """
        if not self._available:
            logger.warning(f"Docker not available, cannot scale {service_name}")
            return False

        if replicas <= 1:
            return self.restart_service(service_name)

        # With standalone Docker (not Swarm), we just restart
        logger.info(f"Scaling {service_name} to {replicas} (demo: restart)")
        return self.restart_service(service_name)

    def get_container_stats(self, service_name: str) -> Dict:
        """
        Returns {cpu_percent, mem_percent, status} for a service container.
        """
        if not self._available:
            return {"cpu_percent": 0.0, "mem_percent": 0.0, "status": "unknown"}

        container = self._find_container(service_name)
        if container is None:
            return {"cpu_percent": 0.0, "mem_percent": 0.0, "status": "not_found"}

        try:
            stats = container.stats(stream=False)

            # CPU
            cpu_delta = (
                stats["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            system_delta = (
                stats["cpu_stats"].get("system_cpu_usage", 0)
                - stats["precpu_stats"].get("system_cpu_usage", 0)
            )
            num_cpus = len(stats["cpu_stats"]["cpu_usage"].get("percpu_usage", [1]))
            cpu_pct = 0.0
            if system_delta > 0:
                cpu_pct = (cpu_delta / system_delta) * num_cpus * 100.0

            # Memory
            mem_usage = stats["memory_stats"].get("usage", 0)
            mem_limit = stats["memory_stats"].get("limit", 1)
            mem_pct = (mem_usage / mem_limit) * 100.0 if mem_limit > 0 else 0.0

            return {
                "cpu_percent": round(cpu_pct, 2),
                "mem_percent": round(mem_pct, 2),
                "status": container.status,
            }

        except Exception as e:
            logger.error(f"Failed to get stats for {service_name}: {e}")
            return {
                "cpu_percent": 0.0,
                "mem_percent": 0.0,
                "status": container.status if container else "error",
            }

    @property
    def available(self) -> bool:
        return self._available


if __name__ == "__main__":
    actions = DockerActions()
    print(f"Docker available: {actions.available}")
    if actions.available:
        stats = actions.get_container_stats("frontend")
        print(f"Frontend stats: {stats}")
