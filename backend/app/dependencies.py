"""
FastAPI dependency injection providers.

Engineering trade-off: Using Depends() for the predictor and service
instead of module-level globals. This gives us:
  1. Testability — tests can override dependencies via app.dependency_overrides
  2. Explicit lifecycle — the predictor loads once and is reused
  3. No import-time side effects — the model doesn't load when you import a module

The predictor is cached in a module-level variable BUT is only accessed
via get_predictor(), which FastAPI's dependency system manages. This is
the idiomatic FastAPI pattern for expensive-to-create resources.
"""

import os
from functools import lru_cache
from typing import Optional

from app.config import Settings, get_settings
from app.models.predictor import KOIModelPredictor
from app.services.prediction_service import PredictionService


@lru_cache()
def get_cached_settings() -> Settings:
    """
    Cached settings singleton for use as a FastAPI dependency.

    Using lru_cache here (not on get_settings itself) keeps the
    factory pure for testing while giving FastAPI a single instance.
    """
    return get_settings()


# Module-level predictor — loaded once on first access.
_predictor: Optional[KOIModelPredictor] = None


def get_predictor(settings: Optional[Settings] = None) -> KOIModelPredictor:
    """
    Get or create the global KOIModelPredictor instance.

    Thread safety: In production with uvicorn's async event loop, Python's
    GIL ensures the None-check + assignment is atomic for single-process
    deployments. For multi-worker (gunicorn), each worker gets its own copy
    which is correct behavior (no shared mutable state).
    """
    global _predictor
    if _predictor is None:
        if settings is None:
            settings = get_cached_settings()
        _predictor = KOIModelPredictor(model_path=settings.MODEL_PATH)
        _predictor.load_model()
    return _predictor


def get_prediction_service(settings: Optional[Settings] = None) -> PredictionService:
    """Build a PredictionService with the singleton predictor."""
    predictor = get_predictor(settings)
    return PredictionService(predictor)

