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

