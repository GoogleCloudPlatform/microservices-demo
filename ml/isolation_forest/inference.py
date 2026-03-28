#!/usr/bin/env python3

from __future__ import annotations

import os
import pickle
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]


def _model_dir() -> Path:
    configured = os.getenv("AEGIS_MODEL_DIR", "models/aegis_models")
    path = Path(configured)
    return path if path.is_absolute() else REPO_ROOT / path


class IFInference:
    def __init__(self) -> None:
        self.model = None
        self.scaler = None
        self.threshold: Optional[float] = None
        self.feature_count = 66
        self.loaded_from: Optional[str] = None

    def load(self) -> bool:
        model_dir = _model_dir()
        model_path = model_dir / "if_model.pkl"
        scaler_path = model_dir / "scaler.pkl"
        if not model_path.exists():
            raise FileNotFoundError(f"Isolation Forest artifact not found at {model_path}")
        if not scaler_path.exists():
            raise FileNotFoundError(f"Isolation Forest scaler not found at {scaler_path}")

        with open(model_path, "rb") as handle:
            payload = pickle.load(handle)
        if isinstance(payload, dict):
            self.model = payload.get("model")
            self.threshold = float(payload.get("threshold", 0.0))
        else:
            self.model = payload
            self.threshold = 0.0
        with open(scaler_path, "rb") as handle:
            self.scaler = pickle.load(handle)

        if self.model is None or self.scaler is None:
            raise RuntimeError("Isolation Forest artifacts loaded but model or scaler is missing")
        self.feature_count = int(getattr(self.scaler, "n_features_in_", self.feature_count))
        self.loaded_from = str(model_dir)
        return True

    def score_vector(self, feature_vector: Dict[str, float] | List[float] | np.ndarray) -> float:
        if self.model is None or self.scaler is None:
            raise RuntimeError("Isolation Forest model is not loaded")

        if isinstance(feature_vector, dict):
            values = list(feature_vector.values())
        else:
            values = feature_vector
        arr = np.array(values, dtype=np.float32).reshape(1, -1)
        if arr.shape[1] != self.feature_count:
            raise ValueError(f"Isolation Forest expected {self.feature_count} features but received {arr.shape[1]}")

        scaled = self.scaler.transform(arr)
        raw = float(self.model.decision_function(scaled)[0])
        threshold = float(self.threshold or 0.0)
        # Lower decision_function values are more anomalous. Map threshold-crossing behavior to [0, 1].
        delta = threshold - raw
        score = 1.0 / (1.0 + np.exp(-6.0 * delta))
        return float(np.clip(score, 0.0, 1.0))

    def score(self, feature_vector: Dict[str, float] | List[float] | np.ndarray) -> float:
        return self.score_vector(feature_vector)

    def metadata(self) -> Dict[str, object]:
        if self.model is None or self.scaler is None:
            return {"loaded": False}
        return {
            "loaded": True,
            "type": type(self.model).__name__,
            "feature_count": self.feature_count,
            "threshold": self.threshold,
            "path": self.loaded_from,
        }

    @property
    def scaler_mean(self) -> Optional[np.ndarray]:
        return getattr(self.scaler, "mean_", None)

    @property
    def scaler_scale(self) -> Optional[np.ndarray]:
        return getattr(self.scaler, "scale_", None)


_instance: Optional[IFInference] = None


def get_instance() -> IFInference:
    global _instance
    if _instance is None:
        _instance = IFInference()
        _instance.load()
    return _instance
