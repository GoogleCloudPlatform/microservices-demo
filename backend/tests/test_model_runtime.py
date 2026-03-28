import os
import sys
import unittest

import numpy as np


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_ROOT = os.path.join(REPO_ROOT, "backend")
for path in [REPO_ROOT, BACKEND_ROOT]:
    if path not in sys.path:
        sys.path.insert(0, path)

from ml.isolation_forest.inference import IFInference
from ml.lstm.inference import LSTMInference


class ModelRuntimeTests(unittest.TestCase):
    def test_uploaded_models_load_and_score(self):
        if_model = IFInference()
        lstm_model = LSTMInference()

        self.assertTrue(if_model.load())
        self.assertTrue(lstm_model.load())

        x2 = np.zeros((if_model.feature_count,), dtype=np.float32)
        x3 = np.zeros((lstm_model.window_size, lstm_model.n_features), dtype=np.float32)

        if_score = if_model.score_vector(x2.tolist())
        lstm_score = lstm_model.predict(x3)

        self.assertGreaterEqual(if_score, 0.0)
        self.assertLessEqual(if_score, 1.0)
        self.assertGreaterEqual(lstm_score, 0.0)
        self.assertLessEqual(lstm_score, 1.0)


if __name__ == "__main__":
    unittest.main()
