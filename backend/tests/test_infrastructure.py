import os
import sys
import unittest
from unittest.mock import patch


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_ROOT = os.path.join(REPO_ROOT, "backend")
for path in [REPO_ROOT, BACKEND_ROOT]:
    if path not in sys.path:
        sys.path.insert(0, path)

from anomaly_api.infrastructure import build_infrastructure_payload
from anomaly_api.settings import load_settings


class _FakeWorkload:
    def __init__(self, service):
        self.service = service

    def to_dict(self):
        return {
            "service": self.service,
            "exists": True,
            "running": True,
            "healthy": True,
            "status": "running",
            "restart_count": 1,
            "oom_killed": False,
            "metadata": {},
        }


class _FakeOrchestrator:
    platform = "kubernetes"

    def inspect_service(self, service_name):
        return _FakeWorkload(service_name)

    def cluster_overview(self):
        return {
            "available": True,
            "platform": "kubernetes",
            "status": "healthy",
            "summary": "all green",
            "nodes": {"ready": 2, "total": 2},
            "pods": {"running": 12, "pending": 0, "failed": 0, "total": 12},
            "deployments": {"unavailable": 0, "total": 8},
        }


class _FakeMemory:
    def list_recent(self, limit=10):
        return [{"incident_id": "abc", "service": "frontend"}]


class _FakeEngine:
    def __init__(self):
        self.orchestrator = _FakeOrchestrator()
        self.memory_store = _FakeMemory()
        self.target_seconds = 15

    def cooldown_snapshot(self):
        return {"frontend": "2026-03-28T10:00:00Z"}

    def lease_snapshot(self):
        return {"frontend": "incident-1"}


class InfrastructurePayloadTests(unittest.TestCase):
    @patch("anomaly_api.infrastructure._safe_json")
    def test_build_payload_contains_expected_sections(self, safe_json):
        safe_json.side_effect = [
            {"ok": True, "json": {"data": {"activeTargets": [{"health": "up"}]}}},
            {"ok": True, "json": {}},
            {"ok": True, "json": {"database": "ok"}},
            {"ok": True, "json": {"data": ["frontend"]}},
            {"ok": True, "json": {}},
            {"ok": True, "json": {}},
        ]
        with patch.dict(os.environ, {"AEGIS_INFRA_COLLECTORS_ENABLED": "true"}, clear=True):
            settings = load_settings()
        payload = build_infrastructure_payload(
            settings=settings,
            topology={
                "timestamp": "2026-03-28T10:00:00Z",
                "services": {
                    "frontend": {
                        "status": "normal",
                        "combined_score": 0.12,
                        "latest_incident": None,
                        "similar_incidents": [],
                    }
                },
                "active_incidents": [],
                "recent_incidents": [],
            },
            history=[{"timestamp": "2026-03-28T10:00:00Z", "scores": {"frontend": 0.12}}],
            remediation_engine=_FakeEngine(),
        )
        self.assertIn("environment", payload)
        self.assertIn("fleet_summary", payload)
        self.assertIn("workloads", payload)
        self.assertIn("observability", payload)
        self.assertIn("cluster", payload)
        self.assertIn("remediation", payload)
        self.assertIn("memory", payload)
        self.assertTrue(payload["cluster"]["available"])
        self.assertTrue(payload["observability"]["prometheus"]["available"])
        self.assertTrue(payload["observability"]["promtail"]["available"])


if __name__ == "__main__":
    unittest.main()
