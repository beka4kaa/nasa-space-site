from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import chardet
from typing import Dict, Any
from pydantic import BaseModel
from model_utils_working import get_model, KOIModelPredictor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    print(f"Received file: {file.filename}")
    
    if not (file.filename.endswith('.csv') or file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
        print(f"Invalid file extension: {file.filename}")
        raise HTTPException(status_code=400, detail="Only CSV, XLS, and XLSX files are allowed.")
    
    content = await file.read()
    print(f"File size: {len(content)} bytes")
    
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    
    try:
        print(f"Processing file: {file.filename}")
        
        if file.filename.endswith('.csv'):
            # Auto-detect encoding for CSV files
            detected = chardet.detect(content)
            encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
            print(f"Detected encoding: {encoding}")
            
            try:
                df = pd.read_csv(io.BytesIO(content), encoding=encoding)
            except (UnicodeDecodeError, UnicodeError) as e:
                print(f"Encoding error: {e}")
                # Fallback encodings
                for fallback_encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        print(f"Trying encoding: {fallback_encoding}")
                        df = pd.read_csv(io.BytesIO(content), encoding=fallback_encoding)
                        break
                    except Exception as encoding_error:
                        print(f"Failed with {fallback_encoding}: {encoding_error}")
                        continue
                else:
                    raise HTTPException(status_code=400, detail="Unable to decode CSV file with any supported encoding.")
        
        elif file.filename.endswith('.xlsx'):
            print("Processing XLSX file")
            df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
        
        elif file.filename.endswith('.xls'):
            print("Processing XLS file")
            try:
                df = pd.read_excel(io.BytesIO(content), engine='xlrd')
            except Exception as xls_error:
                print(f"XLS parsing error: {xls_error}")
                # Try to read as CSV if XLS fails
                try:
                    print("Attempting to read XLS file as CSV")
                    detected = chardet.detect(content)
                    encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
                    df = pd.read_csv(io.BytesIO(content), encoding=encoding)
                except Exception as csv_fallback_error:
                    print(f"CSV fallback failed: {csv_fallback_error}")
                    raise HTTPException(
                        status_code=400, 
                        detail="This appears to be a corrupted or unsupported Excel file format. Please try saving it as CSV or a newer Excel format (.xlsx)."
                    )
        
        print(f"DataFrame shape before cleaning: {df.shape}")
        
        # Clean the data
        df = df.dropna(how='all')  # Remove completely empty rows
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Remove unnamed columns
        
        # Handle BOM issues
        if not df.empty and len(df.columns) > 0:
            df.columns = [str(col).replace('\ufeff', '').strip() for col in df.columns]
        
        print(f"DataFrame shape after cleaning: {df.shape}")
        
        if df.empty:
            raise HTTPException(status_code=400, detail="File contains no valid data after cleaning.")
        
        print(f"Columns: {list(df.columns)}")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        error_msg = str(e)
        if "Expected BOF record" in error_msg or "kepid,ko" in error_msg:
            raise HTTPException(status_code=400, detail="This appears to be a corrupted or unsupported Excel file format. Please try saving it as CSV or a newer Excel format (.xlsx).")
        elif "Unsupported format" in error_msg:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please use CSV, XLS, or XLSX files.")
        elif "No columns to parse from file" in error_msg:
            raise HTTPException(status_code=400, detail="The file appears to be empty or contains no readable data.")
        else:
            raise HTTPException(status_code=400, detail=f"Failed to parse file: {error_msg}")
    # Save original file for download
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)
    data = df.head(100).to_dict(orient="records")
    columns = list(df.columns)
    total_rows = len(df)
    return {
        "columns": columns, 
        "data": data, 
        "filename": file.filename,
        "total_rows": total_rows,
        "showing_rows": min(100, total_rows)
    }

