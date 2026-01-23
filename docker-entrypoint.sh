#!/bin/bash
set -e

echo "Starting Todo Demo Backend..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
max_retries=30
retry_count=0

# Extract database connection details from DATABASE_URL
# Format: postgresql://user:password@host:port/dbname
if [ -n "$DATABASE_URL" ]; then
    # Parse DATABASE_URL to extract host and port
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')

    echo "Database host: $DB_HOST"
    echo "Database port: $DB_PORT"

    # Wait for PostgreSQL to be ready
    until pg_isready -h "$DB_HOST" -p "$DB_PORT" > /dev/null 2>&1 || [ $retry_count -eq $max_retries ]; do
        retry_count=$((retry_count + 1))
        echo "Waiting for database... (attempt $retry_count/$max_retries)"
        sleep 2
    done

    if [ $retry_count -eq $max_retries ]; then
        echo "Warning: Could not connect to database after $max_retries attempts. Proceeding anyway..."
    else
        echo "Database is ready!"
    fi
else
    echo "Warning: DATABASE_URL not set. Skipping database readiness check."
fi

# Run database migrations
echo "Running database migrations..."
/app/.venv/bin/python -m alembic upgrade head

if [ $? -eq 0 ]; then
    echo "Migrations completed successfully!"
else
    echo "Error: Migrations failed!"
    exit 1
fi

# Get port from environment variable (Railway sets PORT)
# Default to 8001 if not set
APP_PORT=${PORT:-8001}

echo "Starting FastAPI application on port $APP_PORT..."

# Start the application using uvicorn
exec /app/.venv/bin/python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$APP_PORT" \
    --workers 1 \
    --log-level info


