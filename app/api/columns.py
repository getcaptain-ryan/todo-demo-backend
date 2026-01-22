from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.column import ColumnCreate, ColumnUpdate, ColumnResponse, ColumnReorder
from app.database.implementations.column_repository import ColumnRepository

router = APIRouter(prefix="/columns", tags=["columns"])
column_repo = ColumnRepository()


@router.post("/", response_model=ColumnResponse, status_code=status.HTTP_201_CREATED)
async def create_column(column: ColumnCreate):
    """Create a new column"""
    return await column_repo.create(column)


@router.get("/", response_model=List[ColumnResponse])
async def get_all_columns():
    """Get all columns ordered by position"""
    return await column_repo.get_all()


@router.get("/{column_id}", response_model=ColumnResponse)
async def get_column(column_id: int):
    """Get a column by ID"""
    column = await column_repo.get_by_id(column_id)
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Column with id {column_id} not found"
        )
    return column


@router.put("/{column_id}", response_model=ColumnResponse)
async def update_column(column_id: int, column: ColumnUpdate):
    """Update a column"""
    updated_column = await column_repo.update(column_id, column)
    if not updated_column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Column with id {column_id} not found"
        )
    return updated_column


@router.delete("/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(column_id: int):
    """Delete a column (will also delete all tasks in this column)"""
    deleted = await column_repo.delete(column_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Column with id {column_id} not found"
        )


@router.patch("/{column_id}/reorder", response_model=ColumnResponse)
async def reorder_column(column_id: int, reorder: ColumnReorder):
    """Reorder a column to a new position"""
    if reorder.column_id != column_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Column ID in path must match column_id in request body"
        )
    
    reordered = await column_repo.reorder(column_id, reorder.new_order)
    if not reordered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Column with id {column_id} not found"
        )
    return reordered

