from typing import Protocol, List, Optional
from app.models.column import ColumnCreate, ColumnUpdate, ColumnInDB


class ColumnRepositoryProtocol(Protocol):
    """Protocol defining the interface for Column repository operations"""
    
    async def create(self, column: ColumnCreate) -> ColumnInDB:
        """Create a new column"""
        ...
    
    async def get_all(self) -> List[ColumnInDB]:
        """Get all columns ordered by position"""
        ...
    
    async def get_by_id(self, column_id: int) -> Optional[ColumnInDB]:
        """Get a column by ID"""
        ...
    
    async def update(self, column_id: int, column: ColumnUpdate) -> Optional[ColumnInDB]:
        """Update a column"""
        ...
    
    async def delete(self, column_id: int) -> bool:
        """Delete a column and reorder remaining columns"""
        ...
    
    async def reorder(self, column_id: int, new_order: int) -> Optional[ColumnInDB]:
        """Reorder a column to a new position"""
        ...

