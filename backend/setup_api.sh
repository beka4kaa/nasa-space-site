#!/bin/bash

# KOI Model API Setup Script
# This script sets up and tests the KOI prediction API

echo "========================================"
echo "KOI Model API Setup"
echo "========================================"
echo ""

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
    echo "Error: Please run this script from the backend directory"
    exit 1
fi

# Check if model file exists
if [ ! -f "models/boost_test_model.json" ]; then
    echo "Warning: Model file not found at models/boost_test_model.json"
    echo "Please ensure the model file is in the correct location"
    exit 1
fi

echo "✓ Model file found"
echo ""

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Test imports
echo "Testing imports..."
python -c "import fastapi; import xgboost; import sklearn; import pandas; import numpy; print('✓ All imports successful')"

if [ $? -ne 0 ]; then
    echo "Error: Import test failed"
    exit 1
fi
echo ""

# Start server in background
echo "Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Check if server is running
curl -s http://localhost:8000/ping > /dev/null

if [ $? -eq 0 ]; then
    echo "✓ Server started successfully (PID: $SERVER_PID)"
    echo ""
    echo "========================================"
    echo "Setup Complete!"
    echo "========================================"
    echo ""
    echo "API is running at: http://localhost:8000"
    echo "Swagger docs: http://localhost:8000/docs"
    echo "ReDoc: http://localhost:8000/redoc"
    echo ""
    echo "To test the API, run: python test_api.py"
    echo "To stop the server: kill $SERVER_PID"
    echo ""
else
    echo "Error: Server failed to start"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

# Keep script running
wait $SERVER_PID
