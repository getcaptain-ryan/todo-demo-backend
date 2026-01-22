# Kanban Board CRUD Implementation Plan

## Overview
This document provides a comprehensive implementation plan for adding Users, Columns, and Tasks entities to the FastAPI backend following the existing 3-file database pattern.

---

## Table of Contents
1. [Database Schema Design](#database-schema-design)
2. [File Structure](#file-structure)
3. [Implementation Order](#implementation-order)
4. [Detailed Implementation Guide](#detailed-implementation-guide)
5. [API Endpoint Specifications](#api-endpoint-specifications)
6. [Migration Strategy](#migration-strategy)
7. [Code Examples](#code-examples)

---

## Database Schema Design

### Entity Relationship Diagram
```
┌─────────────────┐
│     Users       │
│─────────────────│
│ id (PK)         │
│ name            │
│ email (UNIQUE)  │
│ avatar_url      │
│ created_at      │
└─────────────────┘

┌─────────────────┐
│    Columns      │
│─────────────────│
│ id (PK)         │
│ title           │
│ order           │
│ created_at      │
└─────────────────┘

┌─────────────────┐
│     Tasks       │
│─────────────────│
│ id (PK)         │
│ title           │
│ description     │
│ column_id (FK)  │──┐
│ order           │  │
│ created_at      │  │
└─────────────────┘  │
                     │
                     ▼
              ┌─────────────┐
              │   Columns   │
              └─────────────┘
```

### Table Definitions

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    avatar_url TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_users_id ON users(id);
CREATE INDEX ix_users_email ON users(email);
```

#### Columns Table
```sql
CREATE TABLE columns (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    "order" INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_column_order UNIQUE ("order")
);

CREATE INDEX ix_columns_id ON columns(id);
CREATE INDEX ix_columns_order ON columns("order");
```

#### Tasks Table
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    column_id INTEGER NOT NULL REFERENCES columns(id) ON DELETE CASCADE,
    "order" INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_task_order_per_column UNIQUE (column_id, "order")
);

CREATE INDEX ix_tasks_id ON tasks(id);
CREATE INDEX ix_tasks_column_id ON tasks(column_id);
CREATE INDEX ix_tasks_order ON tasks("order");
```

**Key Design Decisions:**
- `order` is quoted as `"order"` because it's a reserved SQL keyword
- Columns have globally unique order (UNIQUE constraint on order)
- Tasks have unique order per column (composite UNIQUE constraint on column_id, order)
- Tasks cascade delete when column is deleted (ON DELETE CASCADE)
- All timestamps use server-side NOW() for consistency

---

## File Structure

```
app/
├── models/
│   ├── user.py          # NEW: User Pydantic models
│   ├── column.py        # NEW: Column Pydantic models
│   └── task.py          # NEW: Task Pydantic models
├── database/
│   ├── sql/
│   │   ├── user_queries.py      # NEW: User SQL queries
│   │   ├── column_queries.py    # NEW: Column SQL queries
│   │   └── task_queries.py      # NEW: Task SQL queries
│   ├── protocols/
│   │   ├── user_protocol.py     # NEW: User repository protocol
│   │   ├── column_protocol.py   # NEW: Column repository protocol
│   │   └── task_protocol.py     # NEW: Task repository protocol
│   └── implementations/
│       ├── user_repository.py   # NEW: User repository implementation
│       ├── column_repository.py # NEW: Column repository implementation
│       └── task_repository.py   # NEW: Task repository implementation
├── api/
│   ├── users.py         # NEW: User API routes
│   ├── columns.py       # NEW: Column API routes
│   └── tasks.py         # NEW: Task API routes
└── main.py              # MODIFY: Include new routers

alembic/versions/
└── XXXXX_create_kanban_tables.py  # NEW: Migration file
```

---

## Implementation Order

Follow this order to minimize dependencies and enable incremental testing:

### Phase 1: Users Entity (Independent)
1. Create Pydantic models (`app/models/user.py`)
2. Create SQL queries (`app/database/sql/user_queries.py`)
3. Create protocol (`app/database/protocols/user_protocol.py`)
4. Create repository (`app/database/implementations/user_repository.py`)
5. Create API routes (`app/api/users.py`)
6. Create migration for users table
7. Update `app/main.py` to include users router
8. Test users endpoints

### Phase 2: Columns Entity (Independent)
1. Create Pydantic models (`app/models/column.py`)
2. Create SQL queries (`app/database/sql/column_queries.py`)
3. Create protocol (`app/database/protocols/column_protocol.py`)
4. Create repository (`app/database/implementations/column_repository.py`)
5. Create API routes (`app/api/columns.py`)
6. Create migration for columns table
7. Update `app/main.py` to include columns router
8. Test columns endpoints

### Phase 3: Tasks Entity (Depends on Columns)
1. Create Pydantic models (`app/models/task.py`)
2. Create SQL queries (`app/database/sql/task_queries.py`)
3. Create protocol (`app/database/protocols/task_protocol.py`)
4. Create repository (`app/database/implementations/task_repository.py`)
5. Create API routes (`app/api/tasks.py`)
6. Create migration for tasks table
7. Update `app/main.py` to include tasks router
8. Test tasks endpoints

**Note:** Users and Columns can be implemented in parallel. Tasks must be implemented after Columns due to foreign key dependency.

---

## Detailed Implementation Guide

### 1. Users Entity Implementation

#### 1.1 Pydantic Models (`app/models/user.py`)

```python
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base User model"""
    name: str = Field(..., min_length=1, max_length=200, description="User's full name")
    email: EmailStr = Field(..., description="User's email address (must be unique)")
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL to user's avatar image")


class UserCreate(UserBase):
    """Model for creating a new User"""
    pass


class UserUpdate(BaseModel):
    """Model for updating a User"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserInDB(UserBase):
    """Model for User in database"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserInDB):
    """Model for User API response"""
    pass
```

**Key Points:**
- Uses `EmailStr` from Pydantic for email validation (requires `email-validator` package)
- `model_config` replaces the old `Config` class (Pydantic v2 syntax)
- All optional fields use `Optional[...]` type hints
- Field descriptions help with auto-generated API docs

#### 1.2 SQL Queries (`app/database/sql/user_queries.py`)

```python
"""SQL queries for User entity"""

# Create a new user
CREATE_USER = """
    INSERT INTO users (name, email, avatar_url)
    VALUES ($1, $2, $3)
    RETURNING id, name, email, avatar_url, created_at
"""

# Get all users
GET_ALL_USERS = """
    SELECT id, name, email, avatar_url, created_at
    FROM users
    ORDER BY created_at DESC
"""

# Get a single user by ID
GET_USER_BY_ID = """
    SELECT id, name, email, avatar_url, created_at
    FROM users
    WHERE id = $1
"""

# Get a user by email
GET_USER_BY_EMAIL = """
    SELECT id, name, email, avatar_url, created_at
    FROM users
    WHERE email = $2
"""

# Update a user
UPDATE_USER = """
    UPDATE users
    SET name = $2, email = $3, avatar_url = $4
    WHERE id = $1
    RETURNING id, name, email, avatar_url, created_at
"""

# Delete a user
DELETE_USER = """
    DELETE FROM users
    WHERE id = $1
    RETURNING id
"""
```

**Key Points:**
- All queries use parameterized queries ($1, $2, etc.) to prevent SQL injection
- RETURNING clause ensures we get the created/updated data back
- Consistent column selection across all queries

#### 1.3 Protocol (`app/database/protocols/user_protocol.py`)

```python
from typing import Protocol, List, Optional
from app.models.user import UserCreate, UserUpdate, UserInDB


class UserRepositoryProtocol(Protocol):
    """Protocol defining the interface for User repository operations"""

    async def create(self, user: UserCreate) -> UserInDB:
        """Create a new user"""
        ...

    async def get_all(self) -> List[UserInDB]:
        """Get all users"""
        ...

    async def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        """Get a user by ID"""
        ...

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        """Get a user by email"""
        ...

    async def update(self, user_id: int, user: UserUpdate) -> Optional[UserInDB]:
        """Update a user"""
        ...

    async def delete(self, user_id: int) -> bool:
        """Delete a user"""
        ...
```

#### 1.4 Repository Implementation (`app/database/implementations/user_repository.py`)

```python
from typing import List, Optional
import asyncpg
from app.models.user import UserCreate, UserUpdate, UserInDB
from app.database.sql import user_queries
from app.database.connection import db


class UserRepository:
    """Implementation of User repository using asyncpg"""

    def __init__(self):
        self.db = db

    async def create(self, user: UserCreate) -> UserInDB:
        """Create a new user"""
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow(
                user_queries.CREATE_USER,
                user.name,
                user.email,
                user.avatar_url
            )
            return UserInDB(**dict(row))
        finally:
            await self.db.release_connection(conn)

    async def get_all(self) -> List[UserInDB]:
        """Get all users"""
        conn = await self.db.get_connection()
        try:
            rows = await conn.fetch(user_queries.GET_ALL_USERS)
            return [UserInDB(**dict(row)) for row in rows]
        finally:
            await self.db.release_connection(conn)

    async def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        """Get a user by ID"""
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow(user_queries.GET_USER_BY_ID, user_id)
            return UserInDB(**dict(row)) if row else None
        finally:
            await self.db.release_connection(conn)

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        """Get a user by email"""
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow(user_queries.GET_USER_BY_EMAIL, email)
            return UserInDB(**dict(row)) if row else None
        finally:
            await self.db.release_connection(conn)

    async def update(self, user_id: int, user: UserUpdate) -> Optional[UserInDB]:
        """Update a user"""
        # First get the existing user
        existing = await self.get_by_id(user_id)
        if not existing:
            return None

        # Merge updates with existing data
        update_data = user.model_dump(exclude_unset=True)
        name = update_data.get("name", existing.name)
        email = update_data.get("email", existing.email)
        avatar_url = update_data.get("avatar_url", existing.avatar_url)

        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow(
                user_queries.UPDATE_USER,
                user_id,
                name,
                email,
                avatar_url
            )
            return UserInDB(**dict(row)) if row else None
        finally:
            await self.db.release_connection(conn)

    async def delete(self, user_id: int) -> bool:
        """Delete a user"""
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow(user_queries.DELETE_USER, user_id)
            return row is not None
        finally:
            await self.db.release_connection(conn)
```

**Key Points:**
- Always use try/finally to ensure connections are released
- Use `model_dump(exclude_unset=True)` to only update provided fields
- Return None for not found cases, let API layer handle 404s


#### 1.5 API Routes (`app/api/users.py`)

```python
from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.user import UserCreate, UserUpdate, UserResponse
from app.database.implementations.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["users"])
user_repo = UserRepository()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Create a new user"""
    # Check if email already exists
    existing = await user_repo.get_by_email(user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {user.email} already exists"
        )
    return await user_repo.create(user)


@router.get("/", response_model=List[UserResponse])
async def get_all_users():
    """Get all users"""
    return await user_repo.get_all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get a user by ID"""
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate):
    """Update a user"""
    # If email is being updated, check for conflicts
    if user.email:
        existing = await user_repo.get_by_email(user.email)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email {user.email} already exists"
            )

    updated_user = await user_repo.update(user_id, user)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """Delete a user"""
    deleted = await user_repo.delete(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
```

**Key Points:**
- Email uniqueness validation at API level (409 Conflict)
- Proper HTTP status codes (201 Created, 204 No Content, 404 Not Found, 409 Conflict)
- Clear error messages for debugging

---

### 2. Columns Entity Implementation

#### 2.1 Pydantic Models (`app/models/column.py`)

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ColumnBase(BaseModel):
    """Base Column model"""
    title: str = Field(..., min_length=1, max_length=200, description="Column title")
    order: int = Field(..., ge=0, description="Display order (0-indexed)")


class ColumnCreate(ColumnBase):
    """Model for creating a new Column"""
    pass


class ColumnUpdate(BaseModel):
    """Model for updating a Column"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    order: Optional[int] = Field(None, ge=0)


class ColumnInDB(ColumnBase):
    """Model for Column in database"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ColumnResponse(ColumnInDB):
    """Model for Column API response"""
    pass


class ColumnReorder(BaseModel):
    """Model for reordering columns"""
    column_id: int = Field(..., description="ID of column to move")
    new_order: int = Field(..., ge=0, description="New order position")
```

**Key Points:**
- `order` field uses `ge=0` (greater than or equal to 0) validation
- Separate `ColumnReorder` model for reordering operations
- Order is 0-indexed for easier array manipulation in frontend

#### 2.2 SQL Queries (`app/database/sql/column_queries.py`)

```python
"""SQL queries for Column entity"""

# Create a new column
CREATE_COLUMN = """
    INSERT INTO columns (title, "order")
    VALUES ($1, $2)
    RETURNING id, title, "order", created_at
"""

# Get all columns
GET_ALL_COLUMNS = """
    SELECT id, title, "order", created_at
    FROM columns
    ORDER BY "order" ASC
"""

# Get a single column by ID
GET_COLUMN_BY_ID = """
    SELECT id, title, "order", created_at
    FROM columns
    WHERE id = $1
"""

# Update a column
UPDATE_COLUMN = """
    UPDATE columns
    SET title = $2, "order" = $3
    WHERE id = $1
    RETURNING id, title, "order", created_at
"""

# Delete a column
DELETE_COLUMN = """
    DELETE FROM columns
    WHERE id = $1
    RETURNING id
"""

# Get max order value
GET_MAX_ORDER = """
    SELECT COALESCE(MAX("order"), -1) as max_order
    FROM columns
"""

# Shift columns order up (when inserting)
SHIFT_COLUMNS_UP = """
    UPDATE columns
    SET "order" = "order" + 1
    WHERE "order" >= $1
"""

# Shift columns order down (when deleting)
SHIFT_COLUMNS_DOWN = """
    UPDATE columns
    SET "order" = "order" - 1
    WHERE "order" > $1
"""

# Reorder column (complex operation)
REORDER_COLUMN = """
    WITH current_pos AS (
        SELECT "order" as old_order FROM columns WHERE id = $1
    )
    UPDATE columns
    SET "order" = CASE
        WHEN id = $1 THEN $2
        WHEN $2 < (SELECT old_order FROM current_pos)
            AND "order" >= $2
            AND "order" < (SELECT old_order FROM current_pos)
            THEN "order" + 1
        WHEN $2 > (SELECT old_order FROM current_pos)
            AND "order" <= $2
            AND "order" > (SELECT old_order FROM current_pos)
            THEN "order" - 1
        ELSE "order"
    END
    WHERE "order" BETWEEN
        LEAST($2, (SELECT old_order FROM current_pos))
        AND GREATEST($2, (SELECT old_order FROM current_pos))
    RETURNING id, title, "order", created_at
"""
```

**Key Points:**
- `"order"` is quoted because it's a SQL reserved keyword
- Helper queries for order management (shift up/down)
- Complex REORDER query handles moving columns between positions
- GET_MAX_ORDER returns -1 if no columns exist (for easy +1 logic)


#### 2.3 Protocol (`app/database/protocols/column_protocol.py`)

```python
from typing import Protocol, List, Optional
from app.models.column import ColumnCreate, ColumnUpdate, ColumnInDB


class ColumnRepositoryProtocol(Protocol):
    """Protocol defining the interface for Column repository operations"""

    async def create(self, column: ColumnCreate) -> ColumnInDB:
        """Create a new column"""
        ...

    async def get_all(self) -> List[ColumnInDB]:
        """Get all columns ordered by position"""
        ...

    async def get_by_id(self, column_id: int) -> Optional[ColumnInDB]:
        """Get a column by ID"""
        ...

    async def update(self, column_id: int, column: ColumnUpdate) -> Optional[ColumnInDB]:
        """Update a column"""
        ...

    async def delete(self, column_id: int) -> bool:
        """Delete a column and reorder remaining columns"""
        ...

    async def reorder(self, column_id: int, new_order: int) -> Optional[ColumnInDB]:
        """Reorder a column to a new position"""
        ...
```

#### 2.4 Repository Implementation (`app/database/implementations/column_repository.py`)

```python
from typing import List, Optional
import asyncpg
from app.models.column import ColumnCreate, ColumnUpdate, ColumnInDB
from app.database.sql import column_queries
from app.database.connection import db


class ColumnRepository:
    """Implementation of Column repository using asyncpg"""

    def __init__(self):
        self.db = db

    async def create(self, column: ColumnCreate) -> ColumnInDB:
        """Create a new column"""
        conn = await self.db.get_connection()
        try:
            # If order conflicts, shift existing columns
            await conn.execute(column_queries.SHIFT_COLUMNS_UP, column.order)

            row = await conn.fetchrow(
                column_queries.CREATE_COLUMN,
                column.title,
                column.order
            )
            return ColumnInDB(**dict(row))
        finally:
            await self.db.release_connection(conn)

    async def get_all(self) -> List[ColumnInDB]:
        """Get all columns ordered by position"""
        conn = await self.db.get_connection()
        try:
            rows = await conn.fetch(column_queries.GET_ALL_COLUMNS)
            return [ColumnInDB(**dict(row)) for row in rows]
        finally:
            await self.db.release_connection(conn)

    async def get_by_id(self, column_id: int) -> Optional[ColumnInDB]:
        """Get a column by ID"""
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow(column_queries.GET_COLUMN_BY_ID, column_id)
            return ColumnInDB(**dict(row)) if row else None
        finally:
            await self.db.release_connection(conn)

    async def update(self, column_id: int, column: ColumnUpdate) -> Optional[ColumnInDB]:
        """Update a column"""
        existing = await self.get_by_id(column_id)
        if not existing:
            return None

        update_data = column.model_dump(exclude_unset=True)
        title = update_data.get("title", existing.title)
        order = update_data.get("order", existing.order)

        conn = await self.db.get_connection()
        try:
            # If order is changing, use reorder logic
            if order != existing.order:
                return await self.reorder(column_id, order)

            row = await conn.fetchrow(
                column_queries.UPDATE_COLUMN,
                column_id,
                title,
                order
            )
            return ColumnInDB(**dict(row)) if row else None
        finally:
            await self.db.release_connection(conn)

    async def delete(self, column_id: int) -> bool:
        """Delete a column and reorder remaining columns"""
        conn = await self.db.get_connection()
        try:
            # Get the column's order before deleting
            existing = await self.get_by_id(column_id)
            if not existing:
                return False

            # Delete the column
            row = await conn.fetchrow(column_queries.DELETE_COLUMN, column_id)
            if not row:
                return False

            # Shift down columns that were after this one
            await conn.execute(column_queries.SHIFT_COLUMNS_DOWN, existing.order)
            return True
        finally:
            await self.db.release_connection(conn)

    async def reorder(self, column_id: int, new_order: int) -> Optional[ColumnInDB]:
        """Reorder a column to a new position"""
        conn = await self.db.get_connection()
        try:
            rows = await conn.fetch(
                column_queries.REORDER_COLUMN,
                column_id,
                new_order
            )
            # Find and return the reordered column
            for row in rows:
                if row['id'] == column_id:
                    return ColumnInDB(**dict(row))
            return None
        finally:
            await self.db.release_connection(conn)
```

**Key Points:**
- Create operation automatically shifts existing columns if order conflicts
- Delete operation automatically reorders remaining columns
- Update delegates to reorder if order is changing
- Reorder uses complex SQL to atomically update all affected columns

#### 2.5 API Routes (`app/api/columns.py`)

```python
from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.column import ColumnCreate, ColumnUpdate, ColumnResponse, ColumnReorder
from app.database.implementations.column_repository import ColumnRepository

router = APIRouter(prefix="/columns", tags=["columns"])
column_repo = ColumnRepository()


@router.post("/", response_model=ColumnResponse, status_code=status.HTTP_201_CREATED)
async def create_column(column: ColumnCreate):
    """Create a new column"""
    return await column_repo.create(column)


@router.get("/", response_model=List[ColumnResponse])
async def get_all_columns():
    """Get all columns ordered by position"""
    return await column_repo.get_all()


@router.get("/{column_id}", response_model=ColumnResponse)
async def get_column(column_id: int):
    """Get a column by ID"""
    column = await column_repo.get_by_id(column_id)
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Column with id {column_id} not found"
        )
    return column


@router.put("/{column_id}", response_model=ColumnResponse)
async def update_column(column_id: int, column: ColumnUpdate):
    """Update a column"""
    updated_column = await column_repo.update(column_id, column)
    if not updated_column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Column with id {column_id} not found"
        )
    return updated_column


@router.delete("/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(column_id: int):
    """Delete a column (will also delete all tasks in this column)"""
    deleted = await column_repo.delete(column_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Column with id {column_id} not found"
        )


@router.patch("/{column_id}/reorder", response_model=ColumnResponse)
async def reorder_column(column_id: int, reorder: ColumnReorder):
    """Reorder a column to a new position"""
    if reorder.column_id != column_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Column ID in path must match column_id in request body"
        )

    reordered = await column_repo.reorder(column_id, reorder.new_order)
    if not reordered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Column with id {column_id} not found"
        )
    return reordered
```

**Key Points:**
- Dedicated reorder endpoint for clarity
- Delete endpoint warns about cascade deletion of tasks
- Validation ensures path and body column IDs match

---

### 3. Tasks Entity Implementation

#### 3.1 Pydantic Models (`app/models/task.py`)

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class TaskBase(BaseModel):
    """Base Task model"""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    column_id: int = Field(..., gt=0, description="ID of the column this task belongs to")
    order: int = Field(..., ge=0, description="Display order within column (0-indexed)")


class TaskCreate(TaskBase):
    """Model for creating a new Task"""
    pass


class TaskUpdate(BaseModel):
    """Model for updating a Task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    order: Optional[int] = Field(None, ge=0)


class TaskInDB(TaskBase):
    """Model for Task in database"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(TaskInDB):
    """Model for Task API response"""
    pass


class TaskMove(BaseModel):
    """Model for moving a task to a different column"""
    task_id: int = Field(..., description="ID of task to move")
    target_column_id: int = Field(..., gt=0, description="ID of target column")
    new_order: int = Field(..., ge=0, description="Order position in target column")


class TaskReorder(BaseModel):
    """Model for reordering a task within the same column"""
    task_id: int = Field(..., description="ID of task to reorder")
    new_order: int = Field(..., ge=0, description="New order position")
```

**Key Points:**
- `column_id` uses `gt=0` (greater than 0) validation
- Separate models for move (between columns) and reorder (within column)
- Description has larger max length (2000) than title

#### 3.2 SQL Queries (`app/database/sql/task_queries.py`)

```python
"""SQL queries for Task entity"""

# Create a new task
CREATE_TASK = """
    INSERT INTO tasks (title, description, column_id, "order")
    VALUES ($1, $2, $3, $4)
    RETURNING id, title, description, column_id, "order", created_at
"""

# Get all tasks
GET_ALL_TASKS = """
    SELECT id, title, description, column_id, "order", created_at
    FROM tasks
    ORDER BY column_id ASC, "order" ASC
"""

# Get a single task by ID
GET_TASK_BY_ID = """
    SELECT id, title, description, column_id, "order", created_at
    FROM tasks
    WHERE id = $1
"""

# Get all tasks in a specific column
GET_TASKS_BY_COLUMN = """
    SELECT id, title, description, column_id, "order", created_at
    FROM tasks
    WHERE column_id = $1
    ORDER BY "order" ASC
"""

# Update a task
UPDATE_TASK = """
    UPDATE tasks
    SET title = $2, description = $3, "order" = $4
    WHERE id = $1
    RETURNING id, title, description, column_id, "order", created_at
"""

# Delete a task
DELETE_TASK = """
    DELETE FROM tasks
    WHERE id = $1
    RETURNING id, column_id, "order"
"""

# Shift tasks order up within a column (when inserting)
SHIFT_TASKS_UP_IN_COLUMN = """
    UPDATE tasks
    SET "order" = "order" + 1
    WHERE column_id = $1 AND "order" >= $2
"""

# Shift tasks order down within a column (when deleting)
SHIFT_TASKS_DOWN_IN_COLUMN = """
    UPDATE tasks
    SET "order" = "order" - 1
    WHERE column_id = $1 AND "order" > $2
"""

# Reorder task within same column
REORDER_TASK_IN_COLUMN = """
    WITH current_pos AS (
        SELECT "order" as old_order, column_id FROM tasks WHERE id = $1
    )
    UPDATE tasks
    SET "order" = CASE
        WHEN id = $1 THEN $2
        WHEN $2 < (SELECT old_order FROM current_pos)
            AND "order" >= $2
            AND "order" < (SELECT old_order FROM current_pos)
            THEN "order" + 1
        WHEN $2 > (SELECT old_order FROM current_pos)
            AND "order" <= $2
            AND "order" > (SELECT old_order FROM current_pos)
            THEN "order" - 1
        ELSE "order"
    END
    WHERE column_id = (SELECT column_id FROM current_pos)
        AND "order" BETWEEN
            LEAST($2, (SELECT old_order FROM current_pos))
            AND GREATEST($2, (SELECT old_order FROM current_pos))
    RETURNING id, title, description, column_id, "order", created_at
"""

# Move task to different column
MOVE_TASK_TO_COLUMN = """
    WITH task_info AS (
        SELECT column_id as old_column_id, "order" as old_order
        FROM tasks
        WHERE id = $1
    )
    UPDATE tasks
    SET column_id = $2, "order" = $3
    WHERE id = $1
    RETURNING id, title, description, column_id, "order", created_at
"""

# Get max order in a column
GET_MAX_ORDER_IN_COLUMN = """
    SELECT COALESCE(MAX("order"), -1) as max_order
    FROM tasks
    WHERE column_id = $1
"""
```

**Key Points:**
- Separate queries for reordering within column vs moving between columns
- Helper queries for shifting tasks within a specific column
- GET_MAX_ORDER_IN_COLUMN helps with appending tasks to end of column

#### 3.3 Protocol (`app/database/protocols/task_protocol.py`)

```python
from typing import Protocol, List, Optional
from app.models.task import TaskCreate, TaskUpdate, TaskInDB


class TaskRepositoryProtocol(Protocol):
    """Protocol defining the interface for Task repository operations"""

    async def create(self, task: TaskCreate) -> TaskInDB:
        """Create a new task"""
        ...

    async def get_all(self) -> List[TaskInDB]:
        """Get all tasks"""
        ...

    async def get_by_id(self, task_id: int) -> Optional[TaskInDB]:
        """Get a task by ID"""
        ...

    async def get_by_column(self, column_id: int) -> List[TaskInDB]:
        """Get all tasks in a specific column"""
        ...

    async def update(self, task_id: int, task: TaskUpdate) -> Optional[TaskInDB]:
        """Update a task"""
        ...

    async def delete(self, task_id: int) -> bool:
        """Delete a task"""
        ...

    async def move_to_column(self, task_id: int, target_column_id: int, new_order: int) -> Optional[TaskInDB]:
        """Move a task to a different column"""
        ...

    async def reorder_in_column(self, task_id: int, new_order: int) -> Optional[TaskInDB]:
        """Reorder a task within its current column"""
        ...
```

---

## API Endpoint Specifications

### Users Endpoints

| Method | Endpoint | Description | Request Body | Response | Status Codes |
|--------|----------|-------------|--------------|----------|--------------|
| POST | `/users` | Create user | `UserCreate` | `UserResponse` | 201, 409 |
| GET | `/users` | Get all users | - | `List[UserResponse]` | 200 |
| GET | `/users/{id}` | Get user by ID | - | `UserResponse` | 200, 404 |
| PUT | `/users/{id}` | Update user | `UserUpdate` | `UserResponse` | 200, 404, 409 |
| DELETE | `/users/{id}` | Delete user | - | - | 204, 404 |

### Columns Endpoints

| Method | Endpoint | Description | Request Body | Response | Status Codes |
|--------|----------|-------------|--------------|----------|--------------|
| POST | `/columns` | Create column | `ColumnCreate` | `ColumnResponse` | 201 |
| GET | `/columns` | Get all columns | - | `List[ColumnResponse]` | 200 |
| GET | `/columns/{id}` | Get column by ID | - | `ColumnResponse` | 200, 404 |
| PUT | `/columns/{id}` | Update column | `ColumnUpdate` | `ColumnResponse` | 200, 404 |
| DELETE | `/columns/{id}` | Delete column | - | - | 204, 404 |
| PATCH | `/columns/{id}/reorder` | Reorder column | `ColumnReorder` | `ColumnResponse` | 200, 404 |

### Tasks Endpoints

| Method | Endpoint | Description | Request Body | Response | Status Codes |
|--------|----------|-------------|--------------|----------|--------------|
| POST | `/tasks` | Create task | `TaskCreate` | `TaskResponse` | 201, 404 |
| GET | `/tasks` | Get all tasks | - | `List[TaskResponse]` | 200 |
| GET | `/tasks/{id}` | Get task by ID | - | `TaskResponse` | 200, 404 |
| GET | `/columns/{id}/tasks` | Get tasks by column | - | `List[TaskResponse]` | 200, 404 |
| PUT | `/tasks/{id}` | Update task | `TaskUpdate` | `TaskResponse` | 200, 404 |
| DELETE | `/tasks/{id}` | Delete task | - | - | 204, 404 |
| PATCH | `/tasks/{id}/move` | Move to column | `TaskMove` | `TaskResponse` | 200, 404 |
| PATCH | `/tasks/{id}/reorder` | Reorder in column | `TaskReorder` | `TaskResponse` | 200, 404 |

**Status Code Legend:**
- 200: Success
- 201: Created
- 204: No Content (successful deletion)
- 400: Bad Request
- 404: Not Found
- 409: Conflict (duplicate email, etc.)

---

## Migration Strategy


### Approach: Single Migration vs Multiple Migrations

**Recommended: Single Migration File**

Create one migration file that creates all three tables. This ensures:
- Atomic operation (all tables created together or none)
- Proper foreign key relationships from the start
- Simpler rollback if needed
- Clearer dependency management

### Migration File Example

**File:** `alembic/versions/XXXXX_create_kanban_tables.py`

```python
"""create_kanban_tables

Revision ID: XXXXX
Revises: a2140c338b0b
Create Date: 2026-01-XX XX:XX:XX.XXXXXX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'XXXXX'
down_revision: Union[str, Sequence[str], None] = 'a2140c338b0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'])

    # Create columns table
    op.create_table(
        'columns',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order', name='uq_columns_order')
    )
    op.create_index('ix_columns_id', 'columns', ['id'])
    op.create_index('ix_columns_order', 'columns', ['order'])

    # Create tasks table (depends on columns)
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('column_id', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['column_id'], ['columns.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('column_id', 'order', name='uq_tasks_column_order')
    )
    op.create_index('ix_tasks_id', 'tasks', ['id'])
    op.create_index('ix_tasks_column_id', 'tasks', ['column_id'])
    op.create_index('ix_tasks_order', 'tasks', ['order'])


def downgrade() -> None:
    """Downgrade schema."""

    # Drop in reverse order (tasks first due to foreign key)
    op.drop_index('ix_tasks_order', table_name='tasks')
    op.drop_index('ix_tasks_column_id', table_name='tasks')
    op.drop_index('ix_tasks_id', table_name='tasks')
    op.drop_table('tasks')

    op.drop_index('ix_columns_order', table_name='columns')
    op.drop_index('ix_columns_id', table_name='columns')
    op.drop_table('columns')

    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
```

### Migration Commands

```bash
# Create the migration file
just migrate-create "create_kanban_tables"

# Edit the generated file with the above content

# Run the migration
just migrate-up

# If needed, rollback
just migrate-down
```

---

## Code Examples

### Example: Updating main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.database.connection import db
from app.api import todos, users, columns, tasks  # Add new imports


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    await db.connect()
    yield
    # Shutdown
    await db.disconnect()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Todo Demo Backend API",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(todos.router)
app.include_router(users.router)      # NEW
app.include_router(columns.router)    # NEW
app.include_router(tasks.router)      # NEW


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Todo Demo Backend API"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
```

### Example: Task Repository Implementation (Partial)

```python
from typing import List, Optional
import asyncpg
from app.models.task import TaskCreate, TaskUpdate, TaskInDB
from app.database.sql import task_queries
from app.database.connection import db


class TaskRepository:
    """Implementation of Task repository using asyncpg"""

    def __init__(self):
        self.db = db

    async def create(self, task: TaskCreate) -> TaskInDB:
        """Create a new task"""
        conn = await self.db.get_connection()
        try:
            # Shift existing tasks in the column
            await conn.execute(
                task_queries.SHIFT_TASKS_UP_IN_COLUMN,
                task.column_id,
                task.order
            )

            row = await conn.fetchrow(
                task_queries.CREATE_TASK,
                task.title,
                task.description,
                task.column_id,
                task.order
            )
            return TaskInDB(**dict(row))
        finally:
            await self.db.release_connection(conn)

    async def move_to_column(self, task_id: int, target_column_id: int, new_order: int) -> Optional[TaskInDB]:
        """Move a task to a different column"""
        conn = await self.db.get_connection()
        try:
            # Get current task info
            existing = await self.get_by_id(task_id)
            if not existing:
                return None

            # If moving to same column, use reorder instead
            if existing.column_id == target_column_id:
                return await self.reorder_in_column(task_id, new_order)

            # Shift tasks in target column to make space
            await conn.execute(
                task_queries.SHIFT_TASKS_UP_IN_COLUMN,
                target_column_id,
                new_order
            )

            # Move the task
            row = await conn.fetchrow(
                task_queries.MOVE_TASK_TO_COLUMN,
                task_id,
                target_column_id,
                new_order
            )

            # Clean up old column by shifting down
            await conn.execute(
                task_queries.SHIFT_TASKS_DOWN_IN_COLUMN,
                existing.column_id,
                existing.order
            )

            return TaskInDB(**dict(row)) if row else None
        finally:
            await self.db.release_connection(conn)
```

---

## Pydantic Configuration for camelCase ↔ snake_case

To automatically convert between camelCase (frontend) and snake_case (backend), add this to your Pydantic models:

```python
from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    """Base User model with camelCase conversion"""
    name: str
    email: str
    avatar_url: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        )
    )
```

This allows the API to accept both `avatar_url` and `avatarUrl` in requests, and respond with `avatarUrl` in JSON.

**Alternative:** Use a library like `humps` for more robust conversion:

```bash
just add humps
```

```python
from humps import camelize

class UserBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=camelize,
        populate_by_name=True
    )
```

---

## Testing Strategy

### 1. Manual Testing with Swagger UI

After implementing each entity:
1. Start the server: `just dev`
2. Open http://localhost:8000/docs
3. Test each endpoint in order:
   - Create
   - Get all
   - Get by ID
   - Update
   - Delete

### 2. Testing Order Operations

**For Columns:**
1. Create column with order=0
2. Create column with order=1
3. Create column with order=0 (should shift others)
4. Reorder column from position 0 to 2
5. Delete middle column (should reorder others)

**For Tasks:**
1. Create column first
2. Create task in column with order=0
3. Create another task with order=0 (should shift)
4. Move task to different column
5. Reorder task within column

### 3. Database Verification

```sql
-- Check users
SELECT * FROM users ORDER BY created_at DESC;

-- Check columns with order
SELECT * FROM columns ORDER BY "order" ASC;

-- Check tasks with their columns
SELECT t.*, c.title as column_title
FROM tasks t
JOIN columns c ON t.column_id = c.id
ORDER BY c."order", t."order";

-- Verify foreign key cascade
DELETE FROM columns WHERE id = 1;
SELECT * FROM tasks WHERE column_id = 1;  -- Should be empty
```

---

## Common Pitfalls and Solutions

### 1. SQL Reserved Keywords

**Problem:** `order` is a SQL reserved keyword

**Solution:** Always quote it as `"order"` in SQL queries

```sql
-- ❌ Wrong
SELECT order FROM columns

-- ✅ Correct
SELECT "order" FROM columns
```

### 2. Order Conflicts

**Problem:** Unique constraint violations when creating/updating order

**Solution:** Always shift existing items before inserting

```python
# Shift existing items first
await conn.execute(SHIFT_COLUMNS_UP, new_order)
# Then insert
await conn.fetchrow(CREATE_COLUMN, title, new_order)
```

### 3. Foreign Key Violations

**Problem:** Creating task with non-existent column_id

**Solution:** Validate column exists in API layer

```python
@router.post("/tasks")
async def create_task(task: TaskCreate):
    # Verify column exists
    column = await column_repo.get_by_id(task.column_id)
    if not column:
        raise HTTPException(404, "Column not found")
    return await task_repo.create(task)
```

### 4. Email Validation

**Problem:** Pydantic's EmailStr requires email-validator package

**Solution:** Install the package

```bash
just add email-validator
```

---

## Implementation Checklist

### Users Entity
- [ ] Create `app/models/user.py`
- [ ] Create `app/database/sql/user_queries.py`
- [ ] Create `app/database/protocols/user_protocol.py`
- [ ] Create `app/database/implementations/user_repository.py`
- [ ] Create `app/api/users.py`
- [ ] Update `app/main.py` to include users router
- [ ] Test all user endpoints

### Columns Entity
- [ ] Create `app/models/column.py`
- [ ] Create `app/database/sql/column_queries.py`
- [ ] Create `app/database/protocols/column_protocol.py`
- [ ] Create `app/database/implementations/column_repository.py`
- [ ] Create `app/api/columns.py`
- [ ] Update `app/main.py` to include columns router
- [ ] Test all column endpoints including reorder

### Tasks Entity
- [ ] Create `app/models/task.py`
- [ ] Create `app/database/sql/task_queries.py`
- [ ] Create `app/database/protocols/task_protocol.py`
- [ ] Create `app/database/implementations/task_repository.py`
- [ ] Create `app/api/tasks.py`
- [ ] Update `app/main.py` to include tasks router
- [ ] Test all task endpoints including move and reorder

### Database Migration
- [ ] Create migration file: `just migrate-create "create_kanban_tables"`
- [ ] Add table creation code to migration
- [ ] Run migration: `just migrate-up`
- [ ] Verify tables in database
- [ ] Test rollback: `just migrate-down` then `just migrate-up`

### Dependencies
- [ ] Install email-validator: `just add email-validator`
- [ ] (Optional) Install humps for camelCase: `just add humps`

---

## Summary

This implementation plan provides a complete roadmap for adding Users, Columns, and Tasks entities to your FastAPI backend. Key highlights:

1. **3-File Pattern**: Maintains consistency with existing codebase architecture
2. **Order Management**: Robust handling of ordering with automatic shifting
3. **Foreign Keys**: Proper relationships with cascade delete
4. **Validation**: Comprehensive validation at both Pydantic and API levels
5. **Testing**: Clear testing strategy for each component

Follow the implementation order (Users → Columns → Tasks) to minimize dependencies and enable incremental testing. Each entity can be fully tested before moving to the next.

**Estimated Implementation Time:**
- Users: 2-3 hours
- Columns: 3-4 hours (more complex due to ordering)
- Tasks: 4-5 hours (most complex due to move/reorder operations)
- Migration & Testing: 1-2 hours
- **Total: 10-14 hours**

Good luck with your implementation! 🚀
