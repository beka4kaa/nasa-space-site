# syntax=docker/dockerfile:1

# Multi-stage build for NASA KOI Data Portal

# --- Backend Stage ---
FROM python:3.11-slim AS backend
WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend .
EXPOSE 8000

# --- Frontend Stage ---
FROM node:20-alpine AS frontend
WORKDIR /app/frontend

# Install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --only=production

# Copy frontend code
COPY frontend .

# Build the application
RUN npm run build
EXPOSE 3000

# --- Production Stage ---
FROM python:3.11-slim AS production
WORKDIR /app

# Install system dependencies and Node.js
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY --from=backend /app/backend /app/backend
COPY --from=backend /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy frontend build
COPY --from=frontend /app/frontend/.next /app/frontend/.next
COPY --from=frontend /app/frontend/public /app/frontend/public
COPY --from=frontend /app/frontend/package.json /app/frontend/package.json
COPY --from=frontend /app/frontend/node_modules /app/frontend/node_modules

# Create startup script
RUN echo '#!/bin/bash\n\
cd /app/backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &\n\
cd /app/frontend && npm start -- --port 3000 --hostname 0.0.0.0 &\n\
wait\n' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
EXPOSE 3000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health && curl -f http://localhost:3000 || exit 1

# Start the application
CMD ["/app/start.sh"]
CMD ["sh", "-c", "cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 & cd ../frontend && npm run start"]
