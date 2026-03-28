import os
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_ROOT = os.path.join(REPO_ROOT, "backend")
for path in [REPO_ROOT, BACKEND_ROOT]:
    if path not in sys.path:
        sys.path.insert(0, path)

from remediation.engine import RemediationEngine
from remediation.memory import SQLiteIncidentMemoryStore
from remediation.models import ActionDecision, WorkloadState
from remediation.orchestrator import OrchestratorAdapter


class FakeOrchestrator(OrchestratorAdapter):
    def __init__(self, becomes_healthy=True):
        self.state = WorkloadState(
            service="recommendationservice",
            exists=True,
            running=True,
            healthy=False,
            status="running",
        )
        self.becomes_healthy = becomes_healthy

    def inspect_service(self, service_name: str) -> WorkloadState:
        self.state.service = service_name
        return self.state

    def restart_service(self, service_name: str):
        if self.becomes_healthy:
            self.state.running = True
            self.state.healthy = True
            self.state.status = "running"
            return True, "restarted", self.state.to_dict()
        return False, "restart failed", {}

    def stop_service(self, service_name: str):
        self.state.running = False
        self.state.healthy = False
        self.state.status = "exited"
        return True, "stopped", self.state.to_dict()

    def start_service(self, service_name: str):
        self.state.running = True
        self.state.healthy = True
        self.state.status = "running"
        return True, "started", self.state.to_dict()

    def isolate_service(self, service_name: str):
        return self.stop_service(service_name)

    def discover_healthy_alternatives(self, service_name: str):
        return []

    @property
    def available(self):
        return True

    @property
    def platform(self):
        return "fake"


class FakePolicyEngine:
    def __init__(self, decision: ActionDecision):
        self.decision = decision

    def build_decision(self, incident, runtime_state, similar_incidents, proposal):
        return self.decision


class RemediationEngineTests(unittest.TestCase):
    def test_engine_resolves_happy_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            scores = iter(
                [
                    {"recommendationservice": {"combined_score": 0.92}},
                    {"recommendationservice": {"combined_score": 0.22}},
                ]
            )
            engine = RemediationEngine(
                score_provider=lambda: next(scores),
                orchestrator=FakeOrchestrator(becomes_healthy=True),
                memory_store=SQLiteIncidentMemoryStore(Path(tmpdir) / "incidents.db"),
            )
            engine.policy_engine = FakePolicyEngine(
                ActionDecision(
                    action="restart_service",
                    target="recommendationservice",
                    retry_budget=0,
                    evaluation_window_s=0.0,
                    containment_actions=["isolate_service", "escalate_incident"],
                )
            )
            result = engine.remediate("recommendationservice", "memory_leak")
            self.assertEqual(result["status"], "resolved")
            self.assertEqual(result["decision"]["action"], "restart_service")

    def test_engine_enters_containment_when_restart_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            scores = iter(
                [
                    {"recommendationservice": {"combined_score": 0.95}},
                    {"recommendationservice": {"combined_score": 0.94}},
                    {"recommendationservice": {"combined_score": 0.94}},
                ]
            )
            engine = RemediationEngine(
                score_provider=lambda: next(scores),
                orchestrator=FakeOrchestrator(becomes_healthy=False),
                memory_store=SQLiteIncidentMemoryStore(Path(tmpdir) / "incidents.db"),
            )
            engine.policy_engine = FakePolicyEngine(
                ActionDecision(
                    action="restart_service",
                    target="recommendationservice",
                    retry_budget=0,
                    evaluation_window_s=0.0,
                    containment_actions=["isolate_service", "escalate_incident"],
                )
            )
            result = engine.remediate("recommendationservice", "generic_anomaly")
            self.assertEqual(result["containment"]["containment_mode"], "isolate")
            self.assertIn(result["status"], {"contained", "manual_required"})
            self.assertEqual(len(engine.list_active_incidents()), 1)

    def test_manual_required_incident_can_be_acknowledged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            scores = iter(
                [
                    {"recommendationservice": {"combined_score": 0.95}},
                    {"recommendationservice": {"combined_score": 0.94}},
                    {"recommendationservice": {"combined_score": 0.94}},
                ]
            )
            engine = RemediationEngine(
                score_provider=lambda: next(scores),
                orchestrator=FakeOrchestrator(becomes_healthy=False),
                memory_store=SQLiteIncidentMemoryStore(Path(tmpdir) / "incidents.db"),
            )
            engine.policy_engine = FakePolicyEngine(
                ActionDecision(
                    action="restart_service",
                    target="recommendationservice",
                    retry_budget=0,
                    evaluation_window_s=0.0,
                    containment_actions=["isolate_service", "escalate_incident"],
                )
            )
            result = engine.remediate("recommendationservice", "generic_anomaly")
            incident_id = result["incident_id"]
            acknowledged = engine.acknowledge_incident(incident_id, owner="ishu")
            self.assertTrue(acknowledged["acknowledged"])
            self.assertEqual(acknowledged["acknowledged_by"], "ishu")
            self.assertEqual(acknowledged["current_phase"], "manual_acknowledged")

    def test_engine_blocks_repeat_action_during_cooldown(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            scores = iter(
                [
                    {"recommendationservice": {"combined_score": 0.92}},
                    {"recommendationservice": {"combined_score": 0.12}},
                ]
            )
            engine = RemediationEngine(
                score_provider=lambda: next(scores),
                orchestrator=FakeOrchestrator(becomes_healthy=True),
                memory_store=SQLiteIncidentMemoryStore(Path(tmpdir) / "incidents.db"),
                cooldown_s=60.0,
            )
            engine.policy_engine = FakePolicyEngine(
                ActionDecision(
                    action="restart_service",
                    target="recommendationservice",
                    retry_budget=0,
                    evaluation_window_s=0.0,
                    containment_actions=["isolate_service", "escalate_incident"],
                )
            )
            first = engine.remediate("recommendationservice", "memory_leak")
            second = engine.remediate("recommendationservice", "memory_leak")
            self.assertEqual(first["status"], "resolved")
            self.assertEqual(second["status"], "manual_required")
            self.assertEqual(second["current_phase"], "guard")


if __name__ == "__main__":
    unittest.main()
