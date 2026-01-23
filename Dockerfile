# Multi-stage Dockerfile for FastAPI application using uv package manager
# Optimized for Railway deployment with automatic migrations

# Stage 1: Builder - Install dependencies
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies required for PostgreSQL drivers
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
# --no-dev excludes development dependencies
# --frozen ensures reproducible builds using uv.lock
RUN uv sync --frozen --no-dev

# Stage 2: Runtime - Create production image
FROM python:3.13-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Disable uv cache in production
    UV_NO_CACHE=1 \
    # Python path
    PYTHONPATH=/app

# Install runtime dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq5 \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy Python environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Copy startup script
COPY --chown=appuser:appuser docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port (Railway will override with PORT env var)
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8001}/health || exit 1

# Use entrypoint script for migrations and startup
ENTRYPOINT ["/app/docker-entrypoint.sh"]

