import os
import sys
import unittest
from unittest.mock import patch


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_ROOT = os.path.join(REPO_ROOT, "backend")
for path in [REPO_ROOT, BACKEND_ROOT]:
    if path not in sys.path:
        sys.path.insert(0, path)

from anomaly_api.settings import load_settings


class SettingsTests(unittest.TestCase):
    def test_production_mode_is_detected(self):
        with patch.dict(os.environ, {"AEGIS_RUNTIME_MODE": "production"}, clear=False):
            settings = load_settings()
            self.assertTrue(settings.is_production)

    def test_default_dev_mode_and_model_dir(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = load_settings()
            self.assertEqual(settings.runtime_mode, "dev")
            self.assertEqual(settings.model_dir, "models/aegis_models")
            self.assertEqual(settings.system_db_path, "backend/.runtime/aegis_system.db")
            self.assertGreater(settings.predictive_alert_threshold, 0.0)
            self.assertGreater(settings.predictive_auto_action_threshold, settings.predictive_alert_threshold)

    def test_google_oauth_settings_are_loaded(self):
        with patch.dict(
            os.environ,
            {
                "AEGIS_GOOGLE_OAUTH_ENABLED": "true",
                "AEGIS_GOOGLE_CLIENT_ID": "client-id.apps.googleusercontent.com",
                "AEGIS_SESSION_COOKIE_SECURE": "true",
                "AEGIS_OPERATOR_EMAILS": "owner@example.com,ops@example.com",
            },
            clear=True,
        ):
            settings = load_settings()
            self.assertTrue(settings.google_oauth_enabled)
            self.assertEqual(settings.google_client_id, "client-id.apps.googleusercontent.com")
            self.assertTrue(settings.session_cookie_secure)
            self.assertEqual(settings.operator_emails, ["owner@example.com", "ops@example.com"])


if __name__ == "__main__":
    unittest.main()
