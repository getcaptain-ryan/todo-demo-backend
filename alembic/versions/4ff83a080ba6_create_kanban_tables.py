"""create_kanban_tables

Revision ID: 4ff83a080ba6
Revises: a2140c338b0b
Create Date: 2026-01-22 09:34:02.414819

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ff83a080ba6'
down_revision: Union[str, Sequence[str], None] = 'a2140c338b0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'])

    # Create columns table
    op.create_table(
        'columns',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order', name='uq_columns_order')
    )
    op.create_index('ix_columns_id', 'columns', ['id'])
    op.create_index('ix_columns_order', 'columns', ['order'])

    # Create tasks table (depends on columns)
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('column_id', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['column_id'], ['columns.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('column_id', 'order', name='uq_tasks_column_order')
    )
    op.create_index('ix_tasks_id', 'tasks', ['id'])
    op.create_index('ix_tasks_column_id', 'tasks', ['column_id'])
    op.create_index('ix_tasks_order', 'tasks', ['order'])


def downgrade() -> None:
    """Downgrade schema."""

    # Drop in reverse order (tasks first due to foreign key)
    op.drop_index('ix_tasks_order', table_name='tasks')
    op.drop_index('ix_tasks_column_id', table_name='tasks')
    op.drop_index('ix_tasks_id', table_name='tasks')
    op.drop_table('tasks')

    op.drop_index('ix_columns_order', table_name='columns')
    op.drop_index('ix_columns_id', table_name='columns')
    op.drop_table('columns')

    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
