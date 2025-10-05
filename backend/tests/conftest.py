"""
Test configuration and fixtures for KOI model tests
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import model_utils_working

@pytest.fixture
def sample_koi_data():
    """Sample KOI data for testing"""
    return pd.DataFrame({
        'kepid': [10666592, 10666593, 10666594],
        'koi_disposition': [1, 2, 0],  # CANDIDATE, CONFIRMED, FALSE POSITIVE
        'koi_period': [9.488036, 54.418383, 123.456],
        'koi_time0bk': [170.538750, 162.513840, 180.123],
        'koi_impact': [0.146, 0.586, 0.234],
        'koi_duration': [2.95750, 4.50700, 3.456],
        'koi_depth': [874.8, 492.3, 1200.5],
        'koi_prad': [2.26, 1.89, 3.45],
        'koi_teq': [1160.0, 797.0, 650.0],
        'koi_insol': [136.5, 17.9, 8.2],
        'koi_model_snr': [35.8, 28.4, 15.6],
        'koi_steff': [5450, 5800, 6100],
        'koi_slogg': [4.38, 4.45, 4.12],
        'koi_srad': [1.02, 0.98, 1.15],
        'ra': [291.93423, 292.12345, 290.87654],
        'dec': [48.14808, 47.98765, 48.34567],
        'koi_kepmag': [14.731, 13.456, 15.234],
        'koi_fpflag_nt': [0, 0, 1],
        'koi_fpflag_ss': [0, 0, 1],
        'koi_fpflag_co': [0, 0, 1],
        'koi_fpflag_ec': [0, 0, 0]
    })

@pytest.fixture
def real_koi_data():
    """Load real KOI dataset"""
    data_path = backend_dir / 'uploads' / 'NewKepler (8) (1).xls'
    if data_path.exists():
        return pd.read_csv(data_path)
    else:
        pytest.skip("Real KOI dataset not found")

@pytest.fixture
def koi_model():
    """KOI model instance"""
    return model_utils_working.get_model()

@pytest.fixture
def expected_classes():
    """Expected classification classes"""
    return ['CANDIDATE', 'CONFIRMED', 'FALSE POSITIVE']

@pytest.fixture
def label_mapping():
    """Label mapping for KOI dispositions"""
    return {0: 'FALSE POSITIVE', 1: 'CANDIDATE', 2: 'CONFIRMED'}