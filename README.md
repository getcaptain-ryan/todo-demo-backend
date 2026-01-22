# Todo Demo Backend

A modern FastAPI-based REST API backend with PostgreSQL database, built with Python 3.13 and managed with `uv`.

## 🚀 Features

- **FastAPI** - Modern, fast web framework for building APIs
- **PostgreSQL** - Robust relational database with async support via `asyncpg`
- **3-File Database Pattern** - Clean separation of concerns:
  - SQL files (`.sql` or `.py`) - Raw SQL queries
  - Protocol files (`.py`) - Interface definitions using Python protocols
  - Implementation files (`.py`) - Concrete implementations
- **Alembic** - Database migration management
- **CORS Support** - Configured for localhost and Railway deployment
- **uv Package Manager** - Fast, modern Python package management
- **just** - Command runner for common development tasks

## 📋 Prerequisites

- Python 3.13+
- PostgreSQL 14+
- [uv](https://github.com/astral-sh/uv) - Python package manager
- [just](https://github.com/casey/just) - Command runner (optional but recommended)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd todo-demo-backend
   ```

2. **Install dependencies**
   ```bash
   uv sync
   # or if you have just installed:
   just install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Set up the database**

   Create a PostgreSQL database:
   ```bash
   createdb todo_db
   # or using psql:
   psql -U postgres -c "CREATE DATABASE todo_db;"
   ```

5. **Run database migrations**
   ```bash
   just migrate-up
   # or:
   uv run alembic upgrade head
   ```

## 🏃 Running the Application

### Development Server (with auto-reload)
```bash
just dev
# or:
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server
```bash
just serve
# or:
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🗂️ Project Structure

```
todo-demo-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   └── todos.py           # Todo endpoints
│   ├── core/                   # Core configuration
│   │   ├── __init__.py
│   │   └── config.py          # Settings and configuration
│   ├── database/               # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py      # Database connection management
│   │   ├── sql/               # SQL queries
│   │   │   ├── __init__.py
│   │   │   └── todo_queries.py
│   │   ├── protocols/         # Interface definitions
│   │   │   ├── __init__.py
│   │   │   └── todo_protocol.py
│   │   └── implementations/   # Concrete implementations
│   │       ├── __init__.py
│   │       └── todo_repository.py
│   └── models/                # Pydantic models
│       ├── __init__.py
│       └── todo.py
├── alembic/                   # Database migrations
│   ├── versions/
│   └── env.py
├── alembic.ini               # Alembic configuration
├── justfile                  # Command runner recipes
├── pyproject.toml           # Project dependencies
├── .env.example             # Example environment variables
└── README.md

```

## 🗄️ Database Architecture

This project implements a **3-file pattern** for database operations:

### 1. SQL File (`app/database/sql/todo_queries.py`)
Contains raw SQL queries as string constants:
```python
CREATE_TODO = """
    INSERT INTO todos (title, description, completed)
    VALUES ($1, $2, $3)
    RETURNING id, title, description, completed, created_at, updated_at
"""
```

### 2. Protocol File (`app/database/protocols/todo_protocol.py`)
Defines the interface using Python protocols:
```python
class TodoRepositoryProtocol(Protocol):
    async def create(self, todo: TodoCreate) -> TodoInDB:
        ...
```

### 3. Implementation File (`app/database/implementations/todo_repository.py`)
Concrete implementation using asyncpg:
```python
class TodoRepository:
    async def create(self, todo: TodoCreate) -> TodoInDB:
        conn = await self.db.get_connection()
        # ... implementation
```

## 🔧 Common Commands (using just)

```bash
# Show all available commands
just

# Install dependencies
just install

# Add a new dependency
just add <package-name>

# Run development server
just dev

# Database migrations
just migrate-create "description"  # Create new migration
just migrate-up                    # Apply migrations
just migrate-down                  # Rollback last migration
just migrate-status                # Show current status
just migrate-history               # Show migration history
just migrate-reset                 # Reset database

# Cleanup
just clean                         # Remove Python cache files

# Project info
just info
```


## 🌐 API Endpoints

### Todos

- `GET /todos` - Get all todos
- `POST /todos` - Create a new todo
- `GET /todos/{id}` - Get a specific todo
- `PUT /todos/{id}` - Update a todo
- `DELETE /todos/{id}` - Delete a todo
- `PATCH /todos/{id}/complete` - Mark todo as completed
- `PATCH /todos/{id}/incomplete` - Mark todo as incomplete

### Health Check

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

## 🔐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECT_NAME` | Project name | `Todo Demo Backend` |
| `VERSION` | API version | `0.1.0` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@localhost:5432/todo_db` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | See `.env.example` |

## 🚢 Deployment

### Railway

1. Create a new project on [Railway](https://railway.app)
2. Add a PostgreSQL database service
3. Add your application service
4. Set environment variables:
   - `DATABASE_URL` (automatically set by Railway for PostgreSQL)
   - `ALLOWED_ORIGINS` (include your Railway app domain)
5. Deploy!

Railway will automatically detect the Python application and install dependencies.

## 🧪 Testing

To add testing support:

```bash
# Install testing dependencies
just add-dev pytest pytest-asyncio httpx

# Run tests
just test
```

## 📝 Creating a New Entity

To add a new entity (e.g., "User"), follow the 3-file pattern:

1. **Create SQL queries** (`app/database/sql/user_queries.py`)
2. **Define protocol** (`app/database/protocols/user_protocol.py`)
3. **Implement repository** (`app/database/implementations/user_repository.py`)
4. **Create Pydantic models** (`app/models/user.py`)
5. **Add API routes** (`app/api/users.py`)
6. **Create migration** (`just migrate-create "create_users_table"`)
7. **Include router in main.py**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [asyncpg](https://github.com/MagicStack/asyncpg) - Fast PostgreSQL driver
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- [just](https://github.com/casey/just) - Command runner

## 📞 Support

For issues and questions, please open an issue on GitHub.
