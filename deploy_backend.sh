#!/bin/bash

# NASA KOI Portal - Complete Deployment Script
# Handles backend setup, testing, and deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_header() {
    echo ""
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}$(printf '=%.0s' {1..60})${NC}"
}

# Main deployment function
deploy_backend() {
    log_header "🚀 NASA KOI Portal - Backend Deployment"
    
    # Check if we're in the right directory
    if [ ! -f "backend/main.py" ]; then
        log_error "Please run this script from the project root directory"
        exit 1
    fi
    
    cd backend
    
    # 1. Environment Setup
    log_header "🔧 Environment Setup"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    log_success "Python found: $(python3 --version)"
    
    # Setup virtual environment
    if [ ! -d "../.venv" ]; then
        log_info "Creating virtual environment..."
        cd ..
        python3 -m venv .venv
        cd backend
    fi
    
    log_info "Activating virtual environment..."
    source ../.venv/bin/activate
    
    # 2. Dependencies
    log_header "📦 Installing Dependencies"
    pip install --upgrade pip
    pip install -r requirements.txt
    log_success "Dependencies installed"
    
    # 3. Directory Setup
    log_header "📁 Setting up directories"
    mkdir -p uploads models logs
    log_success "Directories created"
    
    # 4. Model Setup
    log_header "🤖 Setting up ML Models"
    if [ ! -f "models/simple_test_model.pkl" ]; then
        log_info "Creating ML model..."
        python3 test_model_simple.py
    fi
    log_success "Models ready"
    
    # 5. Configuration
    log_header "⚙️  Configuration Check"
    if [ ! -f ".env" ]; then
        log_warning ".env file not found, creating default..."
        cat > .env << EOF
# Backend Environment Configuration
HOST=0.0.0.0
PORT=8001
DEBUG=False
RELOAD=False
API_PREFIX=/api/v1
API_TITLE=NASA KOI Portal API
API_VERSION=1.0.0
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
MAX_FILE_SIZE=104857600
UPLOAD_DIR=./uploads
MODEL_DIR=./models
LOG_LEVEL=INFO
EOF
    fi
    log_success "Configuration ready"
    
    # 6. Pre-deployment Tests
    log_header "🧪 Running Pre-deployment Tests"
    
    # Test model loading
    log_info "Testing model loading..."
    python3 -c "
from model_utils_working import get_model
predictor = get_model()
print(f'✅ Model loaded - Accuracy: {predictor.accuracy:.3f}')
print(f'✅ Features: {len(predictor.feature_names)}')
"
    
    # Test imports
    log_info "Testing imports..."
    python3 -c "import main; print('✅ All imports successful')"
    
    log_success "All tests passed"
    
    # 7. Clean up existing processes
    log_header "🔄 Cleaning up existing processes"
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    pkill -f "uvicorn.*main:app" 2>/dev/null || true
    sleep 2
    log_success "Cleanup complete"
    
    # 8. Start server
    log_header "🚀 Starting Production Server"
    
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    
    log_info "Server starting on http://localhost:8001"
    log_info "API documentation: http://localhost:8001/docs"
    log_info "Press Ctrl+C to stop"
    echo ""
    
    # Start the server
    python3 -m uvicorn main:app \
        --host 0.0.0.0 \
        --port 8001 \
        --log-level info \
        --access-log \
        --reload
}

# Health check function
health_check() {
    log_header "🏥 Health Check"
    cd backend
    python3 health_check.py
}

# Docker deployment
deploy_docker() {
    log_header "🐳 Docker Deployment"
    
    log_info "Building Docker image..."
    docker build -t nasa-koi-backend -f backend/Dockerfile backend/
    
    log_info "Stopping existing container..."
    docker stop nasa-koi-backend 2>/dev/null || true
    docker rm nasa-koi-backend 2>/dev/null || true
    
    log_info "Starting new container..."
    docker run -d \
        --name nasa-koi-backend \
        -p 8001:8001 \
        -v $(pwd)/backend/uploads:/app/uploads \
        nasa-koi-backend
    
    log_success "Docker container started"
    sleep 5
    health_check
}

# Main script logic
case "${1:-deploy}" in
    "deploy")
        deploy_backend
        ;;
    "health")
        health_check
        ;;
    "docker")
        deploy_docker
        ;;
    "help")
        echo "Usage: $0 [deploy|health|docker|help]"
        echo "  deploy - Deploy backend locally (default)"
        echo "  health - Run health check only"
        echo "  docker - Deploy using Docker"
        echo "  help   - Show this help"
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac