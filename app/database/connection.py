import asyncpg
from typing import Optional
from app.core.config import settings


class DatabaseConnection:
    """Database connection manager using asyncpg"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """Create database connection pool"""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL,
                min_size=5,
                max_size=20,
                command_timeout=60,
            )
    
    async def disconnect(self) -> None:
        """Close database connection pool"""
        if self.pool is not None:
            await self.pool.close()
            self.pool = None
    
    async def get_connection(self) -> asyncpg.Connection:
        """Get a connection from the pool"""
        if self.pool is None:
            await self.connect()
        return await self.pool.acquire()
    
    async def release_connection(self, connection: asyncpg.Connection) -> None:
        """Release a connection back to the pool"""
        if self.pool is not None:
            await self.pool.release(connection)


# Global database connection instance
db = DatabaseConnection()

