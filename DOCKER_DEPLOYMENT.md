# Docker Deployment Guide

This guide explains how to deploy the Stock Trading Decision Support System using Docker and Docker Compose.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Docker Services](#docker-services)
- [Configuration](#configuration)
- [Building Images](#building-images)
- [Running Services](#running-services)
- [Monitoring & Health Checks](#monitoring--health-checks)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 8GB RAM
- 20GB free disk space

Install Docker:
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# macOS
brew install docker docker-compose

# Windows
# Download Docker Desktop from https://www.docker.com/products/docker-desktop
```

## Quick Start

### 1. Clone and Configure

```bash
git clone <repository-url>
cd stock-trading-decision-support

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Build and Run

```bash
# Build all services
docker-compose -f docker/docker-compose.yml build

# Start API and Dashboard
docker-compose -f docker/docker-compose.yml up -d

# Check status
docker-compose -f docker/docker-compose.yml ps
```

### 3. Access Services

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501
- **Health Check**: http://localhost:8000/health

## Docker Services

### 1. API Service (`api`)

**Purpose**: FastAPI backend serving ML predictions and trading signals

**Features**:
- Multi-stage build for optimized image size
- Non-root user for security
- Health checks enabled
- Resource limits configured

**Ports**: 8000

**Environment Variables**:
- `API_HOST=0.0.0.0`
- `API_PORT=8000`
- `APP_ENV=production`

### 2. Dashboard Service (`dashboard`)

**Purpose**: Streamlit dashboard for visualization

**Features**:
- Interactive web interface
- Read-only access to data/models
- Automatic refresh capabilities

**Ports**: 8501

**Environment Variables**:
- `STREAMLIT_SERVER_PORT=8501`
- `API_BASE_URL=http://api:8000`

### 3. Training Service (`training`)

**Purpose**: Optional service for model training/retraining

**Usage**:
```bash
# Run with training profile
docker-compose -f docker/docker-compose.yml --profile training up

# Run specific training command
docker-compose -f docker/docker-compose.yml run training \
  python scripts/train_models.py --symbols AAPL,MSFT --lookback 60
```

## Configuration

### Environment Variables

Key variables in `.env`:

```bash
# Application
APP_ENV=production
DEBUG=False
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000

# Dashboard
DASHBOARD_PORT=8501

# Model Configuration
LSTM_EPOCHS=100
ENSEMBLE_WEIGHTS=0.33,0.33,0.34

# Trading
INITIAL_CAPITAL=100000
MAX_POSITION_SIZE=0.05
```

### Volume Mounts

Data persistence through volumes:

```yaml
volumes:
  - ./data:/app/data          # Historical data
  - ./models:/app/models      # Trained models
  - ./logs:/app/logs          # Application logs
  - ./config:/app/config      # Configuration files
```

## Building Images

### Build All Services

```bash
cd docker
docker-compose build
```

### Build Individual Service

```bash
# API only
docker-compose build api

# Dashboard only
docker-compose build dashboard
```

### Build with No Cache

```bash
docker-compose build --no-cache
```

### Tag Images

```bash
# Tag API image
docker tag trading-api:latest your-registry/trading-api:v1.0.0

# Push to registry
docker push your-registry/trading-api:v1.0.0
```

## Running Services

### Start All Services

```bash
docker-compose -f docker/docker-compose.yml up -d
```

### Start Specific Service

```bash
docker-compose -f docker/docker-compose.yml up -d api
```

### View Logs

```bash
# All services
docker-compose -f docker/docker-compose.yml logs -f

# Specific service
docker-compose -f docker/docker-compose.yml logs -f api

# Last 100 lines
docker-compose -f docker/docker-compose.yml logs --tail=100 dashboard
```

### Stop Services

```bash
# Stop all
docker-compose -f docker/docker-compose.yml down

# Stop and remove volumes
docker-compose -f docker/docker-compose.yml down -v

# Stop specific service
docker-compose -f docker/docker-compose.yml stop api
```

### Restart Services

```bash
# Restart all
docker-compose -f docker/docker-compose.yml restart

# Restart specific service
docker-compose -f docker/docker-compose.yml restart api
```

## Monitoring & Health Checks

### Health Check Endpoints

```bash
# API health
curl http://localhost:8000/health

# Dashboard health (internal)
curl http://localhost:8501/_stcore/health
```

### Check Container Health

```bash
# Docker native
docker ps

# Docker compose
docker-compose -f docker/docker-compose.yml ps
```

### Resource Usage

```bash
# Real-time stats
docker stats

# Specific container
docker stats trading-api
```

### Access Container Shell

```bash
# API container
docker-compose -f docker/docker-compose.yml exec api /bin/bash

# Dashboard container
docker-compose -f docker/docker-compose.yml exec dashboard /bin/sh
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Change port in .env
API_PORT=8001
```

#### 2. Permission Denied

```bash
# Fix data directory permissions
sudo chown -R $(id -u):$(id -g) data/ models/ logs/
```

#### 3. Out of Memory

```bash
# Increase Docker memory limit (Docker Desktop)
# Settings > Resources > Memory > 8GB

# Or modify docker-compose.yml resource limits
```

#### 4. Model Not Found

```bash
# Ensure models are trained
docker-compose -f docker/docker-compose.yml run training \
  python scripts/train_models.py --symbols AAPL
```

### Debug Mode

Enable detailed logging:

```bash
# Set in .env
DEBUG=True
LOG_LEVEL=DEBUG

# Restart services
docker-compose -f docker/docker-compose.yml restart
```

### Clean Everything

```bash
# Stop and remove containers, networks, volumes
docker-compose -f docker/docker-compose.yml down -v

# Remove all images
docker rmi $(docker images -q trading-*)

# Clean system
docker system prune -a
```

## Production Deployment

### 1. Security Hardening

```bash
# Update .env for production
APP_ENV=production
DEBUG=False
API_RELOAD=False

# Use secrets management
docker secret create db_password /path/to/password
```

### 2. Resource Limits

Update `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '1.0'
      memory: 2G
```

### 3. Networking

```bash
# Use reverse proxy (Nginx)
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### 4. Monitoring

```bash
# Add Prometheus & Grafana
docker-compose -f docker/docker-compose.yml \
               -f docker/docker-compose.monitoring.yml up -d
```

### 5. Backup Strategy

```bash
# Backup volumes
docker run --rm \
  -v trading_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/data-backup-$(date +%Y%m%d).tar.gz /data

# Restore
docker run --rm \
  -v trading_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/data-backup-20240101.tar.gz -C /
```

### 6. CI/CD Integration

GitHub Actions workflow (`.github/workflows/ci.yaml`):
- Automated testing on push
- Docker image building
- Push to container registry
- Deploy to production (optional)

### 7. Logging

Use centralized logging:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "100m"
    max-file: "10"
    labels: "service"
```

## Advanced Usage

### Custom Network

```bash
# Create custom network
docker network create trading-net

# Use in docker-compose.yml
networks:
  default:
    external:
      name: trading-net
```

### Multi-Stage Deployment

```bash
# Development
docker-compose -f docker/docker-compose.yml \
               -f docker/docker-compose.dev.yml up

# Production
docker-compose -f docker/docker-compose.yml \
               -f docker/docker-compose.prod.yml up
```

### Scaling

```bash
# Scale API service to 3 replicas
docker-compose -f docker/docker-compose.yml up -d --scale api=3
```

## Performance Optimization

### 1. Build Cache

```bash
# Use BuildKit for faster builds
DOCKER_BUILDKIT=1 docker-compose build
```

### 2. Layer Caching

- Requirements copied before code (in Dockerfile)
- Multi-stage builds reduce final image size
- `.dockerignore` excludes unnecessary files

### 3. Image Size

```bash
# Check image sizes
docker images | grep trading

# Analyze layers
docker history trading-api:latest
```

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Main README](README.md)
- [System Design](SYSTEM_DESIGN.md)

---

For development setup without Docker, see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md).
