from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import chardet

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
