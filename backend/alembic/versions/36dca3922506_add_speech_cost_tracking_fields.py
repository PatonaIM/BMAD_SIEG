"""add_speech_cost_tracking_fields

Revision ID: 36dca3922506
Revises: 075e167c8434
Create Date: 2025-10-31 23:41:02.211227

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36dca3922506'
down_revision: Union[str, Sequence[str], None] = '075e167c8434'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add speech cost tracking fields to interviews table
    op.add_column('interviews', sa.Column('speech_tokens_used', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('interviews', sa.Column('speech_cost_usd', sa.Numeric(precision=10, scale=4), nullable=False, server_default='0.0000'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove speech cost tracking fields
    op.drop_column('interviews', 'speech_cost_usd')
    op.drop_column('interviews', 'speech_tokens_used')
