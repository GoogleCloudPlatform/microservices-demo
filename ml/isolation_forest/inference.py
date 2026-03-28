#!/usr/bin/env python3
"""
Isolation Forest Inference

Class IFInference with:
  - load(): loads model + scaler
  - score(feature_dict) -> float [0-1], higher = more anomalous
  - Falls back to demo_mode if model file is missing
"""

import os
import sys
import math
import time
import pickle
import numpy as np
from pathlib import Path
from typing import Dict

REPO_ROOT = Path(__file__).resolve().parents[2]

# Feature order must match training
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

MODEL_PATH = REPO_ROOT / "ml" / "isolation_forest" / "model" / "if_model.pkl"
SCALER_PATH = REPO_ROOT / "ml" / "isolation_forest" / "data" / "scaler.pkl"


class IFInference:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.threshold = None
        self.score_min = None
        self.score_max = None
        self.demo_mode = False
        self._demo_offset = hash(id(self)) % 100  # unique phase per instance

    def load(self) -> bool:
        """Load model and scaler. Returns True if successful, False = demo_mode."""
        try:
            if not MODEL_PATH.exists():
                print(f"[IFInference] Model not found at {MODEL_PATH} - using demo_mode")
                self.demo_mode = True
                return False

            with open(str(MODEL_PATH), "rb") as f:
                data = pickle.load(f)

            self.model = data["model"]
            self.threshold = data["threshold"]
            self.score_min, self.score_max = data["score_range"]

            if SCALER_PATH.exists():
                with open(str(SCALER_PATH), "rb") as f:
                    self.scaler = pickle.load(f)

            print(f"[IFInference] Model loaded. threshold={self.threshold:.4f}")
            self.demo_mode = False
            return True

        except Exception as e:
            print(f"[IFInference] Failed to load model: {e} - using demo_mode")
            self.demo_mode = True
            return False

    def _features_to_array(self, feature_dict: Dict) -> np.ndarray:
        """Convert feature dict to numpy array in correct order."""
        arr = np.zeros((1, len(FEATURE_COLUMNS)), dtype=np.float32)
        for i, col in enumerate(FEATURE_COLUMNS):
            arr[0, i] = float(feature_dict.get(col, 0.0))
        return arr

    def score(self, feature_dict: Dict) -> float:
        """
        Returns anomaly score [0-1]. Higher = more anomalous.
        """
        if self.demo_mode:
            return self._demo_score()

        try:
            arr = self._features_to_array(feature_dict)

            if self.scaler is not None:
                arr = self.scaler.transform(arr)

            # decision_function: higher = more normal (negative = anomalous)
            raw = self.model.decision_function(arr)[0]

            # Normalize to 0-1: invert so higher = more anomalous
            score_range = self.score_max - self.score_min
            if score_range < 1e-9:
                return 0.5

            # Clamp to known range
            raw_clamped = max(self.score_min, min(self.score_max, raw))
            # Invert: score_min -> 1.0, score_max -> 0.0
            normalized = 1.0 - (raw_clamped - self.score_min) / score_range
            return float(np.clip(normalized, 0.0, 1.0))

        except Exception as e:
            print(f"[IFInference] Score error: {e}")
            return self._demo_score()

    def _demo_score(self) -> float:
        """Sinusoidal demo score based on time."""
        t = time.time()
        phase = (t / 30.0 + self._demo_offset * 0.1) * 2 * math.pi
        # Score oscillates between 0.1 and 0.5
        return 0.3 + 0.2 * math.sin(phase)

    def score_batch(self, feature_dicts) -> list:
        """Score a list of feature dicts."""
        return [self.score(fd) for fd in feature_dicts]


# Convenience singleton
_instance = None


def get_instance() -> IFInference:
    global _instance
    if _instance is None:
        _instance = IFInference()
        _instance.load()
    return _instance


if __name__ == "__main__":
    inf = IFInference()
    inf.load()
    test_feat = {col: 0.5 for col in FEATURE_COLUMNS}
    print(f"Test score: {inf.score(test_feat):.4f}")