@app.get("/download/{filename}")
def download_csv(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    # Determine media type based on file extension
    if filename.endswith('.csv'):
        media_type = "text/csv"
    elif filename.endswith('.xlsx'):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif filename.endswith('.xls'):
        media_type = "application/vnd.ms-excel"
    else:
        media_type = "application/octet-stream"
    
    return StreamingResponse(open(file_path, "rb"), media_type=media_type, headers={"Content-Disposition": f"attachment; filename={filename}"})


# ============= KOI MODEL PREDICTION ENDPOINTS =============

# Pydantic models for request/response validation
class PredictionRequest(BaseModel):
    """Request model for single prediction"""
    features: Dict[str, Any]

class PredictionResponse(BaseModel):
    """Response model for predictions"""
    success: bool
    message: str = ""
    data: Dict[str, Any] = {}


@app.post("/api/koi/predict", response_model=PredictionResponse)
async def predict_koi_dataset(file: UploadFile = File(...)):
    """
    Predict KOI disposition for uploaded dataset
    
    Args:
        file: CSV file containing KOI features
    
    Returns:
        Predictions with probabilities for each sample
    """
    try:
        # Validate file type
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
            raise HTTPException(
                status_code=400, 
                detail="Only CSV, XLS, and XLSX files are supported for KOI predictions"
            )
        
        # Read file content
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        # Parse file with format detection
        try:
            # First try as CSV (most common case)
            detected = chardet.detect(content)
            encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
            df = pd.read_csv(io.BytesIO(content), encoding=encoding)
        except Exception:
            try:
                # If CSV fails, try as Excel XLS
                df = pd.read_excel(io.BytesIO(content), engine='xlrd')
            except Exception:
                try:
                    # If XLS fails, try as Excel XLSX
                    df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unable to read file format. Please ensure the file is a valid CSV, XLS, or XLSX file. Error: {str(e)}"
                    )
        
        # Validate data
        if df.empty:
            raise HTTPException(
                status_code=400, 
                detail="File contains no data"
            )
        
        # Load model and make predictions
        try:
            model = get_model()
            predictions = model.predict(df)
            
            # Add total_samples to the predictions data
            predictions['total_samples'] = len(df)
            
            return PredictionResponse(
                success=True,
                message=f"Successfully predicted {len(df)} samples",
                data=predictions
            )
        
        except FileNotFoundError as e:
            raise HTTPException(
                status_code=500,
                detail="Model file not found. Please ensure the model is properly deployed."
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Prediction failed: {str(e)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@app.post("/api/koi/predict-single", response_model=PredictionResponse)
async def predict_koi_single(request: PredictionRequest):
    """
    Predict KOI disposition for a single set of features
    
    Args:
        request: JSON object containing KOI features
    
    Returns:
        Prediction with probabilities
    """
    try:
        # Load model and make prediction
        model = get_model()
        
        # Convert features dict to DataFrame
        df = pd.DataFrame([request.features])
        prediction = model.predict(df)
        
        if prediction is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to generate prediction"
            )
        
        # Format single prediction result
        single_result = {
            'prediction': prediction['predictions'][0],
            'probabilities': prediction['probabilities'][0],
            'confidence': max(prediction['probabilities'][0]),
            'model_accuracy': prediction['model_accuracy'],
            'feature_count': prediction['feature_count']
        }
        
        return PredictionResponse(
            success=True,
            message="Prediction successful",
            data=single_result
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.get("/api/koi/model-info")
async def get_model_info():
    """
    Get information about the loaded KOI model
    
    Returns:
        Model metadata and feature requirements
    """
    try:
        model = get_model()
        
        return {
            "success": True,
            "model_type": "XGBoost Classifier",
            "classes": list(model.label_mapping.values()),
            "required_features": model.feature_columns if model.feature_columns else [],
            "description": "KOI disposition prediction model (CANDIDATE, CONFIRMED, FALSE POSITIVE)"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load model info: {str(e)}"
        )


@app.post("/api/koi/validate-dataset")
async def validate_koi_dataset(file: UploadFile = File(...)):
    """
    Validate if uploaded dataset is suitable for KOI prediction
    
    Args:
        file: CSV, XLS, or XLSX file to validate
    
    Returns:
        Validation results with missing/extra columns
    """
    try:
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
            raise HTTPException(
                status_code=400,
                detail="Only CSV, XLS, and XLSX files are supported"
            )
        
        content = await file.read()
        
        # Try to detect actual file format by content, not just extension
        try:
            # First try as CSV (most common case)
            detected = chardet.detect(content)
            encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
            df = pd.read_csv(io.BytesIO(content), encoding=encoding)
        except Exception:
            try:
                # If CSV fails, try as Excel XLS
                df = pd.read_excel(io.BytesIO(content), engine='xlrd')
            except Exception:
                try:
                    # If XLS fails, try as Excel XLSX
                    df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unable to read file format. Please ensure the file is a valid CSV, XLS, or XLSX file. Error: {str(e)}"
                    )
        
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        model = get_model()
        
        # Get numeric columns
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        
        # Check for required features (approximate check)
        required_features = ['koi_period', 'koi_srad', 'koi_slogg', 'koi_prad']
        missing_features = [f for f in required_features if f not in df.columns]
        
        return {
            "success": True,
            "valid": len(missing_features) == 0,
            "total_columns": len(df.columns),
            "numeric_columns": len(numeric_cols),
            "total_rows": len(df),
            "missing_required_features": missing_features,
            "sample_columns": df.columns.tolist()[:20],
            "message": "Dataset is valid for prediction" if len(missing_features) == 0 
                      else f"Missing required features: {', '.join(missing_features)}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )
