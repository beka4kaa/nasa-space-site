#!/bin/bash

# NASA KOI Portal Management Script
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

show_help() {
    echo "NASA KOI Portal Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start         Start all services"
    echo "  stop          Stop all services"
    echo "  restart       Restart all services"
    echo "  status        Show service status"
    echo "  logs          Show logs (add service name for specific service)"
    echo "  update        Update and rebuild services"
    echo "  backup        Create backup of data and models"
    echo "  restore       Restore from backup"
    echo "  health        Perform health checks"
    echo "  cleanup       Clean up unused Docker resources"
    echo "  monitor       Show real-time resource monitoring"
    echo "  shell         Open shell in specified container"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs backend"
    echo "  $0 shell backend"
}

start_services() {
    log_info "Starting NASA KOI Portal services..."
    docker-compose up -d
    log_success "Services started successfully!"
    show_status
}

stop_services() {
    log_info "Stopping NASA KOI Portal services..."
    docker-compose down
    log_success "Services stopped successfully!"
}

restart_services() {
    log_info "Restarting NASA KOI Portal services..."
    docker-compose restart
    log_success "Services restarted successfully!"
    show_status
}

show_status() {
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "💻 Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

show_logs() {
    SERVICE=${2:-""}
    if [ -n "$SERVICE" ]; then
        log_info "Showing logs for $SERVICE..."
        docker-compose logs -f "$SERVICE"
    else
        log_info "Showing logs for all services..."
        docker-compose logs -f
    fi
}

update_services() {
    log_info "Updating NASA KOI Portal services..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    log_success "Services updated successfully!"
    perform_health_checks
}

backup_data() {
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    log_info "Creating backup in $BACKUP_DIR..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup uploads and models
    if [ -d "backend/uploads" ]; then
        cp -r backend/uploads "$BACKUP_DIR/"
        log_success "Uploaded files backed up"
    fi
    
    if [ -d "backend/models" ]; then
        cp -r backend/models "$BACKUP_DIR/"
        log_success "Model files backed up"
    fi
    
    # Backup configuration
    cp .env "$BACKUP_DIR/" 2>/dev/null || true
    cp docker-compose.yml "$BACKUP_DIR/"
    
    log_success "Backup created successfully in $BACKUP_DIR"
}

restore_data() {
    if [ -z "$2" ]; then
        log_error "Please specify backup directory"
        echo "Usage: $0 restore [backup_directory]"
        exit 1
    fi
    
    BACKUP_DIR="$2"
    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "Backup directory $BACKUP_DIR not found"
        exit 1
    fi
    
    log_info "Restoring from $BACKUP_DIR..."
    
    # Stop services
    docker-compose down
    
    # Restore data
    if [ -d "$BACKUP_DIR/uploads" ]; then
        rm -rf backend/uploads
        cp -r "$BACKUP_DIR/uploads" backend/
        log_success "Uploaded files restored"
    fi
    
    if [ -d "$BACKUP_DIR/models" ]; then
        rm -rf backend/models
        cp -r "$BACKUP_DIR/models" backend/
        log_success "Model files restored"
    fi
    
    # Start services
    docker-compose up -d
    log_success "Restore completed successfully!"
}

perform_health_checks() {
    log_info "Performing health checks..."
    
    # Wait for services to start
    sleep 10
    
    # Check backend
    if curl -f http://localhost:8001/ping > /dev/null 2>&1; then
        log_success "Backend health check passed ✓"
    else
        log_error "Backend health check failed ✗"
        return 1
    fi
    
    # Check frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_success "Frontend health check passed ✓"
    else
        log_error "Frontend health check failed ✗"
        return 1
    fi
    
    log_success "All health checks passed!"
}

cleanup_docker() {
    log_info "Cleaning up unused Docker resources..."
    docker system prune -f
    docker volume prune -f
    log_success "Docker cleanup completed!"
}

monitor_resources() {
    log_info "Starting real-time resource monitoring (Press Ctrl+C to exit)..."
    docker stats
}

open_shell() {
    SERVICE=${2:-"backend"}
    log_info "Opening shell in $SERVICE container..."
    docker-compose exec "$SERVICE" /bin/bash
}

# Main script logic
case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$@"
        ;;
    update)
        update_services
        ;;
    backup)
        backup_data
        ;;
    restore)
        restore_data "$@"
        ;;
    health)
        perform_health_checks
        ;;
    cleanup)
        cleanup_docker
        ;;
    monitor)
        monitor_resources
        ;;
    shell)
        open_shell "$@"
        ;;
    help|*)
        show_help
        ;;
esac