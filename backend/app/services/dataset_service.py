from __future__ import annotations

"""
Dataset service — handles sample dataset retrieval.

Separated from prediction_service because dataset serving is a
read-only, IO-bound operation with different caching and error
characteristics than ML inference.
"""

import io
import os

import pandas as pd
from fastapi.responses import StreamingResponse

from app.core.exceptions import AppError


def get_sample_dataset_response(datasets_dir: str) -> StreamingResponse:
    """
    Build a StreamingResponse for the sample Kepler dataset.

    Looks for the full dataset first (NewKepler_full.xls, which is
    actually CSV despite the .xls extension), then falls back to koi.csv.

    Raises AppError if no dataset file is found.
    """
    full_path = os.path.join(datasets_dir, "NewKepler_full.xls")
    fallback_path = os.path.join(datasets_dir, "koi.csv")

    if os.path.exists(full_path):
        # NewKepler_full.xls is actually CSV content with a .xls extension.
        df = pd.read_csv(full_path)
        filename = "kepler_full_dataset.csv"
        description = "NASA Kepler Objects of Interest Complete Dataset"
    elif os.path.exists(fallback_path):
        df = pd.read_csv(fallback_path, comment="#")
        df = df.head(100)
        filename = "kepler_sample_dataset.csv"
        description = "NASA Kepler Objects of Interest Sample Dataset"
    else:
        raise AppError("Dataset files not found on server.")

    csv_content = df.to_csv(index=False)
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Description": description,
        },
    )
