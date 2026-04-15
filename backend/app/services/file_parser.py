from __future__ import annotations

"""
Unified file parsing service.

Engineering trade-off: This module exists *solely* to eliminate the 4×
copy-pasted file-parsing block that was in the original main.py. The
parsing strategy (CSV-first → Excel fallback) is now defined once.

The cascade order matters:
  1. CSV with comment='#'  — handles NASA data files that have comment headers
  2. CSV without comment   — handles malformed CSV where '#' is data
  3. openpyxl (.xlsx)      — modern Excel
  4. xlrd (.xls)           — legacy Excel

We try CSV first regardless of extension because NASA distributes .xls
files that are actually CSV (observed in datasets/NewKepler_full.xls).
"""

import io
import chardet
import pandas as pd
from app.core.exceptions import FileParseError


def parse_upload(content: bytes, filename: str) -> pd.DataFrame:
    """
    Parse raw file bytes into a pandas DataFrame.

    Attempts multiple parsing strategies in priority order.
    Raises FileParseError with aggregated error context on failure.

    Parameters
    ----------
    content : bytes
        Raw file content (already read from UploadFile).
    filename : str
        Original filename — used only for logging context, NOT for
        format detection (since NASA ships CSV as .xls).

    Returns
    -------
    pd.DataFrame
        Parsed, non-empty DataFrame.
    """
    errors: list[str] = []

    # Step 1: Detect encoding for text-based formats.
    detected = chardet.detect(content)
    encoding = detected.get("encoding") or "utf-8"

    # Step 2: Try CSV parsing first (works for most NASA data regardless of extension).
    df = _try_csv(content, encoding, errors)

    # Step 3: If CSV failed, try Excel engines.
    if df is None:
        df = _try_excel(content, errors)

    # Step 4: All strategies exhausted.
    if df is None:
        detail = "; ".join(errors[:3]) if errors else "Unknown parsing error"
        raise FileParseError(
            "Invalid file format. Please ensure the file (CSV/XLS/XLSX) is "
            "properly formatted and contains the required KOI columns.",
            detail=detail,
        )

    if df.empty:
        raise FileParseError(
            "The uploaded file is empty or contains no data rows."
        )

    return df


def _try_csv(content: bytes, encoding: str, errors: list[str]) -> pd.DataFrame | None:
    """Attempt CSV parsing with and without NASA comment-line handling."""
    # Attempt 1: CSV with comment='#' (NASA files have #-prefixed headers)
    try:
        df = pd.read_csv(io.BytesIO(content), encoding=encoding, comment="#")
        if not df.empty:
            return df
    except Exception as exc:
        errors.append(f"CSV (comment=#): {exc}")

    # Attempt 2: Plain CSV without comment handling
    try:
        df = pd.read_csv(io.BytesIO(content), encoding=encoding)
        if not df.empty:
            return df
    except Exception as exc:
        errors.append(f"CSV (plain): {exc}")

    return None


def _try_excel(content: bytes, errors: list[str]) -> pd.DataFrame | None:
    """Attempt Excel parsing with multiple engines."""
    for engine in ("openpyxl", "xlrd"):
        try:
            df = pd.read_excel(io.BytesIO(content), engine=engine)
            if not df.empty:
                return df
        except Exception as exc:
            errors.append(f"Excel ({engine}): {exc}")
    return None
