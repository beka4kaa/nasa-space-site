# syntax=docker/dockerfile:1

# --- Backend ---
FROM python:3.11-slim AS backend
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend .
EXPOSE 8000

# --- Frontend ---
FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend .
RUN npm run build
EXPOSE 3000

# --- Final image ---
FROM python:3.11-slim
WORKDIR /app
COPY --from=backend /app/backend /app/backend
COPY --from=frontend /app/frontend/.next /app/frontend/.next
COPY --from=frontend /app/frontend/public /app/frontend/public
COPY --from=frontend /app/frontend/package.json /app/frontend/package.json
COPY --from=frontend /app/frontend/node_modules /app/frontend/node_modules

# Start both servers
CMD ["sh", "-c", "cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 & cd ../frontend && npm run start"]
