"""add_default_columns

Revision ID: 0c4431ca83dd
Revises: 4ff83a080ba6
Create Date: 2026-01-22 19:30:26.467398

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c4431ca83dd'
down_revision: Union[str, Sequence[str], None] = '4ff83a080ba6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add default columns."""
    op.execute("""
        INSERT INTO columns (title, "order") VALUES
        ('Todo', 0),
        ('In Progress', 1),
        ('Done', 2)
    """)


def downgrade() -> None:
    """Remove default columns."""
    op.execute("""
        DELETE FROM columns WHERE title IN ('Todo', 'In Progress', 'Done')
    """)
