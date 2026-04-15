from __future__ import annotations

"""
Typed application configuration via Pydantic BaseSettings.

Engineering trade-off: Using BaseSettings over raw os.getenv() gives us:
  1. Type coercion at startup — fail fast if PORT is not parseable as int
  2. Frozen immutability — config cannot be mutated at runtime
  3. Single source of truth — no scattered getenv() calls across modules
  4. .env file support built-in via model_config

The cost is a Pydantic dependency (already required by FastAPI) and slightly
more ceremony than raw getenv(). For a project with 10+ config values, this
trade-off is unambiguously positive.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import json


class Settings(BaseSettings):
    """Immutable, typed application configuration."""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "frozen": True,
    }

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = True

    # --- API metadata ---
    API_PREFIX: str = "/api/v1"
    API_TITLE: str = "NASA Kepler Portal API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = (
        "NASA Kepler Objects Analysis Portal — "
        "Focused on Kepler Mission Data"
    )

    # --- CORS ---
    CORS_ORIGINS: str = '["http://localhost:3000", "https://nasa-space-site.vercel.app"]'
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: str = '["*"]'
    CORS_HEADERS: str = '["*"]'

    # --- File handling ---
    MAX_FILE_SIZE: int = 104_857_600  # 100 MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: str = '["csv", "xls", "xlsx"]'

    # --- Model ---
    MODEL_PATH: str = "models/simple_test_model.pkl"

    # --- Computed helpers (not env vars) ---

    @property
    def cors_origins_list(self) -> List[str]:
        try:
            return json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            return [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "https://nasa-space-site.vercel.app",
            ]

    @property
    def cors_methods_list(self) -> List[str]:
        try:
            return json.loads(self.CORS_METHODS)
        except (json.JSONDecodeError, TypeError):
            return ["*"]

    @property
    def cors_headers_list(self) -> List[str]:
        try:
            return json.loads(self.CORS_HEADERS)
        except (json.JSONDecodeError, TypeError):
            return ["*"]

    @property
    def allowed_extensions_list(self) -> List[str]:
        try:
            return json.loads(self.ALLOWED_EXTENSIONS)
        except (json.JSONDecodeError, TypeError):
            return ["csv", "xls", "xlsx"]


def get_settings() -> Settings:
    """
    Factory for Settings. Called once at startup.

    Not cached here — caching is the caller's responsibility (via
    FastAPI's Depends() or manual singleton). This keeps the function
    pure and testable: tests can call get_settings() with overridden
    env vars without fighting lru_cache.
    """
    return Settings()
