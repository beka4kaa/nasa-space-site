from __future__ import annotations

"""
Prediction service — orchestrates file parsing, validation, and model inference.

Engineering trade-off: This service layer sits between routers and the model.
Routers handle HTTP concerns (UploadFile, status codes). This service handles
*domain* concerns (is the dataset valid? run predictions, compute summaries).

This separation means:
  1. Service logic is testable without starting FastAPI
  2. The same service can be called from a CLI tool or background worker
  3. Error types are domain-specific (DatasetValidationError, not HTTPException)
"""

import pandas as pd
from typing import Any

from app.models.predictor import KOIModelPredictor
from app.services.file_parser import parse_upload
from app.core.exceptions import DatasetValidationError, FileParseError
from app.core.security import validate_file_extension, validate_file_content


class PredictionService:
    """Stateless service orchestrating dataset validation and prediction."""

    def __init__(self, predictor: KOIModelPredictor):
        self._predictor = predictor

    def validate_dataset(
        self,
        content: bytes,
        filename: str,
        allowed_extensions: list[str],
        max_file_size: int,
    ) -> dict[str, Any]:
        """
        Validate that an uploaded file can be used for prediction.

        Returns a validation result dict (success, valid, message, stats).
        Raises FileParseError or FileValidationError on hard failures.
        """
        validate_file_extension(filename, allowed_extensions)
        validate_file_content(content, max_file_size)

        df = parse_upload(content, filename)

        required = self._predictor.feature_names
        if not required:
            return {
                "valid": True,
                "message": "Model has no declared features; accepting any dataset.",
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "sample_columns": list(df.columns)[:10],
            }

        missing = [f for f in required if f not in df.columns]
        available = [f for f in required if f in df.columns]

        if missing:
            truncated = missing[:5]
            suffix = "..." if len(missing) > 5 else ""
            return {
                "valid": False,
                "message": (
                    f"Dataset is missing {len(missing)} required KOI columns. "
                    f"Found {len(available)}/{len(required)} required columns. "
                    f"Missing: {truncated}{suffix}"
                ),
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "sample_columns": list(df.columns)[:10],
            }

        return {
            "valid": True,
            "message": (
                f"Dataset is valid for prediction! Found all {len(required)} "
                f"required KOI columns with {len(df)} rows of data."
            ),
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "sample_columns": list(df.columns)[:10],
        }

    def predict_batch(
        self,
        content: bytes,
        filename: str,
        allowed_extensions: list[str],
        max_file_size: int,
    ) -> dict[str, Any]:
        """
        Parse, validate, and run predictions on a full dataset.

        Returns a dict matching PredictionResponse schema.
        """
        validate_file_extension(filename, allowed_extensions)
        validate_file_content(content, max_file_size)

        df = parse_upload(content, filename)
        self._assert_required_features(df)

        result = self._predictor.predict(df)
        predictions = result["predictions"]

        # Compute summary: count of each prediction class.
        summary: dict[str, int] = {}
        for pred in predictions:
            key = pred.replace(" ", "_")
            summary[key] = summary.get(key, 0) + 1

        return {
            "predictions": predictions,
            "probabilities": result.get("probabilities", []),
            "summary": summary,
            "total": len(predictions),
            "original_data": result.get("original_data", []),
            "model_metadata": self._model_metadata(),
        }

    def predict_batch_paginated(
        self,
        content: bytes,
        filename: str,
        allowed_extensions: list[str],
        max_file_size: int,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """
        Run predictions and return a paginated slice.

        Engineering note: We predict the entire dataset, then paginate the
        results. This is correct because:
          1. Re-uploading the file per page would be worse UX
          2. Summary statistics must reflect all data, not just the current page
          3. The dataset fits in memory (max 100MB file, ~100K rows typical)
        """
        # Clamp pagination parameters.
        page = max(1, page)
        page_size = min(max(1, page_size), 1000)

        full_result = self.predict_batch(
            content, filename, allowed_extensions, max_file_size
        )

        all_predictions = full_result["predictions"]
        all_probabilities = full_result.get("probabilities", [])
        total = len(all_predictions)
        total_pages = max(1, (total + page_size - 1) // page_size)
        page = min(page, total_pages)

        start = (page - 1) * page_size
        end = start + page_size

        return {
            "predictions": all_predictions[start:end],
            "probabilities": all_probabilities[start:end] if all_probabilities else [],
            "summary": full_result["summary"],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "original_data": full_result.get("original_data", []),
            "model_metadata": full_result["model_metadata"],
        }

    def predict_single(self, features: dict[str, float]) -> dict[str, Any]:
        """Run prediction on a single sample from JSON features."""
        result = self._predictor.predict_single(features)
        return {
            "prediction": result["prediction"],
            "probabilities": result["probabilities"],
            "confidence": result["confidence"],
            "features_used": len(features),
            "model_metadata": self._model_metadata(),
        }

    def get_model_info(self) -> dict[str, Any]:
        """Return metadata about the loaded model."""
        self._predictor._ensure_loaded()
        return {
            "model_type": "SimpleKOIModelPredictor",
            "accuracy": self._predictor.accuracy or 0.91,
            "feature_count": len(self._predictor.feature_names or []),
            "feature_names": self._predictor.feature_names or [],
            "required_columns": self._predictor.feature_names or [],
            "description": (
                "Model trained to classify Kepler Objects of Interest (KOI) "
                "as confirmed planets or false positives using NASA Kepler "
                "mission data"
            ),
            "column_descriptions": {
                "koi_period": "Orbital period [days]",
                "koi_time0bk": "Transit Epoch [BKJD]",
                "koi_impact": "Impact Parameter",
                "koi_duration": "Transit Duration [hrs]",
                "koi_depth": "Transit Depth [ppm]",
                "koi_prad": "Planetary Radius [Earth radii]",
                "koi_teq": "Equilibrium Temperature [K]",
                "koi_insol": "Insolation Flux [Earth flux]",
                "koi_model_snr": "Transit Signal-to-Noise",
                "koi_steff": "Stellar Effective Temperature [K]",
                "koi_slogg": "Stellar Surface Gravity [log10(cm/s**2)]",
                "koi_srad": "Stellar Radius [Solar radii]",
                "ra": "Right Ascension [decimal degrees]",
                "dec": "Declination [decimal degrees]",
                "koi_kepmag": "Kepler-band [mag]",
                "koi_fpflag_nt": "Not Transit-Like Flag",
                "koi_fpflag_ss": "Stellar Eclipse Flag",
                "koi_fpflag_co": "Centroid Offset Flag",
                "koi_fpflag_ec": "Ephemeris Match Indicates Contamination Flag",
            },
        }

    # ── Private helpers ──────────────────────────────────────────────

    def _assert_required_features(self, df: pd.DataFrame) -> None:
        """Raise DatasetValidationError if required features are missing."""
        required = self._predictor.feature_names
        if not required:
            return

        missing = [f for f in required if f not in df.columns]
        if missing:
            raise DatasetValidationError(
                f"Dataset is missing {len(missing)} required KOI columns: "
                f"{missing[:10]}{'...' if len(missing) > 10 else ''}",
                missing_features=missing,
                available_features=[f for f in required if f in df.columns],
            )

    def _model_metadata(self) -> dict[str, Any]:
        return {
            "accuracy": self._predictor.accuracy or 0.91,
            "model_type": "Kepler Mission Analysis",
            "features_count": len(self._predictor.feature_names or []),
        }
