from typing import List, Optional
import asyncpg
from app.models.todo import TodoCreate, TodoUpdate, TodoInDB
from app.database.sql import todo_queries
from app.database.connection import db


class TodoRepository:
    """Implementation of Todo repository using asyncpg"""
    
    def __init__(self):
        self.db = db
    
    async def create(self, todo: TodoCreate) -> TodoInDB:
        """Create a new todo"""
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow(
                todo_queries.CREATE_TODO,
                todo.title,
                todo.description,
                todo.completed
            )
            return TodoInDB(**dict(row))
        finally:
            await self.db.release_connection(conn)
    
    async def get_all(self) -> List[TodoInDB]:
        """Get all todos"""
        conn = await self.db.get_connection()
        try:
            rows = await conn.fetch(todo_queries.GET_ALL_TODOS)
            return [TodoInDB(**dict(row)) for row in rows]
        finally:
            await self.db.release_connection(conn)
    
    async def get_by_id(self, todo_id: int) -> Optional[TodoInDB]:
        """Get a todo by ID"""
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow(todo_queries.GET_TODO_BY_ID, todo_id)
            return TodoInDB(**dict(row)) if row else None
        finally:
            await self.db.release_connection(conn)
    
    async def update(self, todo_id: int, todo: TodoUpdate) -> Optional[TodoInDB]:
        """Update a todo"""
        # First get the existing todo
        existing = await self.get_by_id(todo_id)
        if not existing:
            return None
        
        # Merge updates with existing data
        update_data = todo.model_dump(exclude_unset=True)
        title = update_data.get("title", existing.title)
        description = update_data.get("description", existing.description)
        completed = update_data.get("completed", existing.completed)
        
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow(
                todo_queries.UPDATE_TODO,
                todo_id,
                title,
                description,
                completed
            )
            return TodoInDB(**dict(row)) if row else None
        finally:
            await self.db.release_connection(conn)
    
    async def delete(self, todo_id: int) -> bool:
        """Delete a todo"""
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow(todo_queries.DELETE_TODO, todo_id)
            return row is not None
        finally:
            await self.db.release_connection(conn)
    
    async def mark_completed(self, todo_id: int) -> Optional[TodoInDB]:
        """Mark a todo as completed"""
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow(todo_queries.MARK_TODO_COMPLETED, todo_id)
            return TodoInDB(**dict(row)) if row else None
        finally:
            await self.db.release_connection(conn)
    
    async def mark_incomplete(self, todo_id: int) -> Optional[TodoInDB]:
        """Mark a todo as incomplete"""
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow(todo_queries.MARK_TODO_INCOMPLETE, todo_id)
            return TodoInDB(**dict(row)) if row else None
        finally:
            await self.db.release_connection(conn)

