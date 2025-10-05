# 🚀 NASA KOI Portal - Deployment Guide

## Quick Commands (Backend Only)

### 1. Simple Backend Deployment
```bash
./deploy_backend_only.sh
```

### 2. Backend via Main Script
```bash
./deploy.sh production backend
```

### 3. Local Development
```bash
./start_backend_only.sh
```

---

## Deployment Options

### Backend Only Deployments
| Command | Description |
|---------|-------------|
| `./deploy_backend_only.sh` | Dedicated backend-only Docker deployment |
| `./deploy.sh development backend` | Backend-only in development mode |
| `./deploy.sh production backend` | Backend-only in production mode |
| `./start_backend_only.sh` | Local development server |

### Full Stack Deployments
| Command | Description |
|---------|-------------|
| `./deploy.sh` | Full stack (development mode) |
| `./deploy.sh production` | Full stack (production mode) |
| `./deploy.sh production full` | Full stack (explicit) |

---

## Current Issue Fix

The deployment was trying to build frontend because:
1. ❌ Main `docker-compose.yml` includes frontend service
2. ❌ Root `.env` file had conflicting variables
3. ❌ No backend-only deployment option

### Fixed By:
1. ✅ Created `docker-compose.backend.yml` for backend only
2. ✅ Updated scripts to handle conflicting `.env` files
3. ✅ Added backend-only deployment options
4. ✅ Made main script configurable (`backend` vs `full`)

---

## File Structure

```
├── deploy.sh                    # Main deployment (supports backend/full)
├── deploy_backend_only.sh       # Dedicated backend deployment
├── start_backend_only.sh        # Local development
├── docker-compose.yml           # Full stack
├── docker-compose.backend.yml   # Backend only
└── backend/
    ├── .env                     # Backend configuration
    ├── Dockerfile              # Backend container
    └── requirements.txt        # Python dependencies
```

---

## Usage Examples

### Deploy Only Backend to Production
```bash
./deploy_backend_only.sh production
```

### Check Backend Status
```bash
curl http://localhost:8001/ping
curl http://localhost:8001/api/kepler/model-info
```

### View Backend Logs
```bash
docker-compose -f docker-compose.backend.yml logs -f
```

### Stop Backend
```bash
docker-compose -f docker-compose.backend.yml down
```

---

**Now you can deploy ONLY the backend! No more frontend builds! 🎯**