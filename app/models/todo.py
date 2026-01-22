from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TodoBase(BaseModel):
    """Base Todo model"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: bool = False


class TodoCreate(TodoBase):
    """Model for creating a new Todo"""
    pass


class TodoUpdate(BaseModel):
    """Model for updating a Todo"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None


class TodoInDB(TodoBase):
    """Model for Todo in database"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TodoResponse(TodoInDB):
    """Model for Todo API response"""
    pass

