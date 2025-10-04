# KOI Model API Documentation

## Overview
API endpoints for Kepler Object of Interest (KOI) exoplanet classification using XGBoost model.

## Endpoints

### 1. Predict Dataset
**POST** `/api/koi/predict`

Upload a CSV file with KOI features and get predictions for all samples.

**Request:**
- Content-Type: `multipart/form-data`
- Body: CSV file with KOI features

**Response:**
```json
{
  "success": true,
  "message": "Successfully predicted 100 samples",
  "data": {
    "predictions": [
      {
        "index": 0,
        "prediction": "CONFIRMED",
        "prediction_code": 1,
        "confidence": 0.95,
        "probabilities": {
          "CANDIDATE": 0.02,
          "CONFIRMED": 0.95,
          "FALSE_POSITIVE": 0.03
        }
      }
    ],
    "total_samples": 100,
    "summary": {
      "CANDIDATE": 30,
      "CONFIRMED": 50,
      "FALSE_POSITIVE": 20
    }
  }
}
```

### 2. Predict Single Sample
**POST** `/api/koi/predict-single`

Make prediction for a single KOI object.

**Request:**
```json
{
  "features": {
    "koi_period": 9.488036,
    "koi_srad": 1.046,
    "koi_slogg": 4.467,
    "koi_prad": 2.26,
    "koi_teq": 1160.0,
    "koi_insol": 136.5
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Prediction successful",
  "data": {
    "index": 0,
    "prediction": "CONFIRMED",
    "prediction_code": 1,
    "confidence": 0.92,
    "probabilities": {
      "CANDIDATE": 0.05,
      "CONFIRMED": 0.92,
      "FALSE_POSITIVE": 0.03
    }
  }
}
```

### 3. Get Model Info
**GET** `/api/koi/model-info`

Get information about the loaded model.

**Response:**
```json
{
  "success": true,
  "model_type": "XGBoost Classifier",
  "classes": ["CANDIDATE", "CONFIRMED", "FALSE POSITIVE"],
  "required_features": ["koi_period", "koi_srad", "koi_slogg", ...],
  "description": "KOI disposition prediction model"
}
```

### 4. Validate Dataset
**POST** `/api/koi/validate-dataset`

Validate if a CSV file is suitable for prediction.

**Request:**
- Content-Type: `multipart/form-data`
- Body: CSV file to validate

**Response:**
```json
{
  "success": true,
  "valid": true,
  "total_columns": 50,
  "numeric_columns": 45,
  "total_rows": 1000,
  "missing_required_features": [],
  "sample_columns": ["kepid", "koi_period", "koi_srad", ...],
  "message": "Dataset is valid for prediction"
}
```

## Model Details

### Classes
- **CANDIDATE** (0): Potential exoplanet candidate
- **CONFIRMED** (1): Confirmed exoplanet
- **FALSE POSITIVE** (2): False positive detection

### Key Features
The model uses various KOI features including:
- `koi_period`: Orbital period (days)
- `koi_srad`: Stellar radius (solar radii)
- `koi_slogg`: Stellar surface gravity (log10(cm/s²))
- `koi_prad`: Planetary radius (Earth radii)
- `koi_teq`: Equilibrium temperature (K)
- `koi_insol`: Insolation flux (Earth flux)
- And many more...

### Feature Engineering
The model automatically creates derived features:
- Stellar density
- Planet to star radius ratio
- Semi-major axis to stellar radius ratio

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid file format, missing data, etc.)
- `500`: Server error (model loading failure, prediction error, etc.)

Error responses:
```json
{
  "detail": "Error message description"
}
```

## Usage Example

### cURL
```bash
# Predict dataset
curl -X POST "http://localhost:8000/api/koi/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@koi_dataset.csv"

# Predict single sample
curl -X POST "http://localhost:8000/api/koi/predict-single" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "koi_period": 9.488036,
      "koi_srad": 1.046,
      "koi_slogg": 4.467,
      "koi_prad": 2.26
    }
  }'

# Get model info
curl -X GET "http://localhost:8000/api/koi/model-info"

# Validate dataset
curl -X POST "http://localhost:8000/api/koi/validate-dataset" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_data.csv"
```

### Python
```python
import requests

# Predict dataset
with open('koi_dataset.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/koi/predict',
        files={'file': f}
    )
    predictions = response.json()

# Predict single sample
features = {
    "koi_period": 9.488036,
    "koi_srad": 1.046,
    "koi_slogg": 4.467,
    "koi_prad": 2.26
}
response = requests.post(
    'http://localhost:8000/api/koi/predict-single',
    json={'features': features}
)
result = response.json()
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure model file exists at `models/boost_test_model.json`

3. Run the server:
```bash
uvicorn main:app --reload --port 8000
```

4. Access API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
