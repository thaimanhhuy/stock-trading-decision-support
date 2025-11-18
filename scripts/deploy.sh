#!/bin/bash
# Deployment script

set -e

echo "=== Stock Trading Decision Support System Deployment ==="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    exit 1
fi

# Build and start services
echo "Building Docker images..."
cd docker
docker-compose build

echo "Starting services..."
docker-compose up -d

echo "Deployment complete!"
echo "API available at: http://localhost:8000"
echo "Dashboard available at: http://localhost:8501"
