"""
Kepler prediction router.

Each handler follows the same pattern:
  1. Extract HTTP-specific inputs (UploadFile, query params)
  2. Delegate to PredictionService (domain logic)
  3. Map domain results/exceptions to HTTP responses

This keeps route handlers at ~10 lines — all business logic lives
in the service layer where it can be unit-tested without HTTP.
"""

import os

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from app.config import Settings
from app.core.exceptions import (
    AppError,
    DatasetValidationError,
    FileParseError,
    FileValidationError,
    ModelError,
)
from app.dependencies import get_cached_settings, get_prediction_service
from app.schemas.schemas import (
    ModelInfoResponse,
    PaginatedPredictionResponse,
    PredictionResponse,
    SinglePredictionRequest,
    SinglePredictionResponse,
    ValidationResponse,
)
from app.services.dataset_service import get_sample_dataset_response
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/api/kepler", tags=["kepler"])


# ── Validation ───────────────────────────────────────────────────────────


@router.post("/validate-dataset", response_model=ValidationResponse)
async def validate_dataset(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_cached_settings),
    service: PredictionService = Depends(get_prediction_service),
):
    """Validate whether an uploaded dataset has the required KOI columns."""
    try:
        content = await file.read()
        result = service.validate_dataset(
            content=content,
            filename=file.filename,
            allowed_extensions=settings.allowed_extensions_list,
            max_file_size=settings.MAX_FILE_SIZE,
        )
    except (FileValidationError, FileParseError) as exc:
        raise HTTPException(status_code=400, detail=exc.detail)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Validation failed: {exc}",
        )

    return ValidationResponse(
        success=result["valid"],
        valid=result["valid"],
        message=result["message"],
        total_rows=result["total_rows"],
        total_columns=result["total_columns"],
        sample_columns=result["sample_columns"],
    )


# ── Batch Prediction ─────────────────────────────────────────────────────


@router.post("/predict", response_model=PredictionResponse)
async def predict_dataset(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_cached_settings),
    service: PredictionService = Depends(get_prediction_service),
):
    """Run KOI classification on an uploaded dataset."""
    try:
        content = await file.read()
        result = service.predict_batch(
            content=content,
            filename=file.filename,
            allowed_extensions=settings.allowed_extensions_list,
            max_file_size=settings.MAX_FILE_SIZE,
        )
    except (FileValidationError, FileParseError, DatasetValidationError) as exc:
        raise HTTPException(status_code=400, detail=exc.detail)
    except ModelError as exc:
        raise HTTPException(status_code=500, detail=exc.detail)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    return PredictionResponse(success=True, **result)


# ── Paginated Prediction ────────────────────────────────────────────────


@router.post("/predict-paginated", response_model=PaginatedPredictionResponse)
async def predict_dataset_paginated(
    file: UploadFile = File(...),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=1000, description="Results per page"),
    settings: Settings = Depends(get_cached_settings),
    service: PredictionService = Depends(get_prediction_service),
):
    """Run KOI classification with paginated results."""
    try:
        content = await file.read()
        result = service.predict_batch_paginated(
            content=content,
            filename=file.filename,
            allowed_extensions=settings.allowed_extensions_list,
            max_file_size=settings.MAX_FILE_SIZE,
            page=page,
            page_size=page_size,
        )
    except (FileValidationError, FileParseError, DatasetValidationError) as exc:
        raise HTTPException(status_code=400, detail=exc.detail)
    except ModelError as exc:
        raise HTTPException(status_code=500, detail=exc.detail)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    return PaginatedPredictionResponse(success=True, **result)


# ── Single Prediction ───────────────────────────────────────────────────


@router.post("/predict-single", response_model=SinglePredictionResponse)
def predict_single(
    request: SinglePredictionRequest,
    service: PredictionService = Depends(get_prediction_service),
):
    """Predict classification for a single KOI from JSON features."""
    try:
        result = service.predict_single(request.features)
    except ModelError as exc:
        raise HTTPException(status_code=500, detail=exc.detail)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    return SinglePredictionResponse(success=True, **result)


# ── Model Info ───────────────────────────────────────────────────────────


@router.get("/info", response_model=ModelInfoResponse)
def get_model_info(
    service: PredictionService = Depends(get_prediction_service),
):
    """Return metadata about the loaded classification model."""
    try:
        info = service.get_model_info()
    except ModelError as exc:
        raise HTTPException(status_code=500, detail=exc.detail)

    return ModelInfoResponse(success=True, model_info=info)


# ── Sample Dataset ───────────────────────────────────────────────────────


@router.get("/dataset/sample")
def download_sample_dataset():
    """Download the Kepler sample/full dataset as CSV."""
    datasets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "datasets")
    try:
        return get_sample_dataset_response(datasets_dir)
    except AppError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download dataset: {exc}",
        )
