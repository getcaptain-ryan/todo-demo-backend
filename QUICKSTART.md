# Quick Start Guide

Get up and running with the Todo Demo Backend in 5 minutes!

## Prerequisites Check

Make sure you have these installed:
- ✅ Python 3.13+
- ✅ PostgreSQL 14+
- ✅ uv (install: `pip install uv`)
- ✅ just (optional, install: `cargo install just` or see [just installation](https://github.com/casey/just#installation))

## Step-by-Step Setup

### 1. Install Dependencies (30 seconds)

```bash
uv sync
```

### 2. Configure Environment (1 minute)

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and update the DATABASE_URL
# Example: DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/todo_db
```

### 3. Create Database (30 seconds)

```bash
# Using createdb command
createdb todo_db

# OR using psql
psql -U postgres -c "CREATE DATABASE todo_db;"
```

### 4. Run Migrations (30 seconds)

```bash
just migrate-up
# or: uv run alembic upgrade head
```

### 5. Start the Server (10 seconds)

```bash
just dev
# or: uv run uvicorn app.main:app --reload
```

🎉 **Done!** Your API is now running at http://localhost:8000

## Test It Out

### Open the API Documentation
Visit http://localhost:8000/docs to see the interactive Swagger UI

### Try the API with curl

```bash
# Create a todo
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "My first todo", "description": "Test the API", "completed": false}'

# Get all todos
curl http://localhost:8000/todos

# Health check
curl http://localhost:8000/health
```

## Common Commands

```bash
# Development
just dev              # Start dev server with auto-reload
just migrate-up       # Apply database migrations
just migrate-create "message"  # Create new migration

# Database
just migrate-status   # Check migration status
just migrate-down     # Rollback last migration
just migrate-reset    # Reset database

# Maintenance
just clean           # Clean Python cache files
just info            # Show project info
```

## Troubleshooting

### Database Connection Error
- Make sure PostgreSQL is running
- Check your DATABASE_URL in `.env`
- Verify the database exists: `psql -l`

### Port Already in Use
- Change the PORT in `.env` file
- Or kill the process using port 8000

### Migration Errors
- Check database connection
- Verify you're in the project root directory
- Try: `just migrate-reset` to reset migrations

## Next Steps

1. 📖 Read the full [README.md](README.md) for detailed documentation
2. 🔍 Explore the API at http://localhost:8000/docs
3. 🛠️ Check out the 3-file database pattern in `app/database/`
4. 🚀 Deploy to Railway (see README for instructions)

## Need Help?

- Check the [README.md](README.md) for detailed documentation
- Review the code in `app/` directory
- Open an issue on GitHub

Happy coding! 🚀

