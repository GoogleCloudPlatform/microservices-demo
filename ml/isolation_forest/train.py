#!/usr/bin/env python3
"""
Isolation Forest Training Script

Loads X_normal.npy + scaler.pkl, trains IsolationForest,
saves model to ml/isolation_forest/model/if_model.pkl
"""

import sys
import os
import pickle
import numpy as np
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

DATA_DIR = REPO_ROOT / "ml" / "isolation_forest" / "data"
MODEL_DIR = REPO_ROOT / "ml" / "isolation_forest" / "model"


def main():
    print("=" * 60)
    print("Training Isolation Forest")
    print("=" * 60)

    # Load data
    X_path = DATA_DIR / "X_normal.npy"
    scaler_path = DATA_DIR / "scaler.pkl"

    if not X_path.exists():
        print(f"ERROR: {X_path} not found. Run build_training_dataset.py first.")
        sys.exit(1)

    print(f"\nLoading X_normal from {X_path}")
    X_normal = np.load(str(X_path))
    print(f"  Shape: {X_normal.shape}")

    # Load scaler
    with open(str(scaler_path), "rb") as f:
        scaler = pickle.load(f)
    print(f"  Scaler loaded from {scaler_path}")

    # Train Isolation Forest
    from sklearn.ensemble import IsolationForest

    print("\nTraining IsolationForest(n_estimators=200, contamination=0.05)...")
    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_normal)

    # Compute scores on training data
    scores = model.decision_function(X_normal)  # Higher = more normal
    threshold = np.percentile(scores, 5)  # 5th percentile = anomaly threshold

    print(f"\nTraining complete:")
    print(f"  n_samples:         {X_normal.shape[0]}")
    print(f"  anomaly_threshold: {threshold:.4f}")
    print(f"  score_range:       [{scores.min():.4f}, {scores.max():.4f}]")
    print(f"  score_mean:        {scores.mean():.4f}")

    # Save model
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / "if_model.pkl"
    with open(str(model_path), "wb") as f:
        pickle.dump({"model": model, "threshold": threshold, "score_range": (scores.min(), scores.max())}, f)

    print(f"\nModel saved to {model_path}")


if __name__ == "__main__":
    main()
