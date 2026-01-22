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

