#!/bin/bash

# NASA KOI Portal - Backend Startup Script
# Production ready deployment script

set -e  # Exit on any error

echo "🚀 NASA KOI Portal Backend - Starting..."
echo "========================================"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run from backend directory."
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads models logs
echo "✅ Directories created"

# Check if virtual environment exists
if [ ! -d "../.venv" ]; then
    echo "⚠️  Virtual environment not found, creating one..."
    cd ..
    python3 -m venv .venv
    cd backend
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../.venv/bin/activate

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check model files
echo "🤖 Checking model files..."
if [ ! -f "models/simple_test_model.pkl" ]; then
    echo "⚠️  Model file missing, creating it..."
    python3 test_model_simple.py
fi
echo "✅ Model files ready"

# Test model loading
echo "🧪 Testing model loading..."
python3 -c "
from model_utils_working import get_model
predictor = get_model()
print(f'✅ Model loaded successfully - Accuracy: {predictor.accuracy:.3f}')
print(f'✅ Features: {len(predictor.feature_names)}')
"

# Kill any existing processes on port 8001
echo "🔄 Cleaning up existing processes..."
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
sleep 2

# Set environment variables
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Start the server
echo "🚀 Starting FastAPI server..."
echo "Server will be available at: http://localhost:8001"
echo "API docs at: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"

# Start with uvicorn
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload --log-level info