#!/bin/bash

# start_api.sh - Clean startup script for NASA KOI Portal API
set -e

echo "🚀 Starting NASA KOI Portal API..."

# Clean environment from other projects
unset NODE_ENV
unset NEXT_PUBLIC_API_URL
unset NEXT_PUBLIC_APP_NAME
unset NEXT_PUBLIC_APP_VERSION
unset BACKEND_HOST
unset BACKEND_PORT
unset UPLOAD_DIR
unset MODEL_PATH
unset FRONTEND_HOST
unset FRONTEND_PORT

# Set our environment
export HOST=0.0.0.0
export PORT=8001
export DEBUG=True

# Change to backend directory
cd "$(dirname "$0")"

# Find available port
PORT=8001
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
    echo "Port $PORT is busy, trying $((PORT + 1))..."
    PORT=$((PORT + 1))
done

export PORT=$PORT
echo "Starting server on port $PORT..."

# Start the server
python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT --reload