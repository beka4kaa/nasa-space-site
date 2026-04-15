"""
Entry point for local development.

Usage: python app.py
Production: uvicorn app.main:app --host 0.0.0.0 --port $PORT
"""

import uvicorn
from app.config import get_settings


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )