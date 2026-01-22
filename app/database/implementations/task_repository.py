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
    
    async def get_all(self) -> List[TaskInDB]:
        """Get all tasks"""
        conn = await self.db.get_connection()
        try:
            rows = await conn.fetch(task_queries.GET_ALL_TASKS)
            return [TaskInDB(**dict(row)) for row in rows]
        finally:
            await self.db.release_connection(conn)
    
    async def get_by_id(self, task_id: int) -> Optional[TaskInDB]:
        """Get a task by ID"""
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow(task_queries.GET_TASK_BY_ID, task_id)
            return TaskInDB(**dict(row)) if row else None
        finally:
            await self.db.release_connection(conn)
    
    async def get_by_column(self, column_id: int) -> List[TaskInDB]:
        """Get all tasks in a specific column"""
        conn = await self.db.get_connection()
        try:
            rows = await conn.fetch(task_queries.GET_TASKS_BY_COLUMN, column_id)
            return [TaskInDB(**dict(row)) for row in rows]
        finally:
            await self.db.release_connection(conn)
    
    async def update(self, task_id: int, task: TaskUpdate) -> Optional[TaskInDB]:
        """Update a task"""
        existing = await self.get_by_id(task_id)
        if not existing:
            return None
        
        update_data = task.model_dump(exclude_unset=True)
        title = update_data.get("title", existing.title)
        description = update_data.get("description", existing.description)
        order = update_data.get("order", existing.order)
        
        conn = await self.db.get_connection()
        try:
            # If order is changing, use reorder logic
            if order != existing.order:
                return await self.reorder_in_column(task_id, order)
            
            row = await conn.fetchrow(
                task_queries.UPDATE_TASK,
                task_id,
                title,
                description,
                order
            )
            return TaskInDB(**dict(row)) if row else None
        finally:
            await self.db.release_connection(conn)
    
    async def delete(self, task_id: int) -> bool:
        """Delete a task"""
        conn = await self.db.get_connection()
        try:
            # Get the task info before deleting
            existing = await self.get_by_id(task_id)
            if not existing:
                return False
            
            # Delete the task
            row = await conn.fetchrow(task_queries.DELETE_TASK, task_id)
            if not row:
                return False
            
            # Shift down tasks that were after this one in the same column
            await conn.execute(
                task_queries.SHIFT_TASKS_DOWN_IN_COLUMN,
                existing.column_id,
                existing.order
            )
            return True
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

            # Shift down tasks in the old column
            await conn.execute(
                task_queries.SHIFT_TASKS_DOWN_IN_COLUMN,
                existing.column_id,
                existing.order
            )

            return TaskInDB(**dict(row)) if row else None
        finally:
            await self.db.release_connection(conn)

    async def reorder_in_column(self, task_id: int, new_order: int) -> Optional[TaskInDB]:
        """Reorder a task within its current column"""
        conn = await self.db.get_connection()
        try:
            rows = await conn.fetch(
                task_queries.REORDER_TASK_IN_COLUMN,
                task_id,
                new_order
            )
            # Find and return the reordered task
            for row in rows:
                if row['id'] == task_id:
                    return TaskInDB(**dict(row))
            return None
        finally:
            await self.db.release_connection(conn)

