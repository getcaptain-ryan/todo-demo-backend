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

