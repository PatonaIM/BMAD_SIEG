"""add_realtime_cost_tracking

Revision ID: 173e256bc347
Revises: 36dca3922506
Create Date: 2025-11-01 18:05:09.465189

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '173e256bc347'
down_revision: Union[str, Sequence[str], None] = '36dca3922506'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add realtime API cost tracking field to interviews table
    op.add_column(
        'interviews',
        sa.Column(
            'realtime_cost_usd',
            sa.Numeric(precision=10, scale=4),
            nullable=False,
            server_default='0.0000'
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove realtime API cost tracking field
    op.drop_column('interviews', 'realtime_cost_usd')
