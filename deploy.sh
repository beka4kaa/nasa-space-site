#!/bin/bash

# NASA KOI Portal Deployment Scr# Set deployment mode and scope
DEPLOYMENT_MODE=${1:-"development"}
DEPLOYMENT_SCOPE=${2:-"full"}

log_info "Deployment mode: $DEPLOYMENT_MODE"
log_info "Deployment scope: $DEPLOYMENT_SCOPE"

# Choose compose file based on scope
if [ "$DEPLOYMENT_SCOPE" = "backend" ]; then
    COMPOSE_FILE="docker-compose.backend.yml"
    log_info "🎯 BACKEND ONLY deployment selected"
else
    COMPOSE_FILE="docker-compose.yml"
    log_info "🌐 FULL STACK deployment selected"
fi

# Environment file setup
if [ "$DEPLOYMENT_MODE" = "production" ]; then
    ENV_FILE=".env.production"
else
    ENV_FILE=".env"
fie: ./deploy.sh [development|production] [backend|full]

set -e

echo "🚀 Starting NASA KOI Portal Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
DEPLOYMENT_MODE=${1:-"development"}
log_info "Deployment mode: $DEPLOYMENT_MODE"

# Environment file setup
if [ "$DEPLOYMENT_MODE" = "production" ]; then
    ENV_FILE=".env.production"
else
    ENV_FILE=".env.example"
fi

if [ ! -f "$ENV_FILE" ]; then
    log_error "Environment file $ENV_FILE not found!"
    exit 1
fi

log_info "Using environment file: $ENV_FILE"

# Copy environment file
cp "$ENV_FILE" ".env"

# Create necessary directories
log_info "Creating necessary directories..."
mkdir -p backend/uploads
mkdir -p backend/models
mkdir -p ssl

# Check if model files exist
if [ ! -f "backend/models/simple_test_model.pkl" ]; then
    log_warning "Model file not found. The application will create it on first run."
fi

# Handle conflicting root .env for backend-only deployments
if [ "$DEPLOYMENT_SCOPE" = "backend" ] && [ -f ".env" ]; then
    log_warning "Moving conflicting root .env to prevent backend issues"
    mv .env .env.backup.$(date +%s)
fi

# Build and start services
log_info "Building Docker images..."
docker-compose -f "$COMPOSE_FILE" build --no-cache

log_info "Starting services..."
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for services to be healthy
log_info "Waiting for services to be healthy..."
sleep 30

# Health checks
log_info "Performing health checks..."

# Check backend
if curl -f http://localhost:8001/ping > /dev/null 2>&1; then
    log_success "Backend is healthy ✓"
else
    log_error "Backend health check failed ✗"
    docker-compose -f "$COMPOSE_FILE" logs backend
    exit 1
fi

# Check frontend only for full stack deployments
if [ "$DEPLOYMENT_SCOPE" = "full" ]; then
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_success "Frontend is healthy ✓"
    else
        log_error "Frontend health check failed ✗"
        docker-compose -f "$COMPOSE_FILE" logs frontend
        exit 1
    fi
fi

# Display status
if [ "$DEPLOYMENT_SCOPE" = "backend" ]; then
    log_success "🎉 NASA KOI Portal Backend deployed successfully!"
else
    log_success "🎉 NASA KOI Portal deployed successfully!"
fi

echo ""
echo "📊 Service Status:"
docker-compose -f "$COMPOSE_FILE" ps
echo ""
echo "🌐 Access URLs:"
if [ "$DEPLOYMENT_SCOPE" = "full" ]; then
    echo "  Frontend: http://localhost:3000"
fi
echo "  Backend API: http://localhost:8001"
echo "  API Documentation: http://localhost:8001/docs"
echo "  Health Check: http://localhost:8001/ping"
echo ""
echo "📋 Useful Commands:"
echo "  View logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "  Stop services: docker-compose -f $COMPOSE_FILE down"
echo "  Restart services: docker-compose -f $COMPOSE_FILE restart"
echo "  Update services: docker-compose -f $COMPOSE_FILE up -d --build"
echo ""

# Show resource usage
echo "💻 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"