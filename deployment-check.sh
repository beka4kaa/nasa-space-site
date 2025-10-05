#!/bin/bash

# deployment-check.sh - Quick deployment health verification
set -e

echo "🚀 NASA KOI Portal - Deployment Health Check"
echo "============================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a service is responding
check_service() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Checking $name... "
    
    if command -v curl >/dev/null 2>&1; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
        if [ "$response" = "$expected_status" ]; then
            echo -e "${GREEN}✓ OK${NC} (HTTP $response)"
            return 0
        else
            echo -e "${RED}✗ FAILED${NC} (HTTP $response)"
            return 1
        fi
    else
        echo -e "${YELLOW}? SKIPPED${NC} (curl not available)"
        return 0
    fi
}

# Function to check if Docker service is running
check_docker_service() {
    local service_name=$1
    echo -n "Checking Docker service $service_name... "
    
    if docker-compose ps -q "$service_name" >/dev/null 2>&1; then
        status=$(docker-compose ps --format json "$service_name" 2>/dev/null | grep -o '"State":"[^"]*"' | cut -d'"' -f4)
        if [ "$status" = "running" ]; then
            echo -e "${GREEN}✓ RUNNING${NC}"
            return 0
        else
            echo -e "${RED}✗ $status${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ NOT FOUND${NC}"
        return 1
    fi
}

# Main health checks
echo ""
echo "📊 Service Health Check:"
echo "------------------------"

# Check if docker-compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    echo -e "${RED}✗ docker-compose not found${NC}"
    exit 1
fi

# Check Docker services
failed_services=0

if check_docker_service "backend"; then
    sleep 2
    check_service "Backend API" "http://localhost:8001/ping" || ((failed_services++))
else
    ((failed_services++))
fi

if check_docker_service "frontend"; then
    sleep 2
    check_service "Frontend" "http://localhost:3000" || ((failed_services++))
else
    ((failed_services++))
fi

# Check nginx if it's running
if docker-compose ps -q nginx >/dev/null 2>&1; then
    if check_docker_service "nginx"; then
        sleep 1
        check_service "Nginx Proxy" "http://localhost:80" || ((failed_services++))
    else
        ((failed_services++))
    fi
fi

echo ""
echo "🔍 System Information:"
echo "----------------------"

# Docker info
echo -n "Docker status... "
if docker info >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
    ((failed_services++))
fi

# Memory check
echo -n "Available memory... "
if command -v free >/dev/null 2>&1; then
    mem_available=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    if [ "$mem_available" -gt 500 ]; then
        echo -e "${GREEN}✓ ${mem_available}MB${NC}"
    else
        echo -e "${YELLOW}⚠ ${mem_available}MB (low)${NC}"
    fi
else
    echo -e "${YELLOW}? Unknown${NC}"
fi

# Disk space check
echo -n "Disk space... "
if command -v df >/dev/null 2>&1; then
    disk_available=$(df -h . | awk 'NR==2{print $4}')
    echo -e "${GREEN}✓ ${disk_available} available${NC}"
else
    echo -e "${YELLOW}? Unknown${NC}"
fi

echo ""
echo "📂 File System Check:"
echo "---------------------"

# Check important directories and files
check_path() {
    local path=$1
    local type=$2
    echo -n "Checking $path... "
    
    if [ -$type "$path" ]; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${RED}✗ Missing${NC}"
        ((failed_services++))
    fi
}

check_path "backend/models" "d"
check_path "backend/uploads" "d"
check_path "backend/requirements.txt" "f"
check_path "frontend/package.json" "f"
check_path "docker-compose.yml" "f"

echo ""
echo "🧠 ML Model Check:"
echo "------------------"

# Check model files
echo -n "Model files... "
model_count=$(find backend/models -name "*.json" -o -name "*.pkl" -o -name "*.joblib" 2>/dev/null | wc -l)
if [ "$model_count" -gt 0 ]; then
    echo -e "${GREEN}✓ Found $model_count model file(s)${NC}"
else
    echo -e "${YELLOW}⚠ No model files found${NC}"
fi

# Test prediction endpoint if backend is running
if docker-compose ps -q backend >/dev/null 2>&1; then
    echo -n "Prediction endpoint... "
    if command -v curl >/dev/null 2>&1; then
        # Simple test data
        test_response=$(curl -s -X POST "http://localhost:8001/predict" \
            -H "Content-Type: application/json" \
            -d '{"data": [[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0]]}' \
            2>/dev/null || echo "ERROR")
        
        if echo "$test_response" | grep -q "predictions"; then
            echo -e "${GREEN}✓ Working${NC}"
        else
            echo -e "${RED}✗ Not responding${NC}"
            ((failed_services++))
        fi
    else
        echo -e "${YELLOW}? Skipped (curl not available)${NC}"
    fi
fi

echo ""
echo "📈 Final Status:"
echo "=================="

if [ $failed_services -eq 0 ]; then
    echo -e "${GREEN}🎉 All systems operational!${NC}"
    echo ""
    echo "🌐 Access your application:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend:  http://localhost:8001"
    echo "   API Docs: http://localhost:8001/docs"
    exit 0
else
    echo -e "${RED}❌ $failed_services issue(s) found${NC}"
    echo ""
    echo "🔧 Troubleshooting steps:"
    echo "   1. Run: docker-compose ps"
    echo "   2. Check logs: docker-compose logs"
    echo "   3. Restart services: ./manage.sh restart"
    echo "   4. Check DEPLOYMENT.md for detailed troubleshooting"
    exit 1
fi