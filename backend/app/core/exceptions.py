from __future__ import annotations

"""
Domain exception hierarchy.

Engineering trade-off: A custom exception hierarchy instead of raising
HTTPException from service/model layers. This decouples business logic
from the HTTP transport — services raise domain errors, and the router
layer (or a global exception handler) maps them to HTTP status codes.

Without this, service code becomes tightly coupled to FastAPI's exception
model, making it impossible to reuse services in CLI tools, background
workers, or tests without importing fastapi.
"""


class AppError(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str, *, detail: str | None = None):
        self.message = message
        self.detail = detail or message
        super().__init__(self.message)


class FileParseError(AppError):
    """Raised when an uploaded file cannot be parsed into a DataFrame."""
    pass


class FileValidationError(AppError):
    """Raised when an uploaded file fails validation (wrong extension, empty, too large)."""
    pass


class DatasetValidationError(AppError):
    """Raised when a parsed DataFrame is missing required columns or is empty."""

    def __init__(
        self,
        message: str,
        *,
        missing_features: list[str] | None = None,
        available_features: list[str] | None = None,
    ):
        super().__init__(message)
        self.missing_features = missing_features or []
        self.available_features = available_features or []


class ModelError(AppError):
    """Raised when the ML model fails to load or predict."""
    pass


class PathTraversalError(AppError):
    """Raised when a filename resolves outside the allowed directory."""
    pass
