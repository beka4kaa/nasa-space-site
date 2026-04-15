"""
Health and metadata endpoints.

These are intentionally thin — no business logic, just status reporting.
"""

from fastapi import APIRouter, Depends
from app.config import Settings
from app.dependencies import get_cached_settings
from app.schemas.schemas import HealthResponse, ApiInfoResponse

router = APIRouter(tags=["health"])


@router.get("/ping", response_model=HealthResponse)
def ping():
    """Liveness probe for load balancers and monitoring."""
    return HealthResponse(
        status="ok",
        message="NASA Kepler Portal API is running",
    )


@router.get("/", response_model=ApiInfoResponse)
def root(settings: Settings = Depends(get_cached_settings)):
    """Root endpoint with API information and endpoint directory."""
    return ApiInfoResponse(
        name=settings.API_TITLE,
        version=settings.API_VERSION,
        description=settings.API_DESCRIPTION,
        endpoints={
            "health": "/ping",
            "upload": "/upload",
            "download": "/download/{filename}",
            "predict": "/api/kepler/predict",
            "predict_paginated": "/api/kepler/predict-paginated",
            "predict_single": "/api/kepler/predict-single",
            "validate": "/api/kepler/validate-dataset",
            "model_info": "/api/kepler/info",
            "sample_dataset": "/api/kepler/dataset/sample",
        },
    )
