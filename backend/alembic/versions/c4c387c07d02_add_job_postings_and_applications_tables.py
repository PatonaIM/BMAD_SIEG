"""add_job_postings_and_applications_tables

Revision ID: c4c387c07d02
Revises: 4839d6236216
Create Date: 2025-11-04 18:46:17.618820

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c4c387c07d02'
down_revision: Union[str, Sequence[str], None] = '4839d6236216'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add job_postings and applications tables."""
    # Create enums using DO blocks to avoid duplicate errors
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE role_category AS ENUM ('engineering', 'quality_assurance', 'data', 'devops', 'design', 'product', 'sales', 'support', 'operations', 'management', 'other');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE employment_type AS ENUM ('permanent', 'contract', 'part_time');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE work_setup AS ENUM ('remote', 'hybrid', 'onsite');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE job_posting_status AS ENUM ('active', 'paused', 'closed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE application_status AS ENUM ('applied', 'interview_scheduled', 'interview_completed', 'under_review', 'rejected', 'offered', 'accepted', 'withdrawn');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create job_postings table
    op.create_table(
        'job_postings',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('role_category', postgresql.ENUM('engineering', 'quality_assurance', 'data', 'devops', 'design', 'product', 'sales', 'support', 'operations', 'management', 'other', name='role_category', create_type=False), nullable=False),
        sa.Column('tech_stack', sa.String(length=100), nullable=True),
        sa.Column('employment_type', postgresql.ENUM('permanent', 'contract', 'part_time', name='employment_type', create_type=False), nullable=False),
        sa.Column('work_setup', postgresql.ENUM('remote', 'hybrid', 'onsite', name='work_setup', create_type=False), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('salary_min', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('salary_max', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('salary_currency', sa.String(length=3), nullable=False),
        sa.Column('required_skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('experience_level', sa.String(length=50), nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'paused', 'closed', name='job_posting_status', create_type=False), nullable=False),
        sa.Column('is_cancelled', sa.Boolean(), nullable=False),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for job_postings
    op.create_index('idx_job_postings_role_category', 'job_postings', ['role_category'])
    op.create_index(
        'idx_job_postings_tech_stack',
        'job_postings',
        ['tech_stack'],
        postgresql_where=sa.text('tech_stack IS NOT NULL')
    )
    op.create_index(
        'idx_job_postings_status',
        'job_postings',
        ['status'],
        postgresql_where=sa.text("status = 'active'")
    )
    op.create_index('idx_job_postings_employment_type', 'job_postings', ['employment_type'])
    op.create_index('idx_job_postings_created_at', 'job_postings', ['created_at'])

    # Create applications table
    op.create_table(
        'applications',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('candidate_id', postgresql.UUID(), nullable=False),
        sa.Column('job_posting_id', postgresql.UUID(), nullable=False),
        sa.Column('interview_id', postgresql.UUID(), nullable=True),
        sa.Column('status', postgresql.ENUM('applied', 'interview_scheduled', 'interview_completed', 'under_review', 'rejected', 'offered', 'accepted', 'withdrawn', name='application_status', create_type=False), nullable=False),
        sa.Column('applied_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_posting_id'], ['job_postings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('candidate_id', 'job_posting_id', name='uq_applications_candidate_job')
    )

    # Create indexes for applications
    op.create_index('idx_applications_candidate_id', 'applications', ['candidate_id'])
    op.create_index('idx_applications_job_posting_id', 'applications', ['job_posting_id'])
    op.create_index('idx_applications_interview_id', 'applications', ['interview_id'])
    op.create_index('idx_applications_status', 'applications', ['status'])
    op.create_index('idx_applications_applied_at', 'applications', ['applied_at'])


def downgrade() -> None:
    """Downgrade schema - Remove job_postings and applications tables."""
    # Drop tables (indexes and constraints will be dropped automatically)
    op.drop_table('applications')
    op.drop_table('job_postings')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS application_status")
    op.execute("DROP TYPE IF EXISTS job_posting_status")
    op.execute("DROP TYPE IF EXISTS work_setup")
    op.execute("DROP TYPE IF EXISTS employment_type")
    op.execute("DROP TYPE IF EXISTS role_category")

