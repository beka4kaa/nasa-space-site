"""
Application factory.

Engineering trade-off: Using a create_app() factory instead of a
module-level `app = FastAPI()` singleton. This enables:
  1. Test isolation — each test can create a fresh app with overridden deps
  2. Configuration injection — different configs for dev/staging/prod
  3. Clean startup — model loads in a lifespan handler, not on import

The cost is one extra function call. The benefit is a testable,
configurable application that follows The Twelve-Factor App methodology.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.dependencies import get_predictor, get_cached_settings
from app.routers import health, files, kepler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup/shutdown lifecycle handler.

    Loads the ML model eagerly at startup rather than lazily on first
    request. This means:
      - The first request isn't penalized with model load latency
      - Deployment health checks fail fast if the model file is missing
      - Memory usage is predictable from startup
    """
    settings = get_cached_settings()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Eagerly load model — fail fast if model file is missing.
    get_predictor(settings)

    yield  # Application runs here.

    # Shutdown: nothing to clean up (model is in-memory, GC handles it).


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_cached_settings()

    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description=settings.API_DESCRIPTION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # CORS middleware.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.cors_methods_list,
        allow_headers=settings.cors_headers_list,
    )

    # Register routers.
    app.include_router(health.router)
    app.include_router(files.router)
    app.include_router(kepler.router)

    return app


# Module-level app instance for uvicorn: `uvicorn app.main:app`
app = create_app()
