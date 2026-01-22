# Railway Deployment Guide

This guide explains how to deploy the Todo Demo Backend to Railway with automatic deployments and database migrations.

## Prerequisites

1. A [Railway](https://railway.app) account
2. Railway CLI installed (optional, for local testing)
3. GitHub repository connected to Railway

## Architecture Overview

The application uses:
- **FastAPI** backend with Python 3.13
- **PostgreSQL** database (Railway managed)
- **Alembic** for database migrations
- **Docker** for containerization
- **uv** package manager for fast dependency installation

## Railway Setup

### 1. Create a New Project

1. Log in to [Railway](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `todo-demo-backend` repository
5. Railway will automatically detect the Dockerfile

### 2. Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create a PostgreSQL instance
4. The `DATABASE_URL` environment variable will be automatically set

### 3. Configure Environment Variables

Railway automatically provides `DATABASE_URL` and `PORT`. Add these additional variables:

```bash
# Required Variables (set in Railway dashboard)
PROJECT_NAME=Todo Demo Backend
VERSION=0.1.0
HOST=0.0.0.0

# CORS Configuration
# Add your frontend domains (comma-separated)
ALLOWED_ORIGINS=https://your-frontend.railway.app,https://your-custom-domain.com
```

**Note:** Railway automatically sets:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - The port your application should listen on

### 4. Deploy

1. Railway will automatically deploy when you push to your main branch
2. The deployment process:
   - Builds the Docker image using the multi-stage Dockerfile
   - Waits for PostgreSQL to be ready
   - Runs Alembic migrations (`alembic upgrade head`)
   - Starts the FastAPI application with uvicorn

## Automatic Migrations

The `docker-entrypoint.sh` script automatically runs database migrations on every deployment:

```bash
# Migrations run automatically before the app starts
/app/.venv/bin/python -m alembic upgrade head
```

This ensures your database schema is always up-to-date with your code.

## Environment Variables Reference

### Automatically Set by Railway

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `PORT` | Port to listen on | `8001` |

### Required Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PROJECT_NAME` | Application name | `Todo Demo Backend` | No |
| `VERSION` | Application version | `0.1.0` | No |
| `HOST` | Host to bind to | `0.0.0.0` | No |
| `ALLOWED_ORIGINS` | CORS allowed origins | See config.py | Yes |

### CORS Configuration

For production, update `ALLOWED_ORIGINS` to include your frontend domains:

```bash
ALLOWED_ORIGINS=https://your-frontend.railway.app,https://www.yourdomain.com
```

## Health Checks

The application includes a health check endpoint at `/health`:

```bash
curl https://your-app.railway.app/health
# Response: {"status": "healthy"}
```

Railway uses this endpoint to verify the application is running correctly.

## Monitoring Deployments

### View Logs

1. Go to your Railway project
2. Click on your service
3. Navigate to the "Deployments" tab
4. Click on a deployment to view logs

### Check Migration Status

Logs will show migration output:
```
Running database migrations...
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> a2140c338b0b, create todos table
Migrations completed successfully!
```

## Troubleshooting

### Database Connection Issues

If the app can't connect to the database:

1. Verify `DATABASE_URL` is set in Railway dashboard
2. Check PostgreSQL service is running
3. Review deployment logs for connection errors

### Migration Failures

If migrations fail:

1. Check the deployment logs for Alembic errors
2. Verify migration files in `alembic/versions/` are valid
3. Manually run migrations using Railway CLI:
   ```bash
   railway run alembic upgrade head
   ```

### Port Binding Issues

Railway automatically sets the `PORT` environment variable. The application reads this in `docker-entrypoint.sh`:

```bash
APP_PORT=${PORT:-8001}
```

## Local Testing with Docker

Test the containerized application locally:

```bash
# Build the image
docker build -t todo-demo-backend .

# Run with docker-compose (includes PostgreSQL)
docker-compose up

# Access the application
curl http://localhost:8001/health
```

## CI/CD Workflow

Railway automatically deploys when you push to your repository:

1. **Push to GitHub** → Triggers Railway deployment
2. **Railway builds** → Uses Dockerfile to create image
3. **Database ready** → Waits for PostgreSQL
4. **Run migrations** → Executes `alembic upgrade head`
5. **Start app** → Launches FastAPI with uvicorn
6. **Health check** → Verifies `/health` endpoint

## Production Optimizations

The Dockerfile includes several production optimizations:

1. **Multi-stage build** - Smaller final image size
2. **Non-root user** - Enhanced security
3. **Layer caching** - Faster rebuilds
4. **Frozen dependencies** - Reproducible builds using `uv.lock`
5. **Health checks** - Automatic service monitoring

## Rollback Strategy

If a deployment fails:

1. Go to Railway dashboard
2. Navigate to "Deployments"
3. Click on a previous successful deployment
4. Click "Redeploy"

Railway will rollback to the previous version.

## Next Steps

1. Set up custom domain in Railway dashboard
2. Configure environment-specific variables
3. Set up monitoring and alerts
4. Review and optimize CORS settings
5. Consider adding Redis for caching (optional)

## Support

- Railway Documentation: https://docs.railway.app
- FastAPI Documentation: https://fastapi.tiangolo.com
- Alembic Documentation: https://alembic.sqlalchemy.org

