"""
Remediation Engine

Executes predefined playbooks to remediate service failures.
Supports demo_mode where actions are simulated.
"""

import time
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Playbooks: failure_type -> list of steps
PLAYBOOKS = {
    "memory_leak": [
        {"action": "restart_service", "target": "self", "delay_s": 0},
    ],
    "cpu_starvation": [
        {"action": "restart_service", "target": "self", "delay_s": 0},
    ],
    "network_latency": [
        {"action": "restart_service", "target": "self", "delay_s": 5},
    ],
    "generic_anomaly": [
        {"action": "restart_service", "target": "self", "delay_s": 0},
    ],
    "none": [],
}


class RemediationEngine:
    def __init__(self, target_seconds: int = 15, demo_mode: bool = False):
        """
        Args:
            target_seconds: Target remediation time in seconds
            demo_mode: If True, simulate actions without Docker
        """
        self.target_seconds = target_seconds
        self.demo_mode = demo_mode
        self._docker = None
        self._init_docker()

    def _init_docker(self):
        if self.demo_mode:
            return
        try:
            from remediation.docker_actions import DockerActions
            self._docker = DockerActions()
            if not self._docker.available:
                logger.warning("Docker not available, switching to demo_mode")
                self.demo_mode = True
        except Exception as e:
            logger.warning(f"Could not init DockerActions: {e}, using demo_mode")
            self.demo_mode = True

    def remediate(self, service: str, failure_type: str) -> Dict:
        """
        Execute remediation playbook for a service failure.

        Args:
            service: Service name to remediate
            failure_type: Type of failure (memory_leak, cpu_starvation, etc.)

        Returns:
            {
                "success": bool,
                "actions_taken": list[str],
                "elapsed_s": float,
                "demo_mode": bool,
            }
        """
        start_time = time.time()
        actions_taken = []

        playbook = PLAYBOOKS.get(failure_type, PLAYBOOKS["generic_anomaly"])

        if not playbook:
            return {
                "success": True,
                "actions_taken": ["no_action_needed"],
                "elapsed_s": 0.0,
                "demo_mode": self.demo_mode,
                "message": f"No playbook steps for failure_type={failure_type}",
            }

        logger.info(f"Starting remediation: service={service}, failure_type={failure_type}, demo_mode={self.demo_mode}")

        success = True
        for step in playbook:
            action = step["action"]
            target = step.get("target", "self")
            delay_s = step.get("delay_s", 0)

            # Resolve target
            resolved_target = service if target == "self" else target

            # Apply pre-step delay
            if delay_s > 0:
                logger.info(f"  Waiting {delay_s}s before action...")
                if not self.demo_mode:
                    time.sleep(delay_s)
                else:
                    time.sleep(min(delay_s, 0.1))  # Short sleep in demo mode

            # Execute action
            step_result = self._execute_step(action, resolved_target)
            action_str = f"{action}({resolved_target})"

            if step_result:
                actions_taken.append(f"{action_str}: OK")
                logger.info(f"  {action_str}: SUCCESS")
            else:
                actions_taken.append(f"{action_str}: FAILED")
                logger.warning(f"  {action_str}: FAILED")
                success = False

        elapsed = time.time() - start_time

        result = {
            "success": success,
            "actions_taken": actions_taken,
            "elapsed_s": round(elapsed, 2),
            "demo_mode": self.demo_mode,
            "target_s": self.target_seconds,
            "within_target": elapsed <= self.target_seconds,
        }

        logger.info(f"Remediation complete: {result}")
        return result

    def _execute_step(self, action: str, target: str) -> bool:
        """Execute a single remediation step. Returns True on success."""
        if self.demo_mode:
            return self._simulate_action(action, target)

        if action == "restart_service":
            if self._docker is not None:
                return self._docker.restart_service(target)
            return False

        elif action == "scale_service":
            if self._docker is not None:
                return self._docker.scale_service(target, 2)
            return False

        else:
            logger.warning(f"Unknown action: {action}")
            return False

    def _simulate_action(self, action: str, target: str) -> bool:
        """Simulate action in demo mode."""
        logger.info(f"  [DEMO] Simulating {action}({target})")
        time.sleep(0.05)  # Brief delay to simulate work
        return True

    def get_playbook(self, failure_type: str) -> List[Dict]:
        return PLAYBOOKS.get(failure_type, PLAYBOOKS["generic_anomaly"])

    def list_playbooks(self) -> Dict[str, List]:
        return {k: v for k, v in PLAYBOOKS.items()}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test in demo mode
    engine = RemediationEngine(target_seconds=15, demo_mode=True)
    result = engine.remediate("recommendationservice", "memory_leak")
    print(f"Result: {result}")

    result2 = engine.remediate("checkoutservice", "network_latency")
    print(f"Result2: {result2}")
