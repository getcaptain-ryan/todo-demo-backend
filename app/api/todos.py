from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.todo import TodoCreate, TodoUpdate, TodoResponse
from app.database.implementations.todo_repository import TodoRepository

router = APIRouter(prefix="/todos", tags=["todos"])
todo_repo = TodoRepository()


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate):
    """Create a new todo"""
    return await todo_repo.create(todo)


@router.get("/", response_model=List[TodoResponse])
async def get_all_todos():
    """Get all todos"""
    return await todo_repo.get_all()


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int):
    """Get a todo by ID"""
    todo = await todo_repo.get_by_id(todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {todo_id} not found"
        )
    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, todo: TodoUpdate):
    """Update a todo"""
    updated_todo = await todo_repo.update(todo_id, todo)
    if not updated_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {todo_id} not found"
        )
    return updated_todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int):
    """Delete a todo"""
    deleted = await todo_repo.delete(todo_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {todo_id} not found"
        )


@router.patch("/{todo_id}/complete", response_model=TodoResponse)
async def mark_todo_completed(todo_id: int):
    """Mark a todo as completed"""
    todo = await todo_repo.mark_completed(todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {todo_id} not found"
        )
    return todo


@router.patch("/{todo_id}/incomplete", response_model=TodoResponse)
async def mark_todo_incomplete(todo_id: int):
    """Mark a todo as incomplete"""
    todo = await todo_repo.mark_incomplete(todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {todo_id} not found"
        )
    return todo

