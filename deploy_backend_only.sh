#!/bin/bash

# NASA KOI Portal - Backend Only Deployment
# This script deploys ONLY the backend service

set -e

echo "🚀 NASA KOI Portal - Backend Only Deployment"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Set deployment mode
DEPLOYMENT_MODE=${1:-"production"}
log_info "Deployment mode: $DEPLOYMENT_MODE"

# Stop any existing containers
log_info "Stopping existing containers..."
docker-compose -f docker-compose.backend.yml down 2>/dev/null || true

# Environment setup
log_info "Setting up environment..."
if [ -f "backend/.env" ]; then
    log_success "Backend environment found"
else
    log_warning "No backend/.env found, using defaults"
fi

# Temporary fix for conflicting root .env
if [ -f ".env" ]; then
    log_warning "Found conflicting root .env, moving to backup"
    mv .env .env.backup.$(date +%s)
fi

# Build and start backend service
log_info "Building backend Docker image..."
docker-compose -f docker-compose.backend.yml build --no-cache

log_info "Starting backend service..."
docker-compose -f docker-compose.backend.yml up -d

# Wait for backend to be ready
log_info "Waiting for backend to be ready..."
sleep 15

# Health check
log_info "Performing health check..."
for i in {1..30}; do
    if curl -f http://localhost:8001/ping > /dev/null 2>&1; then
        log_success "Backend is healthy ✓"
        break
    fi
    if [ $i -eq 30 ]; then
        log_error "Backend health check failed after 30 attempts ✗"
        docker-compose -f docker-compose.backend.yml logs backend
        exit 1
    fi
    log_info "Waiting for backend... ($i/30)"
    sleep 2
done

# Display status
log_success "🎉 NASA KOI Portal Backend deployed successfully!"
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.backend.yml ps
echo ""
echo "🌐 Access URLs:"
echo "  Backend API: http://localhost:8001"
echo "  API Documentation: http://localhost:8001/docs"
echo "  Health Check: http://localhost:8001/ping"
echo ""
echo "📋 Useful Commands:"
echo "  View logs: docker-compose -f docker-compose.backend.yml logs -f"
echo "  Stop service: docker-compose -f docker-compose.backend.yml down"
echo "  Restart service: docker-compose -f docker-compose.backend.yml restart"
echo "  Update service: docker-compose -f docker-compose.backend.yml up -d --build"
echo ""

# Show resource usage
echo "💻 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" nasa-koi-backend

# Test API endpoints
echo ""
echo "🧪 Quick API Test:"
echo "Ping: $(curl -s http://localhost:8001/ping)"
echo "Model Info: $(curl -s http://localhost:8001/api/kepler/model-info | head -100)..."