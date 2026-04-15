from __future__ import annotations

"""
Clean ML model predictor — replaces model_utils_working.py.

Engineering trade-off: This class is intentionally *not* a singleton.
Lifecycle management is handled by the dependency injection layer
(dependencies.py), not by the class itself. This means:
  1. Tests can instantiate fresh predictors without fighting global state
  2. Multiple model versions can coexist (e.g., A/B testing)
  3. The class follows the Single Responsibility Principle: it predicts,
     it does not manage its own lifecycle

The lazy-load pattern (load on first predict) is preserved from the
original for backward compatibility, but callers should prefer explicit
load_model() at startup.
"""

import os
import pickle
from typing import Any

import numpy as np
import pandas as pd

from app.core.exceptions import ModelError


class KOIModelPredictor:
    """
    Kepler Objects of Interest classifier.

    Wraps a scikit-learn compatible model (RandomForest by default)
    with preprocessing and label mapping.
    """

    def __init__(self, model_path: str = "models/simple_test_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.feature_names: list[str] | None = None
        self.label_mapping: dict[int, str] | None = None
        self.accuracy: float | None = None
        self._loaded = False

    def load_model(self) -> None:
        """
        Load serialized model artifacts from disk.

        Raises ModelError if the file is missing or unpickling fails.
        """
        if not os.path.exists(self.model_path):
            raise ModelError(
                f"Model file not found at {self.model_path}. "
                "Ensure the model has been trained and serialized."
            )

        try:
            with open(self.model_path, "rb") as f:
                model_data = pickle.load(f)
        except Exception as exc:
            raise ModelError(f"Failed to deserialize model: {exc}") from exc

        self.model = model_data["model"]
        self.feature_names = model_data["feature_names"]
        self.label_mapping = model_data["label_mapping"]
        self.accuracy = model_data.get("accuracy")
        self._loaded = True

    def _ensure_loaded(self) -> None:
        """Lazy-load guard. Prefer explicit load_model() at startup."""
        if not self._loaded:
            self.load_model()

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare a raw DataFrame for prediction.

        Steps:
          1. Drop target/ID columns if present (prevents label leakage)
          2. Select only features used during training
          3. Impute missing values with column medians

        Median imputation formula per feature j:
            x_missing(j) ← median({x_i(j) | x_i(j) is not NaN})

        Trade-off: Median imputation is biased for non-symmetric
        distributions but is robust to outliers — appropriate for
        astronomical data with heavy tails (e.g., koi_insol spans
        6 orders of magnitude).
        """
        self._ensure_loaded()

        feature_df = df.copy()

        # Remove target and ID columns if present — prevents leakage.
        for col in ("koi_disposition", "kepid"):
            if col in feature_df.columns:
                feature_df = feature_df.drop(columns=[col])

        # Select only training features, preserving order.
        if self.feature_names:
            available = [c for c in self.feature_names if c in feature_df.columns]
            feature_df = feature_df[available]

        # Impute missing values with column median.
        feature_df = feature_df.fillna(feature_df.median())

        return feature_df

    def predict(self, df: pd.DataFrame) -> dict[str, Any]:
        """
        Run predictions on a DataFrame.

        Returns a dict with:
          - predictions: list[str]     — human-readable class labels
          - probabilities: list[list[float]] — per-class probabilities
          - original_data: list[dict]  — input records for analytics
          - model_accuracy: float | None
          - feature_count: int
        """
        self._ensure_loaded()

        X = self.preprocess(df)

        try:
            raw_predictions = self.model.predict(X)
            raw_probabilities = self.model.predict_proba(X)
        except Exception as exc:
            raise ModelError(f"Prediction failed: {exc}") from exc

        # Map integer labels → human-readable strings.
        labels = [
            self.label_mapping.get(int(pred), "UNKNOWN")
            for pred in raw_predictions
        ]

        return {
            "predictions": labels,
            "probabilities": raw_probabilities.tolist(),
            "original_data": df.to_dict("records"),
            "model_accuracy": self.accuracy,
            "feature_count": len(self.feature_names) if self.feature_names else 0,
        }

    def predict_single(self, features: dict[str, float]) -> dict[str, Any]:
        """Convenience wrapper for single-sample prediction."""
        df = pd.DataFrame([features])
        result = self.predict(df)
        return {
            "prediction": result["predictions"][0],
            "probabilities": result["probabilities"][0],
            "confidence": float(max(result["probabilities"][0])),
        }
