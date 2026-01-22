from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ColumnBase(BaseModel):
    """Base Column model"""
    title: str = Field(..., min_length=1, max_length=200, description="Column title")
    order: int = Field(..., ge=0, description="Display order (0-indexed)")


class ColumnCreate(ColumnBase):
    """Model for creating a new Column"""
    pass


class ColumnUpdate(BaseModel):
    """Model for updating a Column"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    order: Optional[int] = Field(None, ge=0)


class ColumnInDB(ColumnBase):
    """Model for Column in database"""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ColumnResponse(ColumnInDB):
    """Model for Column API response"""
    pass


class ColumnReorder(BaseModel):
    """Model for reordering columns"""
    column_id: int = Field(..., description="ID of column to move")
    new_order: int = Field(..., ge=0, description="New order position")

