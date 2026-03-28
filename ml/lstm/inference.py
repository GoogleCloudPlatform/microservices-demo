#!/usr/bin/env python3
"""
LSTM Inference

Class LSTMInference with:
  - load(): loads model
  - predict(sequence_array) -> float [0-1]
  - Rolling buffer for live prediction
  - demo_mode fallback if model missing
"""

import math
import time
import pickle
import numpy as np
from pathlib import Path
from collections import deque
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]

MODEL_DIR = REPO_ROOT / "ml" / "lstm" / "model"
WINDOW_SIZE = 20

FEATURE_COLUMNS = [
    "cpu_percent",
    "mem_percent",
    "net_rx_mb",
    "net_tx_mb",
    "block_read_mb",
    "block_write_mb",
    "log_count",
    "error_rate",
    "warn_rate",
    "template_entropy",
]


class LSTMInference:
    def __init__(self, window_size: int = WINDOW_SIZE):
        self.model = None
        self.model_type = None  # "tensorflow", "sklearn", "demo"
        self.window_size = window_size
        self.n_features = len(FEATURE_COLUMNS)
        self.demo_mode = False
        self._buffer = deque(maxlen=window_size)
        self._demo_offset = time.time() % 100

    def load(self) -> bool:
        """
        Loads model. Returns True if successful, False = demo_mode.
        Tries .keras, .h5, .pkl in order.
        """
        # Try TensorFlow models
        for ext in ["lstm_model.keras", "lstm_model.h5"]:
            model_path = MODEL_DIR / ext
            if model_path.exists():
                try:
                    import tensorflow as tf
                    self.model = tf.keras.models.load_model(str(model_path), compile=False)
                    self.model_type = "tensorflow"
                    print(f"[LSTMInference] TensorFlow model loaded from {model_path}")
                    self.demo_mode = False
                    return True
                except Exception as e:
                    print(f"[LSTMInference] Failed to load {model_path}: {e}")

        # Try sklearn fallback
        pkl_path = MODEL_DIR / "lstm_model.pkl"
        if pkl_path.exists():
            try:
                with open(str(pkl_path), "rb") as f:
                    data = pickle.load(f)
                self.model = data["model"]
                self.model_type = "sklearn"
                print(f"[LSTMInference] Sklearn model loaded from {pkl_path}")
                self.demo_mode = False
                return True
            except Exception as e:
                print(f"[LSTMInference] Failed to load sklearn model: {e}")

        print(f"[LSTMInference] No model found - using demo_mode")
        self.demo_mode = True
        self.model_type = "demo"
        return False

    def predict(self, sequence_array: np.ndarray) -> float:
        """
        Predict failure probability from sequence.
        sequence_array shape: (window_size, n_features)
        Returns: float [0-1]
        """
        if self.demo_mode:
            return self._demo_score()

        try:
            seq = np.array(sequence_array, dtype=np.float32)
            if seq.ndim == 2:
                seq = seq[np.newaxis, :, :]  # (1, T, F)

            if self.model_type == "tensorflow":
                pred = self.model.predict(seq, verbose=0)
                return float(pred[0, 0])

            elif self.model_type == "sklearn":
                T, F = seq.shape[1], seq.shape[2]
                flat = seq.reshape(1, T * F)
                prob = self.model.predict_proba(flat)[0, 1]
                return float(prob)

        except Exception as e:
            print(f"[LSTMInference] Predict error: {e}")
            return self._demo_score()

        return self._demo_score()

    def predict_from_features(self, feature_dict: dict) -> Optional[float]:
        """
        Push one feature vector to rolling buffer, predict when full.
        Returns None if buffer not full yet.
        """
        vec = np.zeros(self.n_features, dtype=np.float32)
        for i, col in enumerate(FEATURE_COLUMNS):
            vec[i] = float(feature_dict.get(col, 0.0))

        self._buffer.append(vec)

        if len(self._buffer) < self.window_size:
            return None

        sequence = np.array(list(self._buffer), dtype=np.float32)
        return self.predict(sequence)

    def get_buffer_fill(self) -> float:
        """Returns fraction of buffer filled [0-1]."""
        return len(self._buffer) / self.window_size

    def _demo_score(self) -> float:
        """Sinusoidal demo score."""
        t = time.time()
        phase = (t / 45.0 + self._demo_offset * 0.07) * 2 * math.pi
        return float(np.clip(0.25 + 0.2 * math.sin(phase), 0.0, 1.0))


# Convenience singleton
_instance = None


def get_instance() -> LSTMInference:
    global _instance
    if _instance is None:
        _instance = LSTMInference()
        _instance.load()
    return _instance


if __name__ == "__main__":
    inf = LSTMInference()
    inf.load()

    # Test with random sequence
    seq = np.random.randn(WINDOW_SIZE, len(FEATURE_COLUMNS)).astype(np.float32)
    score = inf.predict(seq)
    print(f"Test prediction: {score:.4f}")
