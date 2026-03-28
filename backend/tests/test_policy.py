import os
import sys
import unittest


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_ROOT = os.path.join(REPO_ROOT, "backend")
for path in [REPO_ROOT, BACKEND_ROOT]:
    if path not in sys.path:
        sys.path.insert(0, path)

from remediation.models import ActionProposal, Incident, WorkloadState
from remediation.policy import ActionPolicyEngine


class PolicyEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = ActionPolicyEngine()

    def test_memory_failure_prefers_restart(self):
        incident = Incident.create(
            service="recommendationservice",
            failure_type="memory_leak",
            evidence={"feature_flags": ["memory_high"]},
        )
        runtime = WorkloadState(
            service="recommendationservice",
            exists=True,
            running=True,
            healthy=False,
            status="running",
            oom_killed=True,
        )
        decision = self.engine.build_decision(incident, runtime, [], None)
        self.assertEqual(decision.action, "restart_service")
        self.assertEqual(decision.retry_budget, 2)
        self.assertIn("isolate_service", decision.containment_actions)

    def test_invalid_ai_action_is_clamped_to_policy(self):
        incident = Incident.create(service="frontend", failure_type="generic_anomaly")
        runtime = WorkloadState(service="frontend", exists=True, running=True, healthy=False, status="running")
        proposal = ActionProposal(
            source="ai",
            proposed_action="delete_namespace",
            confidence=0.99,
            rationale="unsafe suggestion",
        )
        decision = self.engine.build_decision(incident, runtime, [], proposal)
        self.assertEqual(decision.action, "restart_service")
        self.assertNotIn("delete_namespace", decision.allowed_actions)

    def test_dependency_failure_is_not_overridden_by_oom_signal(self):
        incident = Incident.create(
            service="cartservice",
            failure_type="dependency_failure",
            affected_services=["cartservice", "redis-cart"],
            evidence={"feature_flags": ["memory_high"]},
        )
        runtime = WorkloadState(
            service="cartservice",
            exists=True,
            running=True,
            healthy=False,
            status="degraded",
            oom_killed=True,
        )
        decision = self.engine.build_decision(incident, runtime, [], None)
        self.assertEqual(incident.failure_type, "dependency_failure")
        self.assertEqual(decision.action, "restart_dependency_chain")
        self.assertEqual(decision.parameters["chain"], ["redis-cart", "cartservice"])

    def test_dependency_failure_ignores_mismatched_memory_match(self):
        incident = Incident.create(
            service="redis-cart",
            failure_type="dependency_failure",
            affected_services=["redis-cart", "cartservice"],
        )
        runtime = WorkloadState(
            service="redis-cart",
            exists=True,
            running=True,
            healthy=False,
            status="degraded",
        )
        decision = self.engine.build_decision(
            incident,
            runtime,
            [
                {
                    "service": "recommendationservice",
                    "failure_type": "service_unhealthy",
                    "selected_action": "restart_service",
                    "outcome": "contained",
                }
            ],
            None,
        )
        self.assertEqual(decision.action, "restart_dependency_chain")
        self.assertEqual(decision.parameters["chain"], ["redis-cart"])


if __name__ == "__main__":
    unittest.main()
