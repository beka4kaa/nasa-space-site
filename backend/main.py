from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import os
import pandas as pd
import io
import chardet
from typing import Dict, Any, List
from pydantic import BaseModel
from model_utils_working import get_model, KOIModelPredictor
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configuration from environment
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8001"))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
API_TITLE = os.getenv("API_TITLE", "NASA Kepler Portal API")
API_VERSION = os.getenv("API_VERSION", "1.0.0")
API_DESCRIPTION = os.getenv("API_DESCRIPTION", "NASA Kepler Objects Analysis Portal - Focused on Kepler Mission Data")

# CORS settings
try:
    CORS_ORIGINS = json.loads(os.getenv("CORS_ORIGINS", '["http://localhost:3000"]'))
except:
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

# File settings
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "104857600"))  # 100MB
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
ALLOWED_EXTENSIONS = json.loads(os.getenv("ALLOWED_EXTENSIONS", '["csv", "xls", "xlsx"]'))

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    debug=DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=os.getenv("CORS_CREDENTIALS", "True").lower() == "true",
    allow_methods=json.loads(os.getenv("CORS_METHODS", '["*"]')),
    allow_headers=json.loads(os.getenv("CORS_HEADERS", '["*"]')),
)

# Global model instance for better performance
model_predictor = None

def get_predictor():
    global model_predictor
    if model_predictor is None:
        model_predictor = get_model()
    return model_predictor

# Pydantic models
class PredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    success: bool
    predictions: List[str]
    probabilities: List[List[float]]
    summary: Dict[str, Any]
    total: int
    model_metadata: Dict[str, Any]

class ValidationResponse(BaseModel):
    success: bool
    valid: bool
    message: str
    total_rows: int
    total_columns: int
    sample_columns: List[str]

# ============= BASIC ENDPOINTS =============

@app.get("/ping")
def ping():
    """Health check endpoint"""
    return {"status": "ok", "message": "NASA Kepler Portal API is running"}

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "endpoints": {
            "health": "/ping",
            "upload": "/upload",
            "download": "/download/{filename}",
            "predict": "/api/kepler/predict",
            "predict_single": "/api/kepler/predict-single",
            "validate": "/api/kepler/validate-dataset",
            "model_info": "/api/kepler/model-info"
        }
    }

# ============= FILE OPERATIONS =============

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload and preview dataset"""
    if not any(file.filename.endswith(f'.{ext}') for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400, 
            detail=f"Only {', '.join(ALLOWED_EXTENSIONS).upper()} files are allowed."
        )
    
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    
    try:
        # Read file based on extension
        if file.filename.endswith('.csv'):
            detected = chardet.detect(content)
            encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
            df = pd.read_csv(io.BytesIO(content), encoding=encoding)
        else:  # Excel files
            try:
                df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
            except:
                df = pd.read_excel(io.BytesIO(content), engine='xlrd')
        
        # Save file for later use
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Return preview
        return {
            "columns": list(df.columns),
            "data": df.head(100).to_dict(orient="records"),
            "filename": file.filename,
            "total_rows": len(df),
            "showing_rows": min(100, len(df))
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

@app.get("/download/{filename}")
def download_file(filename: str):
    """Download previously uploaded file"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    # Determine media type
    if filename.endswith('.csv'):
        media_type = "text/csv"
    elif filename.endswith('.xlsx'):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif filename.endswith('.xls'):
        media_type = "application/vnd.ms-excel"
    else:
        media_type = "application/octet-stream"
    
    return StreamingResponse(
        open(file_path, "rb"), 
        media_type=media_type, 
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ============= KEPLER MODEL ENDPOINTS =============

@app.post("/api/kepler/validate-dataset")
async def validate_dataset(file: UploadFile = File(...)):
    """Validate dataset for Kepler model prediction"""
    try:
        content = await file.read()
        
        # Detect file format based on content, not extension
        try:
            # Try CSV first (most common and faster)
            detected = chardet.detect(content)
            encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
            df = pd.read_csv(io.BytesIO(content), encoding=encoding)
        except:
            # If CSV fails, try Excel
            try:
                df = pd.read_excel(io.BytesIO(content))
            except:
                # Try Excel with different engines
                try:
                    df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
                except:
                    df = pd.read_excel(io.BytesIO(content), engine='xlrd')
        
        # Get model and check required features
        predictor = get_predictor()
        required_features = predictor.feature_names
        
        missing_features = [f for f in required_features if f not in df.columns]
        
        if missing_features:
            return ValidationResponse(
                success=False,
                valid=False,
                message=f"Missing required columns: {missing_features}",
                total_rows=len(df),
                total_columns=len(df.columns),
                sample_columns=list(df.columns)[:10]
            )
        
        return ValidationResponse(
            success=True,
            valid=True,
            message="Dataset is valid for prediction",
            total_rows=len(df),
            total_columns=len(df.columns),
            sample_columns=list(df.columns)[:10]
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")

@app.post("/api/kepler/predict", response_model=PredictionResponse)
async def predict_dataset(file: UploadFile = File(...)):
    """Run Kepler model predictions on uploaded dataset"""
    try:
        content = await file.read()
        
        # Detect file format based on content, not extension
        try:
            # Try CSV first (most common and faster)
            detected = chardet.detect(content)
            encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
            df = pd.read_csv(io.BytesIO(content), encoding=encoding)
        except:
            # If CSV fails, try Excel
            try:
                df = pd.read_excel(io.BytesIO(content))
            except:
                # Try Excel with different engines
                try:
                    df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
                except:
                    df = pd.read_excel(io.BytesIO(content), engine='xlrd')
        
        # Get predictions
        predictor = get_predictor()
        result = predictor.predict(df)
        
        # Calculate summary statistics
        predictions = result['predictions']
        summary = {
            prediction_type: predictions.count(prediction_type) 
            for prediction_type in set(predictions)
        }
        
        return PredictionResponse(
            success=True,
            predictions=predictions,
            probabilities=result.get('probabilities', []),
            summary=summary,
            total=len(predictions),
            model_metadata={
                "accuracy": getattr(predictor, 'accuracy', 0.91),
                "model_type": "Kepler Mission Analysis",
                "features_count": len(predictor.feature_names)
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

class SinglePredictionRequest(BaseModel):
    features: Dict[str, float]

@app.post("/api/kepler/predict-single")
def predict_single(request: SinglePredictionRequest):
    """Make a single prediction with provided features"""
    try:
        predictor = get_predictor()
        
        # Convert features dict to DataFrame
        df = pd.DataFrame([request.features])
        
        # Make prediction
        result = predictor.predict(df)
        
        prediction = result['predictions'][0]
        probabilities = result['probabilities'][0] if result.get('probabilities') else []
        
        return {
            "success": True,
            "prediction": prediction,
            "probabilities": probabilities,
            "confidence": max(probabilities) if probabilities else 0.0,
            "features_used": len(request.features),
            "model_metadata": {
                "accuracy": getattr(predictor, 'accuracy', 0.91),
                "model_type": "Kepler Mission Analysis"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/api/kepler/model-info")
def get_model_info():
    """Get information about the Kepler model"""
    try:
        predictor = get_predictor()
        return {
            "model_type": "Kepler Mission Analysis Model",
            "accuracy": getattr(predictor, 'accuracy', 0.91),
            "features": predictor.feature_names,
            "feature_count": len(predictor.feature_names),
            "prediction_classes": ["CONFIRMED", "CANDIDATE", "FALSE POSITIVE"],
            "description": "Machine learning model trained on NASA Kepler mission data for exoplanet classification",
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")

# ============= STARTUP =============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, reload=DEBUG)