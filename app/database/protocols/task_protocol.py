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

