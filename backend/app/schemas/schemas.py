from __future__ import annotations

"""
Pydantic response and request schemas.

Engineering trade-off: Strict schemas at the boundary enforce a contract
between frontend and backend. The original code had PredictionResponse
silently dropping original_data because the schema didn't declare it.
By making the schema explicit and complete, we guarantee the frontend
receives exactly what it expects — no more, no less.

We use model_config = {"protected_namespaces": ()} to avoid Pydantic v2
warnings on fields prefixed with 'model_'.
"""

from pydantic import BaseModel, Field
from typing import Any


# ── Responses ────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    message: str


class ApiInfoResponse(BaseModel):
    name: str
    version: str
    description: str
    endpoints: dict[str, str]


class UploadPreviewResponse(BaseModel):
    columns: list[str]
    data: list[dict[str, Any]]
    filename: str
    total_rows: int
    showing_rows: int


class ValidationResponse(BaseModel):
    success: bool
    valid: bool
    message: str
    total_rows: int
    total_columns: int
    sample_columns: list[str]


class PredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    success: bool
    predictions: list[str]
    probabilities: list[list[float]]
    summary: dict[str, int]
    total: int
    model_metadata: dict[str, Any]
    # Fix: original_data was silently dropped in the old schema,
    # breaking all frontend analytics charts that depend on it.
    original_data: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Selected columns from the input data for analytics visualizations",
    )


class PaginatedPredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    success: bool
    predictions: list[str]
    probabilities: list[list[float]]
    summary: dict[str, int]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    model_metadata: dict[str, Any]
    original_data: list[dict[str, Any]] = Field(default_factory=list)


class SinglePredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    success: bool
    prediction: str
    probabilities: list[float]
    confidence: float
    features_used: int
    model_metadata: dict[str, Any]


class ModelInfoResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    success: bool
    model_info: dict[str, Any]


# ── Requests ─────────────────────────────────────────────────────────────

class SinglePredictionRequest(BaseModel):
    """Request body for single-sample prediction."""
    features: dict[str, float] = Field(
        ...,
        description="Dictionary mapping feature names to float values",
        min_length=1,
    )
