#!/usr/bin/env python3
"""
LSTM Training Script

Tries to use TensorFlow/Keras if available.
Falls back to a sklearn-based approach if not.

Architecture (TF): LSTM(64) -> Dropout(0.3) -> LSTM(32) -> Dropout(0.2) -> Dense(1, sigmoid)
Uses focal loss (gamma=2, alpha=0.25)
"""

import sys
import os
import json
import pickle
import numpy as np
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

DATA_DIR = REPO_ROOT / "ml" / "lstm" / "data"
MODEL_DIR = REPO_ROOT / "ml" / "lstm" / "model"


def focal_loss(gamma=2.0, alpha=0.25):
    """Focal loss for binary classification."""
    try:
        import tensorflow as tf

        def loss_fn(y_true, y_pred):
            y_true = tf.cast(y_true, tf.float32)
            p_t = y_true * y_pred + (1 - y_true) * (1 - y_pred)
            alpha_t = y_true * alpha + (1 - y_true) * (1 - alpha)
            focal_weight = alpha_t * tf.pow(1 - p_t, gamma)
            bce = -tf.math.log(tf.clip_by_value(p_t, 1e-7, 1.0))
            return tf.reduce_mean(focal_weight * bce)

        return loss_fn
    except ImportError:
        return "binary_crossentropy"


def train_with_tensorflow(X, y):
    """Train LSTM with TensorFlow/Keras."""
    import tensorflow as tf
    from tensorflow import keras

    print(f"  TensorFlow version: {tf.__version__}")

    n_timesteps = X.shape[1]
    n_features = X.shape[2]

    # Class weights
    n_pos = y.sum()
    n_neg = len(y) - n_pos
    if n_pos > 0:
        class_weight = {0: 1.0, 1: float(n_neg / n_pos)}
    else:
        class_weight = {0: 1.0, 1: 1.0}

    print(f"  Class weights: {class_weight}")

    model = keras.Sequential([
        keras.layers.LSTM(64, return_sequences=True, input_shape=(n_timesteps, n_features)),
        keras.layers.Dropout(0.3),
        keras.layers.LSTM(32),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(1, activation="sigmoid"),
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss=focal_loss(gamma=2.0, alpha=0.25),
        metrics=["accuracy", keras.metrics.AUC(name="auc")],
    )

    model.summary()

    # Train
    history = model.fit(
        X, y,
        epochs=30,
        batch_size=64,
        validation_split=0.2,
        class_weight=class_weight,
        verbose=1,
    )

    # Try .keras first, fall back to .h5
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / "lstm_model.keras"
    try:
        model.save(str(model_path))
    except Exception:
        model_path = MODEL_DIR / "lstm_model.h5"
        model.save(str(model_path))

    # Save history
    hist_dict = {k: [float(v) for v in vals] for k, vals in history.history.items()}
    with open(str(MODEL_DIR / "history.json"), "w") as f:
        json.dump(hist_dict, f, indent=2)

    final_epoch = -1
    val_loss = hist_dict.get("val_loss", [None])[final_epoch]
    val_acc = hist_dict.get("val_accuracy", [None])[final_epoch]
    val_auc = hist_dict.get("val_auc", [None])[final_epoch]

    print(f"\nFinal metrics (epoch 30):")
    print(f"  val_loss:     {val_loss}")
    print(f"  val_accuracy: {val_acc}")
    print(f"  val_auc:      {val_auc}")

    return str(model_path)


def train_sklearn_fallback(X, y):
    """
    NumPy/sklearn fallback when TensorFlow not available.
    Trains a simple GradientBoosting on flattened sequences.
    Saves a compatible model dict.
    """
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import train_test_split

    print("  Using sklearn GradientBoosting fallback (TensorFlow not available)")

    # Flatten sequences: (N, T, F) -> (N, T*F)
    N, T, F = X.shape
    X_flat = X.reshape(N, T * F)

    X_train, X_val, y_train, y_val = train_test_split(X_flat, y, test_size=0.2, random_state=42)

    model = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict_proba(X_val)[:, 1]
    val_loss = float(np.mean(-(y_val * np.log(y_pred + 1e-7) + (1 - y_val) * np.log(1 - y_pred + 1e-7))))
    val_acc = float(np.mean((y_pred > 0.5) == y_val))
    try:
        val_auc = float(roc_auc_score(y_val, y_pred))
    except Exception:
        val_auc = 0.5

    print(f"\nFinal metrics:")
    print(f"  val_loss:     {val_loss:.4f}")
    print(f"  val_accuracy: {val_acc:.4f}")
    print(f"  val_auc:      {val_auc:.4f}")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    model_data = {
        "type": "sklearn_fallback",
        "model": model,
        "input_shape": (T, F),
        "val_loss": val_loss,
        "val_accuracy": val_acc,
        "val_auc": val_auc,
    }
    model_path = MODEL_DIR / "lstm_model.pkl"
    with open(str(model_path), "wb") as f:
        pickle.dump(model_data, f)

    history = {
        "val_loss": [val_loss],
        "val_accuracy": [val_acc],
        "val_auc": [val_auc],
    }
    with open(str(MODEL_DIR / "history.json"), "w") as f:
        json.dump(history, f, indent=2)

    return str(model_path)


def main():
    print("=" * 60)
    print("Training LSTM / Sequence Model")
    print("=" * 60)

    # Load data
    X_path = DATA_DIR / "X_sequences.npy"
    y_path = DATA_DIR / "y_sequences.npy"

    if not X_path.exists():
        print(f"ERROR: {X_path} not found. Run build_training_dataset.py first.")
        sys.exit(1)

    print(f"\nLoading sequences from {DATA_DIR}")
    X = np.load(str(X_path))
    y = np.load(str(y_path))

    print(f"  X shape: {X.shape}")
    print(f"  y shape: {y.shape}")
    print(f"  Positive rate: {y.mean():.4f}")

    # Try TensorFlow first
    try:
        import tensorflow as tf
        model_path = train_with_tensorflow(X, y)
    except ImportError:
        model_path = train_sklearn_fallback(X, y)

    print(f"\nModel saved to {model_path}")


if __name__ == "__main__":
    main()
