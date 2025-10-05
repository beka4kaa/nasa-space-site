#!/bin/bash

# NASA KOI Portal - Backend Only Deployment
# Fixed version that handles environment conflicts

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

echo -e "${BLUE}🚀 NASA KOI Portal - Backend Only Deployment${NC}"
echo "==============================================="

# Check we're in the right place
if [ ! -f "backend/main.py" ]; then
    log_error "Please run from project root directory"
    exit 1
fi

# Handle conflicting .env file
if [ -f ".env" ]; then
    log_warning "Found conflicting .env in root directory"
    log_info "Temporarily renaming .env to .env.backup"
    mv .env .env.backup
    ENV_BACKUP_CREATED=true
fi

cd backend

# Kill any existing processes
log_info "Stopping existing backend processes..."
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "nohup.*uvicorn" 2>/dev/null || true
sleep 2

# Setup environment
log_info "Setting up Python environment..."
if [ ! -d "../.venv" ]; then
    cd ..
    python3 -m venv .venv
    cd backend
fi

source ../.venv/bin/activate

# Install dependencies
log_info "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads models logs

# Test imports
log_info "Testing application..."
python3 -c "
try:
    from main import app
    print('✅ Application imports successful')
    from model_utils_working import get_model
    model = get_model()
    print(f'✅ Model loaded - Accuracy: {model.accuracy:.3f}')
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
"

# Deployment mode selection
echo ""
echo "Select deployment mode:"
echo "1. Development (with reload, interactive)"
echo "2. Production (background, logged)"
echo ""
read -p "Enter choice (1-2): " choice

case $choice in
    1)
        log_success "Starting backend in development mode..."
        log_info "Backend: http://localhost:8001"
        log_info "API docs: http://localhost:8001/docs"
        log_info "Press Ctrl+C to stop"
        echo ""
        
        python3 -m uvicorn main:app \
            --host 0.0.0.0 \
            --port 8001 \
            --log-level info \
            --reload
        ;;
    2)
        log_success "Starting backend in production mode..."
        
        nohup python3 -m uvicorn main:app \
            --host 0.0.0.0 \
            --port 8001 \
            --log-level info \
            --access-log > backend.log 2>&1 &
        
        BACKEND_PID=$!
        echo $BACKEND_PID > backend.pid
        
        sleep 3
        
        # Test if backend is running
        if curl -s "http://localhost:8001/ping" > /dev/null; then
            log_success "Backend started successfully!"
            log_info "Backend: http://localhost:8001"
            log_info "API docs: http://localhost:8001/docs"
            log_info "Logs: tail -f backend.log"
            log_info "Stop: kill \$(cat backend.pid)"
        else
            log_error "Backend failed to start. Check backend.log"
            exit 1
        fi
        ;;
    *)
        log_error "Invalid choice"
        exit 1
        ;;
esac

# Cleanup function
cleanup() {
    if [ "$ENV_BACKUP_CREATED" = true ] && [ -f "../.env.backup" ]; then
        log_info "Restoring original .env file"
        cd ..
        mv .env.backup .env
    fi
}

trap cleanup EXIT