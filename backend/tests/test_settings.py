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
    def test_production_mode_requires_models_when_demo_disabled(self):
        with patch.dict(os.environ, {"AEGIS_RUNTIME_MODE": "production", "AEGIS_ALLOW_DEMO_MODE": "false"}, clear=False):
            settings = load_settings()
            self.assertTrue(settings.is_production)
            self.assertTrue(settings.requires_models)

    def test_default_dev_mode_allows_demo(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = load_settings()
            self.assertEqual(settings.runtime_mode, "dev")
            self.assertFalse(settings.requires_models)


if __name__ == "__main__":
    unittest.main()
