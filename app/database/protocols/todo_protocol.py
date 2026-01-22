from typing import Protocol, List, Optional
from app.models.todo import TodoCreate, TodoUpdate, TodoInDB


class TodoRepositoryProtocol(Protocol):
    """Protocol defining the interface for Todo repository operations"""
    
    async def create(self, todo: TodoCreate) -> TodoInDB:
        """Create a new todo"""
        ...
    
    async def get_all(self) -> List[TodoInDB]:
        """Get all todos"""
        ...
    
    async def get_by_id(self, todo_id: int) -> Optional[TodoInDB]:
        """Get a todo by ID"""
        ...
    
    async def update(self, todo_id: int, todo: TodoUpdate) -> Optional[TodoInDB]:
        """Update a todo"""
        ...
    
    async def delete(self, todo_id: int) -> bool:
        """Delete a todo"""
        ...
    
    async def mark_completed(self, todo_id: int) -> Optional[TodoInDB]:
        """Mark a todo as completed"""
        ...
    
    async def mark_incomplete(self, todo_id: int) -> Optional[TodoInDB]:
        """Mark a todo as incomplete"""
        ...

