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

from remediation.memory import SQLiteIncidentMemoryStore
from remediation.models import MemoryRecord


class MemoryStoreTests(unittest.TestCase):
    def test_hybrid_similarity_prefers_matching_service_and_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SQLiteIncidentMemoryStore(Path(tmpdir) / "incidents.db")
            store.save(
                MemoryRecord(
                    incident_id="1",
                    service="redis-cart",
                    failure_type="memory_leak",
                    severity="critical",
                    feature_flags=["memory_high", "restart_flapping"],
                    evidence_summary="redis oom killed during traffic spike",
                    metric_signature={"mem_percent": 92.0, "combined_score": 0.91},
                    selected_action="restart_service",
                    outcome="resolved",
                )
            )
            store.save(
                MemoryRecord(
                    incident_id="2",
                    service="frontend",
                    failure_type="network_latency",
                    severity="warning",
                    feature_flags=["error_rate_high"],
                    evidence_summary="frontend slow downstream request",
                    metric_signature={"mem_percent": 32.0, "combined_score": 0.48},
                    selected_action="restart_dependency_chain",
                    outcome="contained",
                )
            )

            matches = store.find_similar(
                service="redis-cart",
                failure_type="memory_leak",
                feature_flags=["memory_high"],
                metric_signature={"mem_percent": 90.0, "combined_score": 0.88},
                evidence_summary="redis oom",
                limit=2,
            )
            self.assertEqual(matches[0]["incident_id"], "1")
            self.assertGreater(matches[0]["similarity_score"], matches[1]["similarity_score"])

    def test_store_prunes_to_max_records(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SQLiteIncidentMemoryStore(Path(tmpdir) / "incidents.db", max_records=2, retention_days=365)
            for incident_id in ["1", "2", "3"]:
                store.save(
                    MemoryRecord(
                        incident_id=incident_id,
                        service="frontend",
                        failure_type="generic_anomaly",
                        severity="warning",
                        selected_action="restart_service",
                        outcome="resolved",
                    )
                )
            recent = store.list_recent(limit=10)
            self.assertEqual(len(recent), 2)
            self.assertEqual({item["incident_id"] for item in recent}, {"2", "3"})


if __name__ == "__main__":
    unittest.main()
