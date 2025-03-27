# Deployment Guide

This guide explains how to deploy the Korea Geovariable project.

## Deployment Overview

The project can be deployed in various environments:
- Local development
- Cloud servers (AWS, GCP, Azure)
- Container platforms (Docker, Kubernetes)

## Local Deployment

### 1. Prerequisites

```bash
# Install Python 3.11 or later
brew install python@3.11

# Install PostgreSQL 14 or later
brew install postgresql@14

# Install PostGIS
brew install postgis

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Environment Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
uv sync

# Set up environment variables
cp .env.template .env
# Edit .env with your configuration
```

### 3. Database Setup

```bash
# Start PostgreSQL service
brew services start postgresql@14

# Create database
createdb korea_geovariable

# Run migrations
alembic upgrade head
```

### 4. Run Application

```bash
# Run development server
python -m uvicorn app.main:app --reload

# Run tests
python -m pytest

# Build documentation
mkdocs build
```

## Docker Deployment

### 1. Dockerfile

```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    postgresql-server-dev-all \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_URL=postgresql://user:password@db:5432/korea_geovariable

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/korea_geovariable
    depends_on:
      - db
    volumes:
      - .:/app

  db:
    image: postgis/postgis:14-3.2
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=korea_geovariable
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 3. Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Run migrations
docker-compose exec app alembic upgrade head

# Check logs
docker-compose logs -f
```

## Cloud Deployment

### 1. AWS Deployment

1. **EC2 Setup**
   ```bash
   # Install dependencies
   sudo yum update -y
   sudo yum install -y postgresql14 postgresql14-server postgis31_14

   # Start PostgreSQL
   sudo systemctl start postgresql-14
   sudo systemctl enable postgresql-14

   # Install Python
   sudo yum install -y python3.11 python3.11-devel
   ```

2. **Application Setup**
   ```bash
   # Clone repository
   git clone https://github.com/yourusername/korea-geovariable.git
   cd korea-geovariable

   # Create virtual environment
   python3.11 -m venv .venv
   source .venv/bin/activate

   # Install dependencies
   uv sync

   # Set up environment variables
   cp .env.template .env
   # Edit .env
   ```

3. **Systemd Service**
   ```ini
   # /etc/systemd/system/korea-geovariable.service
   [Unit]
   Description=Korea Geovariable Application
   After=network.target

   [Service]
   User=ec2-user
   WorkingDirectory=/home/ec2-user/korea-geovariable
   Environment="PATH=/home/ec2-user/korea-geovariable/.venv/bin"
   ExecStart=/home/ec2-user/korea-geovariable/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start Service**
   ```bash
   sudo systemctl start korea-geovariable
   sudo systemctl enable korea-geovariable
   ```

### 2. GCP Deployment

1. **App Engine Setup**
   ```yaml
   # app.yaml
   runtime: python39
   env: standard
   instance_class: F1

   env_variables:
     DATABASE_URL: "postgresql://user:password@/korea_geovariable?host=/cloudsql/INSTANCE_CONNECTION_NAME"

   beta_settings:
     cloud_sql_instances: INSTANCE_CONNECTION_NAME

   handlers:
     - url: /.*
       script: auto
   ```

2. **Deploy Application**
   ```bash
   # Install Cloud SDK
   brew install --cask google-cloud-sdk

   # Initialize project
   gcloud init

   # Deploy application
   gcloud app deploy
   ```

### 3. Azure Deployment

1. **App Service Setup**
   ```bash
   # Install Azure CLI
   brew install azure-cli

   # Login to Azure
   az login

   # Create resource group
   az group create --name korea-geovariable --location eastus

   # Create App Service plan
   az appservice plan create --name korea-geovariable-plan --resource-group korea-geovariable --sku B1

   # Create web app
   az webapp create --resource-group korea-geovariable --plan korea-geovariable-plan --name korea-geovariable
   ```

2. **Deploy Application**
   ```bash
   # Deploy from local directory
   az webapp up --name korea-geovariable --resource-group korea-geovariable --runtime PYTHON:3.11
   ```

## Kubernetes Deployment

### 1. Kubernetes Manifests

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: korea-geovariable
spec:
  replicas: 3
  selector:
    matchLabels:
      app: korea-geovariable
  template:
    metadata:
      labels:
        app: korea-geovariable
    spec:
      containers:
      - name: korea-geovariable
        image: korea-geovariable:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: korea-geovariable-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: korea-geovariable
spec:
  selector:
    app: korea-geovariable
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 2. Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services
```

## Monitoring and Logging

### 1. Application Monitoring

```python
# app/monitoring.py
from prometheus_client import Counter, Histogram
import time

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

# Use metrics in application
@app.middleware("http")
async def monitor_requests(request, call_next):
    REQUEST_COUNT.inc()
    start_time = time.time()
    response = await call_next(request)
    REQUEST_LATENCY.observe(time.time() - start_time)
    return response
```

### 2. Logging

```python
# app/logging.py
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

# Use logging in application
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Hello World"}
```

## Backup and Recovery

### 1. Database Backup

```bash
# Create backup
pg_dump -U postgres -d korea_geovariable > backup.sql

# Restore backup
psql -U postgres -d korea_geovariable < backup.sql
```

### 2. Application Backup

```bash
# Backup application files
tar -czf app_backup.tar.gz app/ tests/ docs/

# Restore application files
tar -xzf app_backup.tar.gz
```

## Security

### 1. Environment Variables

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/korea_geovariable
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,example.com
```

### 2. SSL/TLS

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

# Enable HTTPS redirect
app.add_middleware(HTTPSRedirectMiddleware)
```

## Next Steps

1. Review the [Contributing Guide](contributing.md)
2. Check [Code Style Guide](code-style.md)
3. Review [Architecture Guide](architecture.md)
