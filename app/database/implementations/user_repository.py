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

