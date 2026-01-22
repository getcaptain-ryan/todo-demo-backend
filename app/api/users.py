from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.user import UserCreate, UserUpdate, UserResponse
from app.database.implementations.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["users"])
user_repo = UserRepository()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Create a new user"""
    # Check if email already exists
    existing = await user_repo.get_by_email(user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {user.email} already exists"
        )
    return await user_repo.create(user)


@router.get("/", response_model=List[UserResponse])
async def get_all_users():
    """Get all users"""
    return await user_repo.get_all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get a user by ID"""
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate):
    """Update a user"""
    # If email is being updated, check for conflicts
    if user.email:
        existing = await user_repo.get_by_email(user.email)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email {user.email} already exists"
            )
    
    updated_user = await user_repo.update(user_id, user)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """Delete a user"""
    deleted = await user_repo.delete(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

