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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionRequest(BaseModel):
    """Request model for predictions"""
    data: Dict[str, Any]

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "NASA KOI Data Portal API", "status": "online"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

@app.post("/upload/csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload and process CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        contents = await file.read()
        
        # Detect encoding
        detected = chardet.detect(contents)
        encoding = detected['encoding'] if detected['confidence'] > 0.7 else 'utf-8'
        
        # Decode content
        content_str = contents.decode(encoding)
        
        # Read CSV
        df = pd.read_csv(io.StringIO(content_str))
        
        # Basic validation
        if df.empty:
            raise HTTPException(status_code=400, detail="Empty CSV file")
        
        # Return basic info about the dataset
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head().to_dict('records') if len(df) > 0 else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/predict")
async def predict(request: PredictionRequest):
    """Make predictions on KOI data"""
    try:
        # For now, return a mock prediction since we don't have the model working
        return {
            "prediction": "CANDIDATE",
            "confidence": 0.85,
            "message": "Model prediction (demo mode - XGBoost model not loaded)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/api/data/stats")
async def get_data_stats():
    """Get statistics about available data"""
    return {
        "total_objects": 1000,
        "confirmed_planets": 750,
        "false_positives": 200,
        "candidates": 50,
        "message": "Demo statistics"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)