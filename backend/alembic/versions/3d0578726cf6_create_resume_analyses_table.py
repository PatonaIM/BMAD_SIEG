"""create_resume_analyses_table

Revision ID: 3d0578726cf6
Revises: 952cb9047261
Create Date: 2025-11-09 04:09:49.366614

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '3d0578726cf6'
down_revision: Union[str, Sequence[str], None] = '952cb9047261'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'resume_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('resume_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('overall_score', sa.Integer(), nullable=False),
        sa.Column('strengths', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('weaknesses', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('suggestions', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('keywords_missing', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('analysis_model', sa.String(50), server_default='gpt-4o-mini'),
        sa.Column('tokens_used', sa.Integer(), server_default='0'),
        sa.Column('analyzed_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('overall_score >= 0 AND overall_score <= 100', name='check_score_range')
    )
    
    # Create index for efficient lookups by resume_id
    op.create_index('idx_resume_analyses_resume_id', 'resume_analyses', ['resume_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_resume_analyses_resume_id', table_name='resume_analyses')
    op.drop_table('resume_analyses')
