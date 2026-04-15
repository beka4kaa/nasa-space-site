from __future__ import annotations

"""
Security utilities — file path sanitization and upload validation.

Engineering trade-off: Centralizing security checks in a dedicated module
rather than inlining them in route handlers. This ensures every code path
that touches user-supplied filenames goes through the same guard — a
defense-in-depth measure against path traversal (CWE-22).
"""

import os
from app.core.exceptions import PathTraversalError, FileValidationError


def sanitize_filepath(filename: str, base_dir: str) -> str:
    """
    Resolve an absolute path for *filename* within *base_dir* and verify
    that the result does not escape the base directory.

    Raises PathTraversalError if the resolved path is outside base_dir.

    Why os.path.realpath: It resolves symlinks and normalizes '..'.
    os.path.abspath alone would not resolve symlinks — an attacker could
    create a symlink inside uploads/ pointing to /etc/passwd. realpath
    follows the link and catches the escape.
    """
    resolved = os.path.realpath(os.path.join(base_dir, filename))
    base_resolved = os.path.realpath(base_dir)

    if not resolved.startswith(base_resolved + os.sep) and resolved != base_resolved:
        raise PathTraversalError(
            f"Path traversal detected: '{filename}' resolves outside upload directory"
        )
    return resolved


def validate_file_extension(filename: str | None, allowed_extensions: list[str]) -> str:
    """
    Validate that a filename has an allowed extension.

    Returns the lowercase extension (without dot) on success.
    Raises FileValidationError on failure.
    """
    if not filename:
        raise FileValidationError("Filename is missing or empty")

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in allowed_extensions:
        allowed = ", ".join(ext.upper() for ext in allowed_extensions)
        raise FileValidationError(
            f"Invalid file format. Only {allowed} files are allowed."
        )
    return ext


def validate_file_content(content: bytes, max_size: int) -> None:
    """
    Validate uploaded file content is non-empty and within size limits.

    Raises FileValidationError on failure.
    """
    if not content:
        raise FileValidationError(
            "Uploaded file is empty. Please upload a valid file with data."
        )
    if len(content) > max_size:
        size_mb = max_size / (1024 * 1024)
        raise FileValidationError(
            f"File size exceeds {size_mb:.0f}MB limit."
        )
