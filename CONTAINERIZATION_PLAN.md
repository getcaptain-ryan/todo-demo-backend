# Comprehensive Containerization Plan for Todo Demo Backend

## Executive Summary

This document outlines the complete containerization strategy for the Todo Demo Backend FastAPI application, enabling Railway's auto-deploy feature with automatic database migrations, production optimizations, and seamless CI/CD integration.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Dockerfile Design](#dockerfile-design)
3. [Docker Compose Integration](#docker-compose-integration)
4. [Railway Deployment Configuration](#railway-deployment-configuration)
5. [Automatic Database Migrations](#automatic-database-migrations)
6. [Environment Configuration](#environment-configuration)
7. [Production Optimizations](#production-optimizations)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Workflow](#deployment-workflow)

---

## 1. Architecture Overview

### Current Application Stack

- **Framework**: FastAPI (Python 3.13)
- **Package Manager**: uv (fast Python package installer)
- **Database**: PostgreSQL with asyncpg driver
- **Migrations**: Alembic
- **Server**: Uvicorn ASGI server
- **Port**: 8001 (configurable via environment)

### Containerization Components

```
todo-demo-backend/
├── Dockerfile                    # Multi-stage production build
├── docker-entrypoint.sh         # Startup script with migrations
├── .dockerignore                # Build optimization
├── docker-compose.yml           # Local development environment
├── railway.toml                 # Railway platform configuration
└── RAILWAY_DEPLOYMENT.md        # Deployment documentation
```

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Railway Platform                         │
│                                                              │
│  ┌────────────────────┐         ┌──────────────────────┐   │
│  │  FastAPI Backend   │────────▶│  PostgreSQL Database │   │
│  │  (Docker Container)│         │  (Managed Service)   │   │
│  │                    │         │                      │   │
│  │  - Auto Migrations │         │  - Auto Backups      │   │
│  │  - Health Checks   │         │  - Connection Pool   │   │
│  │  - Port: Dynamic   │         │  - DATABASE_URL      │   │
│  └────────────────────┘         └──────────────────────┘   │
│           │                                                  │
│           ▼                                                  │
│  ┌────────────────────┐                                     │
│  │   Public Endpoint  │                                     │
│  │  your-app.railway  │                                     │
│  └────────────────────┘                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Dockerfile Design

### Multi-Stage Build Strategy

The Dockerfile uses a two-stage build process for optimal image size and security:

#### Stage 1: Builder (Dependency Installation)

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
```

**Purpose**: Install Python dependencies using uv package manager

**Key Features**:
- Uses official uv Docker image for fast dependency resolution
- Installs system dependencies (gcc, libpq-dev) for PostgreSQL drivers
- Creates isolated virtual environment with `uv sync --frozen --no-dev`
- Excludes development dependencies for smaller production image

**Benefits**:
- Faster builds with uv (10-100x faster than pip)
- Reproducible builds using `uv.lock`
- Smaller final image (build tools not included in production)

#### Stage 2: Runtime (Production Image)

```dockerfile
FROM python:3.13-slim-bookworm
```

**Purpose**: Create minimal production runtime environment

**Key Features**:
- Slim Python base image (smaller attack surface)
- Only runtime dependencies (libpq5 for PostgreSQL)
- Non-root user (`appuser`) for security
- Health check configuration
- Entrypoint script for migrations

**Security Measures**:
1. Non-root user execution
2. Minimal system packages
3. No build tools in production image
4. Read-only application code

### Layer Caching Optimization

The Dockerfile is optimized for Docker layer caching:

```dockerfile
# 1. Copy dependency files first (changes infrequently)
COPY pyproject.toml uv.lock ./

# 2. Install dependencies (cached unless dependencies change)
RUN uv sync --frozen --no-dev

# 3. Copy application code last (changes frequently)
COPY --chown=appuser:appuser . .
```

**Result**: Faster rebuilds when only code changes (not dependencies)

### Port Configuration

```dockerfile
EXPOSE 8001
```

- Default port: 8001 (matches current configuration)
- Railway overrides with `PORT` environment variable
- Entrypoint script uses `${PORT:-8001}` for flexibility

---

## 3. Docker Compose Integration

### Updated docker-compose.yml

The updated configuration includes both PostgreSQL and the backend service:

#### PostgreSQL Service

```yaml
postgres:
  image: postgres:16-alpine
  ports:
    - "5433:5432"
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres -d todo_db"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Features**:
- Alpine-based image (smaller size)
- Health check for service readiness
- Persistent volume for data
- Environment variables from .env file

#### Backend Service

```yaml
backend:
  build:
    context: .
    dockerfile: Dockerfile
  ports:
    - "${PORT:-8001}:8001"
  environment:
    DATABASE_URL: postgresql://postgres:password@postgres:5432/todo_db
  depends_on:
    postgres:
      condition: service_healthy
```

**Features**:
- Builds from local Dockerfile
- Waits for PostgreSQL health check before starting
- Automatic migrations on startup
- Network isolation with custom bridge network

### Local Development Workflow

```bash
# Start all services
docker-compose up

# Rebuild after code changes
docker-compose up --build

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Reset database
docker-compose down -v
docker-compose up
```

---

## 4. Railway Deployment Configuration

### railway.toml Configuration

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
```

### Railway-Specific Features

#### 1. Automatic Environment Variables

Railway automatically provides:
- `DATABASE_URL`: PostgreSQL connection string
- `PORT`: Dynamic port assignment
- `RAILWAY_ENVIRONMENT`: Deployment environment

#### 2. Health Check Integration

The `/health` endpoint is used by Railway to verify service health:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

#### 3. Auto-Deploy Trigger

Railway automatically deploys when:
- Code is pushed to the connected GitHub branch
- Environment variables are updated
- Manual deployment is triggered

### Port Handling

Railway dynamically assigns ports. The application handles this in two ways:

1. **Entrypoint Script**:
```bash
APP_PORT=${PORT:-8001}
exec uvicorn app.main:app --port "$APP_PORT"
```

2. **Settings Configuration**:
```python
# app/core/config.py
PORT: int = 8001  # Default, overridden by Railway
```

---

## 5. Automatic Database Migrations

### Migration Strategy

The `docker-entrypoint.sh` script ensures migrations run automatically on every deployment:

```bash
#!/bin/bash
set -e

# 1. Wait for database to be ready
until pg_isready -h "$DB_HOST" -p "$DB_PORT"; do
    echo "Waiting for database..."
    sleep 2
done

# 2. Run migrations
/app/.venv/bin/python -m alembic upgrade head

# 3. Start application
exec /app/.venv/bin/python -m uvicorn app.main:app
```

### Database Readiness Check

The script parses `DATABASE_URL` to extract connection details:

```bash
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
```

**Benefits**:
- Prevents connection errors during startup
- Handles Railway's PostgreSQL initialization delay
- Configurable retry logic (30 attempts, 2-second intervals)

### Migration Execution

```bash
/app/.venv/bin/python -m alembic upgrade head
```

**Features**:
- Uses virtual environment Python
- Runs all pending migrations
- Fails deployment if migrations fail (safety)
- Logs migration output for debugging

### Existing Migrations

Current migration files:
1. `a2140c338b0b_create_todos_table.py` - Initial todos table
2. `4ff83a080ba6_create_kanban_tables.py` - Kanban columns and tasks

**Migration Pattern**: 3-file database pattern
- `protocols/` - Interface definitions
- `implementations/` - Repository implementations  
- `sql/` - SQL query definitions

### Rollback Strategy

If a migration fails:

1. **Automatic**: Deployment fails, previous version continues running
2. **Manual**: Use Railway CLI to rollback:
   ```bash
   railway run alembic downgrade -1
   ```

---

## 6. Environment Configuration

### Environment Variable Hierarchy

1. **Railway Dashboard** (highest priority)
2. **railway.toml** (platform configuration)
3. **.env file** (local development)
4. **config.py defaults** (fallback values)

### Required Variables for Railway


