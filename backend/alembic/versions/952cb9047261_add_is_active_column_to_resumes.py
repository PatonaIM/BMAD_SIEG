"""add_is_active_column_to_resumes

Revision ID: 952cb9047261
Revises: ef17ef26d8a1
Create Date: 2025-11-09 04:08:25.944464

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '952cb9047261'
down_revision: Union[str, Sequence[str], None] = 'ef17ef26d8a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add is_active column to resumes table with default True
    op.add_column(
        'resumes',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true')
    )
    # Create index for filtering active resumes by candidate
    op.create_index(
        'idx_resumes_candidate_active',
        'resumes',
        ['candidate_id', 'is_active']
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index and column
    op.drop_index('idx_resumes_candidate_active', table_name='resumes')
    op.drop_column('resumes', 'is_active')
