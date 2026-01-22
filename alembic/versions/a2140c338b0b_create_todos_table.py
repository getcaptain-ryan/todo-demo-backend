"""create_todos_table

Revision ID: a2140c338b0b
Revises: 
Create Date: 2026-01-22 07:35:36.401374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2140c338b0b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'todos',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_todos_id', 'todos', ['id'])
    op.create_index('ix_todos_completed', 'todos', ['completed'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_todos_completed', table_name='todos')
    op.drop_index('ix_todos_id', table_name='todos')
    op.drop_table('todos')
