from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.task import TaskCreate, TaskUpdate, TaskResponse, TaskMove, TaskReorder
from app.database.implementations.task_repository import TaskRepository
from app.database.implementations.column_repository import ColumnRepository

router = APIRouter(prefix="/tasks", tags=["tasks"])
task_repo = TaskRepository()
column_repo = ColumnRepository()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    """Create a new task"""
    # Verify column exists
    column = await column_repo.get_by_id(task.column_id)
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Column with id {task.column_id} not found"
        )
    return await task_repo.create(task)


@router.get("/", response_model=List[TaskResponse])
async def get_all_tasks():
    """Get all tasks"""
    return await task_repo.get_all()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int):
    """Get a task by ID"""
    task = await task_repo.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task: TaskUpdate):
    """Update a task"""
    updated_task = await task_repo.update(task_id, task)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    """Delete a task"""
    deleted = await task_repo.delete(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )


@router.patch("/{task_id}/move", response_model=TaskResponse)
async def move_task(task_id: int, move: TaskMove):
    """Move a task to a different column"""
    if move.task_id != task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task ID in path must match task_id in request body"
        )
    
    # Verify target column exists
    column = await column_repo.get_by_id(move.target_column_id)
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target column with id {move.target_column_id} not found"
        )
    
    moved_task = await task_repo.move_to_column(task_id, move.target_column_id, move.new_order)
    if not moved_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return moved_task


@router.patch("/{task_id}/reorder", response_model=TaskResponse)
async def reorder_task(task_id: int, reorder: TaskReorder):
    """Reorder a task within the same column"""
    if reorder.task_id != task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task ID in path must match task_id in request body"
        )
    
    reordered_task = await task_repo.reorder_in_column(task_id, reorder.new_order)
    if not reordered_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return reordered_task


@router.get("/columns/{column_id}/tasks", response_model=List[TaskResponse])
async def get_tasks_by_column(column_id: int):
    """Get all tasks in a specific column"""
    # Verify column exists
    column = await column_repo.get_by_id(column_id)
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Column with id {column_id} not found"
        )
    return await task_repo.get_by_column(column_id)

