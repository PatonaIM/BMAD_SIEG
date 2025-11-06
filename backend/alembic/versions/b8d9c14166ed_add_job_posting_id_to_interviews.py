"""add_job_posting_id_to_interviews

Revision ID: b8d9c14166ed
Revises: c4c387c07d02
Create Date: 2025-11-05 00:27:07.261874

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8d9c14166ed'
down_revision: Union[str, Sequence[str], None] = 'c4c387c07d02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Add optional job_posting_id FK to interviews table."""
    # Add nullable job_posting_id column with foreign key constraint
    op.add_column(
        'interviews',
        sa.Column(
            'job_posting_id',
            sa.UUID(as_uuid=True),
            nullable=True
        )
    )
    
    # Add foreign key constraint with ON DELETE SET NULL
    op.create_foreign_key(
        'fk_interviews_job_posting_id',
        'interviews',
        'job_postings',
        ['job_posting_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Add index for performance on job_posting_id lookups
    op.create_index(
        'ix_interviews_job_posting_id',
        'interviews',
        ['job_posting_id']
    )


def downgrade() -> None:
    """Downgrade schema: Remove job_posting_id from interviews table."""
    # Drop index first
    op.drop_index('ix_interviews_job_posting_id', table_name='interviews')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_interviews_job_posting_id', 'interviews', type_='foreignkey')
    
    # Drop column
    op.drop_column('interviews', 'job_posting_id')
