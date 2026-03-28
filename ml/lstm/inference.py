#!/usr/bin/env python3

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import torch
from torch import nn

REPO_ROOT = Path(__file__).resolve().parents[2]
WINDOW_SIZE = 8
FEATURE_COUNT = 33
HIDDEN_SIZE = 64
NUM_LAYERS = 2


def _model_path() -> Path:
    configured = os.getenv("AEGIS_MODEL_DIR", "models/aegis_models")
    path = Path(configured)
    base = path if path.is_absolute() else REPO_ROOT / path
    return base / "lstm_model.pth"


class AegisLSTM(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=FEATURE_COUNT,
            hidden_size=HIDDEN_SIZE,
            num_layers=NUM_LAYERS,
            batch_first=True,
        )
        self.fc = nn.Linear(HIDDEN_SIZE, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        output, _ = self.lstm(x)
        logits = self.fc(output[:, -1, :])
        return torch.sigmoid(logits)


class LSTMInference:
    def __init__(self, window_size: int = WINDOW_SIZE) -> None:
        self.window_size = window_size
        self.n_features = FEATURE_COUNT
        self.model: Optional[AegisLSTM] = None
        self.loaded_from: Optional[str] = None

    def load(self) -> bool:
        model_path = _model_path()
        if not model_path.exists():
            raise FileNotFoundError(f"LSTM model artifact not found at {model_path}")
        state_dict = torch.load(model_path, map_location="cpu")
        if not isinstance(state_dict, dict):
            raise RuntimeError("Unsupported LSTM checkpoint format")

        model = AegisLSTM()
        model.load_state_dict(state_dict)
        model.eval()

        self.model = model
        self.loaded_from = str(model_path)
        return True

    def predict(self, sequence_array: np.ndarray) -> float:
        if self.model is None:
            raise RuntimeError("LSTM model is not loaded")

        seq = np.array(sequence_array, dtype=np.float32)
        if seq.ndim == 2:
            seq = seq[np.newaxis, :, :]
        if seq.shape[1] != self.window_size or seq.shape[2] != self.n_features:
            raise ValueError(
                f"LSTM expected input shape (*, {self.window_size}, {self.n_features}) "
                f"but received {seq.shape}"
            )

        with torch.inference_mode():
            tensor = torch.from_numpy(seq)
            pred = self.model(tensor).cpu().numpy()
        return float(pred[0, 0])

    def metadata(self) -> Dict[str, object]:
        if self.model is None:
            return {"loaded": False}
        return {
            "loaded": True,
            "type": "pytorch_lstm",
            "window_size": self.window_size,
            "feature_count": self.n_features,
            "hidden_size": HIDDEN_SIZE,
            "num_layers": NUM_LAYERS,
            "path": self.loaded_from,
        }


_instance: Optional[LSTMInference] = None


def get_instance() -> LSTMInference:
    global _instance
    if _instance is None:
        _instance = LSTMInference()
        _instance.load()
    return _instance
