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
    CORS_ORIGINS = json.loads(os.getenv("CORS_ORIGINS", '["http://localhost:3000", "https://nasa-space-site.vercel.app"]'))
except:
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000", "https://nasa-space-site.vercel.app"]

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
        # Check file extension first
        if not any(file.filename.lower().endswith(f'.{ext}') for ext in ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file format. Please ensure the file (CSV/XLS/XLSX) is properly formatted and contains the required KOI columns."
            )
        
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty. Please upload a valid CSV/XLS/XLSX file with KOI data."
            )
        
        # Try to read file with multiple approaches
        df = None
        file_errors = []
        
        # Try CSV first (most common and faster)
        if file.filename.lower().endswith('.csv'):
            try:
                detected = chardet.detect(content)
                encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
                df = pd.read_csv(io.BytesIO(content), encoding=encoding)
            except Exception as e:
                file_errors.append(f"CSV parsing error: {str(e)}")
        
        # Try Excel formats
        if df is None and (file.filename.lower().endswith('.xlsx') or file.filename.lower().endswith('.xls')):
            # Try different Excel engines
            engines = ['openpyxl', 'xlrd'] if file.filename.lower().endswith('.xlsx') else ['xlrd', 'openpyxl']
            
            for engine in engines:
                try:
                    df = pd.read_excel(io.BytesIO(content), engine=engine)
                    break
                except Exception as e:
                    file_errors.append(f"Excel parsing error ({engine}): {str(e)}")
        
        # If all parsing attempts failed
        if df is None:
            error_msg = "Invalid file format. Please ensure the file (CSV/XLS/XLSX) is properly formatted and contains the required KOI columns."
            if file_errors:
                error_msg += f" Errors: {'; '.join(file_errors[:2])}"  # Show first 2 errors
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Check if dataframe is empty
        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty or contains no data. Please upload a file with KOI astronomical data."
            )
        
        # Get model and check required features
        predictor = get_predictor()
        required_features = predictor.feature_names
        
        missing_features = [f for f in required_features if f not in df.columns]
        available_features = [f for f in required_features if f in df.columns]
        
        if missing_features:
            return ValidationResponse(
                success=False,
                valid=False,
                message=f"Dataset is missing {len(missing_features)} required KOI columns. Found {len(available_features)}/{len(required_features)} required columns. Missing: {missing_features[:5]}{'...' if len(missing_features) > 5 else ''}",
                total_rows=len(df),
                total_columns=len(df.columns),
                sample_columns=list(df.columns)[:10]
            )
        
        return ValidationResponse(
            success=True,
            valid=True,
            message=f"Dataset is valid for prediction! Found all {len(required_features)} required KOI columns with {len(df)} rows of data.",
            total_rows=len(df),
            total_columns=len(df.columns),
            sample_columns=list(df.columns)[:10]
        )
    
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file format. Please ensure the file (CSV/XLS/XLSX) is properly formatted and contains the required KOI columns. Error: {str(e)}"
        )

@app.post("/api/kepler/predict", response_model=PredictionResponse)
async def predict_dataset(file: UploadFile = File(...)):
    """Run Kepler model predictions on uploaded dataset"""
    try:
        # Check file extension first
        if not any(file.filename.lower().endswith(f'.{ext}') for ext in ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file format. Please ensure the file (CSV/XLS/XLSX) is properly formatted and contains the required KOI columns."
            )
        
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty. Please upload a valid CSV/XLS/XLSX file with KOI data."
            )
        
        # Try to read file with multiple approaches
        df = None
        file_errors = []
        
        # Try CSV first (most common and faster)
        if file.filename.lower().endswith('.csv'):
            try:
                detected = chardet.detect(content)
                encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
                df = pd.read_csv(io.BytesIO(content), encoding=encoding)
            except Exception as e:
                file_errors.append(f"CSV parsing error: {str(e)}")
        
        # Try Excel formats
        if df is None and (file.filename.lower().endswith('.xlsx') or file.filename.lower().endswith('.xls')):
            engines = ['openpyxl', 'xlrd'] if file.filename.lower().endswith('.xlsx') else ['xlrd', 'openpyxl']
            
            for engine in engines:
                try:
                    df = pd.read_excel(io.BytesIO(content), engine=engine)
                    break
                except Exception as e:
                    file_errors.append(f"Excel parsing error ({engine}): {str(e)}")
        
        # If all parsing attempts failed
        if df is None:
            error_msg = "Invalid file format. Please ensure the file (CSV/XLS/XLSX) is properly formatted and contains the required KOI columns."
            if file_errors:
                error_msg += f" Parsing errors: {'; '.join(file_errors[:2])}"
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Check if dataframe is empty
        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty or contains no data. Please upload a file with KOI astronomical data."
            )
        
        # Get predictor and validate required features
        predictor = get_predictor()
        required_features = predictor.feature_names
        
        missing_features = [f for f in required_features if f not in df.columns]
        if missing_features:
            raise HTTPException(
                status_code=400,
                detail=f"Dataset is missing {len(missing_features)} required KOI columns: {missing_features[:10]}{'...' if len(missing_features) > 10 else ''}. Please ensure your file contains NASA Kepler Objects of Interest (KOI) data with all required astronomical measurements."
            )
        
        # Get predictions
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
    
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Invalid file format. Please ensure the file (CSV/XLS/XLSX) is properly formatted and contains the required KOI columns. Error: {str(e)}"
        )

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

@app.get("/api/kepler/info")
def get_model_info():
    """Get information about the Kepler model"""
    try:
        predictor = get_predictor()
        
        return {
            "success": True,
            "model_info": {
                "model_type": "SimpleKOIModelPredictor",
                "accuracy": getattr(predictor, "accuracy", 0.91),
                "feature_count": len(predictor.feature_names),
                "feature_names": predictor.feature_names,
                "required_columns": predictor.feature_names,
                "description": "Model trained to classify Kepler Objects of Interest (KOI) as confirmed planets or false positives using NASA Kepler mission data",
                "column_descriptions": {
                    "koi_period": "Orbital period [days]",
                    "koi_time0bk": "Transit Epoch [BKJD]", 
                    "koi_impact": "Impact Parameter",
                    "koi_duration": "Transit Duration [hrs]",
                    "koi_depth": "Transit Depth [ppm]",
                    "koi_prad": "Planetary Radius [Earth radii]",
                    "koi_teq": "Equilibrium Temperature [K]",
                    "koi_insol": "Insolation Flux [Earth flux]",
                    "koi_model_snr": "Transit Signal-to-Noise",
                    "koi_steff": "Stellar Effective Temperature [K]",
                    "koi_slogg": "Stellar Surface Gravity [log10(cm/s**2)]",
                    "koi_srad": "Stellar Radius [Solar radii]",
                    "ra": "Right Ascension [decimal degrees]",
                    "dec": "Declination [decimal degrees]",
                    "koi_kepmag": "Kepler-band [mag]",
                    "koi_fpflag_nt": "Not Transit-Like Flag",
                    "koi_fpflag_ss": "Stellar Eclipse Flag", 
                    "koi_fpflag_co": "Centroid Offset Flag",
                    "koi_fpflag_ec": "Ephemeris Match Indicates Contamination Flag"
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")

# ============= STARTUP =============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, reload=DEBUG)