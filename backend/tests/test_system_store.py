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

from anomaly_api.system_store import SQLiteSystemStore


class SystemStoreTests(unittest.TestCase):
    def test_events_and_logs_are_persisted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "system.db"
            store = SQLiteSystemStore(db_path)

            store.add_event(
                event_type="predictive_alert",
                category="prediction",
                severity="warning",
                title="Alert raised",
                message="LSTM predicts rising failure risk.",
                service="frontend",
                payload={"score": 0.81},
            )
            store.add_log(
                level="WARNING",
                logger_name="aegis.test",
                message="Predictive threshold crossed",
                context={"service": "frontend"},
            )

            events = store.list_events(limit=5)
            logs = store.list_logs(limit=5)

            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["service"], "frontend")
            self.assertEqual(events[0]["payload"]["score"], 0.81)
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]["level"], "WARNING")
            self.assertEqual(logs[0]["context"]["service"], "frontend")

    def test_user_accounts_and_sessions_are_persisted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "system.db"
            store = SQLiteSystemStore(db_path)

            user = store.upsert_user_account(
                google_sub="google-sub-123",
                email="owner@example.com",
                name="Owner",
                picture_url="https://example.com/avatar.png",
                verified_email=True,
                role="operator",
            )
            session = store.create_user_session(
                user_id=user["id"],
                ttl_seconds=3600,
                user_agent="pytest",
                ip_address="127.0.0.1",
            )
            looked_up = store.get_user_session(session["token"])

            self.assertIsNotNone(looked_up)
            self.assertEqual(looked_up["user"]["email"], "owner@example.com")
            self.assertEqual(looked_up["user"]["role"], "operator")

            store.revoke_user_session(session["token"])
            self.assertIsNone(store.get_user_session(session["token"]))


if __name__ == "__main__":
    unittest.main()
