# NASA KOI Portal - Deployment Guide

This guide provides comprehensive instructions for deploying the NASA KOI Portal application in various environments.

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available
- 10GB+ disk space

### One-Command Deployment

```bash
# Clone the repository
git clone <repository-url>
cd site_nasa

# Deploy in development mode
./deploy.sh development

# Deploy in production mode
./deploy.sh production
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## 📋 Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Individual Services

#### Backend Only
```bash
cd backend
docker build -t nasa-koi-backend .
docker run -p 8001:8001 -v $(pwd)/uploads:/app/uploads nasa-koi-backend
```

#### Frontend Only
```bash
cd frontend
docker build -t nasa-koi-frontend .
docker run -p 3000:3000 nasa-koi-frontend
```

## ⚙️ Configuration

### Environment Variables

Copy the appropriate environment file:

```bash
# Development
cp .env.example .env

# Production
cp .env.production .env
```

Key configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| `NODE_ENV` | Environment mode | `development` |
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8001` |
| `BACKEND_PORT` | Backend port | `8001` |
| `FRONTEND_PORT` | Frontend port | `3000` |
| `MAX_FILE_SIZE` | Maximum upload size | `100MB` |

### Production Configuration

For production deployment:

1. **Update environment variables**:
   ```bash
   # Edit .env.production
   NEXT_PUBLIC_API_URL=https://your-domain.com/api
   NODE_ENV=production
   ```

2. **Configure SSL** (recommended):
   - Place SSL certificates in `./ssl/` directory
   - Uncomment HTTPS configuration in `nginx.conf`
   - Update domain name in nginx configuration

3. **Security considerations**:
   - Change default secret keys
   - Configure firewall rules
   - Enable HTTPS
   - Set up monitoring

## 🛠️ Management Commands

Use the management script for common operations:

```bash
# Start services
./manage.sh start

# Stop services
./manage.sh stop

# Restart services
./manage.sh restart

# View status
./manage.sh status

# View logs
./manage.sh logs
./manage.sh logs backend  # Specific service

# Update services
./manage.sh update

# Create backup
./manage.sh backup

# Restore from backup
./manage.sh restore backups/20231205_143022

# Health checks
./manage.sh health

# Resource monitoring
./manage.sh monitor

# Open container shell
./manage.sh shell backend
./manage.sh shell frontend

# Clean up Docker resources
./manage.sh cleanup
```

## 📊 Monitoring & Health Checks

### Health Endpoints

- **Backend**: `GET /ping`
- **Frontend**: `GET /` (returns status 200)

### Resource Monitoring

```bash
# Real-time monitoring
./manage.sh monitor

# Container stats
docker stats

# Service logs
docker-compose logs -f [service_name]
```

### Performance Metrics

The application provides the following performance characteristics:

- **Model predictions**: 70,000+ predictions/second
- **File upload**: Supports files up to 100MB
- **Response time**: < 1s for 100 samples
- **Memory usage**: ~512MB backend, ~256MB frontend
- **Model accuracy**: 91%+

## 🔧 Troubleshooting

### Common Issues

1. **Port conflicts**:
   ```bash
   # Check what's using the ports
   lsof -i :3000
   lsof -i :8001
   
   # Kill processes if needed
   sudo kill -9 $(lsof -t -i:3000)
   ```

2. **Permission issues**:
   ```bash
   # Fix Docker permissions
   sudo usermod -aG docker $USER
   
   # Fix file permissions
   sudo chown -R $USER:$USER backend/uploads
   ```

3. **Memory issues**:
   ```bash
   # Check memory usage
   free -h
   
   # Increase swap if needed
   sudo fallocate -l 2G /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

4. **Model loading issues**:
   ```bash
   # Check if model files exist
   ls -la backend/models/
   
   # Regenerate model if needed
   docker-compose exec backend python test_model_simple.py
   ```

### Log Analysis

```bash
# View all logs
docker-compose logs -f

# Backend logs only
docker-compose logs -f backend

# Frontend logs only
docker-compose logs -f frontend

# Nginx logs (if using)
docker-compose logs -f nginx
```

## 🚢 Production Deployment

### Cloud Deployment

#### AWS ECS
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

docker build -t nasa-koi-backend backend/
docker tag nasa-koi-backend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/nasa-koi-backend:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/nasa-koi-backend:latest
```

#### Google Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/nasa-koi-backend backend/
gcloud run deploy --image gcr.io/PROJECT-ID/nasa-koi-backend --platform managed
```

#### Azure Container Instances
```bash
# Build and push to ACR
az acr build --registry myregistry --image nasa-koi-backend backend/
az container create --resource-group myResourceGroup --name nasa-koi --image myregistry.azurecr.io/nasa-koi-backend
```

### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nasa-koi-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nasa-koi-backend
  template:
    metadata:
      labels:
        app: nasa-koi-backend
    spec:
      containers:
      - name: backend
        image: nasa-koi-backend:latest
        ports:
        - containerPort: 8001
        env:
        - name: PORT
          value: "8001"
---
apiVersion: v1
kind: Service
metadata:
  name: nasa-koi-backend-service
spec:
  selector:
    app: nasa-koi-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8001
  type: LoadBalancer
```

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale backend instances
docker-compose up -d --scale backend=3

# Load balancer configuration needed for multiple instances
```

### Vertical Scaling

Update `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

## 🔒 Security

### Security Checklist

- [ ] Change default passwords/secrets
- [ ] Enable HTTPS with valid certificates
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Backup encryption
- [ ] Container scanning

### SSL/TLS Setup

1. Obtain certificates (Let's Encrypt recommended):
   ```bash
   certbot certonly --webroot -w /var/www/html -d yourdomain.com
   ```

2. Update nginx.conf with SSL configuration
3. Restart services:
   ```bash
   ./manage.sh restart
   ```

## 💾 Backup & Recovery

### Automated Backups

```bash
# Create daily backup cron job
echo "0 2 * * * /path/to/site_nasa/manage.sh backup" | crontab -
```

### Manual Backup

```bash
# Create backup
./manage.sh backup

# Restore from backup
./manage.sh restore backups/20231205_143022
```

### Backup Contents

- Application data (`backend/uploads/`)
- ML models (`backend/models/`)
- Configuration files
- Docker volumes (if using)

## 📞 Support

For deployment issues:

1. Check the troubleshooting section above
2. Review application logs
3. Verify system requirements
4. Check network connectivity
5. Validate configuration files

## 🔄 Updates

### Application Updates

```bash
# Pull latest changes
git pull origin main

# Update and restart services
./manage.sh update
```

### Security Updates

```bash
# Update base images
docker-compose build --no-cache --pull

# Update dependencies
# Update requirements.txt and package.json
./manage.sh update
```

---

**NASA KOI Portal** - Discover exoplanets with AI-powered analysis 🚀