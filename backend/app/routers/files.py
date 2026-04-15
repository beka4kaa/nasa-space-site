"""
File upload/download router.

Engineering trade-off: File operations are separated from prediction
endpoints because they have different auth, rate-limiting, and caching
requirements. Upload is a write path (creates files); download is a
read path (serves files). Mixing them with ML prediction in one router
violates the Interface Segregation Principle.
"""

import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.config import Settings
from app.core.exceptions import FileParseError, FileValidationError, PathTraversalError
from app.core.security import sanitize_filepath, validate_file_extension, validate_file_content
from app.dependencies import get_cached_settings
from app.schemas.schemas import UploadPreviewResponse
from app.services.file_parser import parse_upload

router = APIRouter(tags=["files"])


@router.post("/upload", response_model=UploadPreviewResponse)
async def upload_csv(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_cached_settings),
):
    """Upload a dataset file and return a preview of the first 100 rows."""
    try:
        validate_file_extension(file.filename, settings.allowed_extensions_list)
        content = await file.read()
        validate_file_content(content, settings.MAX_FILE_SIZE)
        df = parse_upload(content, file.filename)
    except (FileValidationError, FileParseError) as exc:
        raise HTTPException(status_code=400, detail=exc.detail)

    # Persist file for later download.
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)

    return UploadPreviewResponse(
        columns=list(df.columns),
        data=df.head(100).to_dict(orient="records"),
        filename=file.filename,
        total_rows=len(df),
        showing_rows=min(100, len(df)),
    )


@router.get("/download/{filename}")
def download_file(
    filename: str,
    settings: Settings = Depends(get_cached_settings),
):
    """
    Download a previously uploaded file.

    Security: The filename is sanitized to prevent path traversal (CWE-22).
    """
    try:
        safe_path = sanitize_filepath(filename, settings.UPLOAD_DIR)
    except PathTraversalError:
        raise HTTPException(status_code=403, detail="Access denied.")

    if not os.path.exists(safe_path):
        raise HTTPException(status_code=404, detail="File not found.")

    # Determine MIME type from extension.
    media_types = {
        ".csv": "text/csv",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
    }
    ext = os.path.splitext(filename)[1].lower()
    media_type = media_types.get(ext, "application/octet-stream")

    # Use a generator to ensure the file handle is properly closed.
    def _iter_file():
        with open(safe_path, "rb") as fh:
            yield from fh

    return StreamingResponse(
        _iter_file(),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
