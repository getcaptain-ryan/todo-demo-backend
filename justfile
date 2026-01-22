# Todo Demo Backend - Justfile
# Command runner for common development tasks

# Default recipe to display help information
default:
    @just --list

# Install dependencies using uv
install:
    uv sync

# Add a new dependency
add package:
    uv add {{package}}

# Add a development dependency
add-dev package:
    uv add --dev {{package}}

# Run the development server
dev:
    uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Run the production server
serve:
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8001

# Create a new database migration
migrate-create message:
    uv run alembic revision -m "{{message}}"

# Run database migrations (upgrade to latest)
migrate-up:
    uv run alembic upgrade head

# Rollback database migration (downgrade by 1)
migrate-down:
    uv run alembic downgrade -1

# Show current migration status
migrate-status:
    uv run alembic current

# Show migration history
migrate-history:
    uv run alembic history

# Reset database (downgrade all, then upgrade all)
migrate-reset:
    uv run alembic downgrade base
    uv run alembic upgrade head

# Format code (if you add a formatter like black or ruff)
format:
    @echo "Add a formatter like 'uv add --dev ruff' and configure this command"

# Lint code (if you add a linter)
lint:
    @echo "Add a linter like 'uv add --dev ruff' and configure this command"

# Run tests (if you add pytest)
test:
    @echo "Add pytest with 'uv add --dev pytest pytest-asyncio' and configure this command"

# Clean up Python cache files
clean:
    @echo "Cleaning Python cache files..."
    @powershell -Command "Get-ChildItem -Path . -Include __pycache__,*.pyc,*.pyo,.pytest_cache,.coverage -Recurse -Force | Remove-Item -Force -Recurse"
    @echo "Clean complete!"

# Show project info
info:
    @echo "Todo Demo Backend"
    @echo "================="
    @echo "Python version: 3.13"
    @echo "Package manager: uv"
    @echo "Framework: FastAPI"
    @echo "Database: PostgreSQL (asyncpg)"
    @echo "Migrations: Alembic"

