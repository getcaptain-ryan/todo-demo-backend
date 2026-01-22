from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base User model"""
    name: str = Field(..., min_length=1, max_length=200, description="User's full name")
    email: EmailStr = Field(..., description="User's email address (must be unique)")
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL to user's avatar image")


class UserCreate(UserBase):
    """Model for creating a new User"""
    pass


class UserUpdate(BaseModel):
    """Model for updating a User"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserInDB(UserBase):
    """Model for User in database"""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserInDB):
    """Model for User API response"""
    pass

