"""add_profile_fields_and_embeddings_epic_04

Epic 04: Intelligent Job Matching System - Foundation Schema

This migration extends candidates and job_postings tables with:
- Profile fields: skills, experience_years, job_preferences, profile_completeness_score
- Vector embeddings: profile_embedding (candidates), job_embedding (job_postings)
- pgvector extension enabled

Vector dimension: 3072 (matches OpenAI text-embedding-3-large)

IMPORTANT: Vector indexes NOT created due to 2000-dimension limit in pgvector < 0.5.0.
For small-medium datasets (<10k records), exact search (without indexes) is acceptable.
For production with large datasets, upgrade to pgvector >= 0.5.0 and create HNSW indexes manually.

Revision ID: ef17ef26d8a1
Revises: b8d9c14166ed
Create Date: 2025-11-06 14:49:09.885129

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'ef17ef26d8a1'
down_revision: str | Sequence[str] | None = 'b8d9c14166ed'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - Add profile fields and vector embeddings for Epic 04."""
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Add profile fields to candidates table
    op.add_column(
        'candidates',
        sa.Column('skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="Array of skill strings")
    )
    op.add_column(
        'candidates',
        sa.Column('experience_years', sa.Integer(), nullable=True, comment="Years of professional experience")
    )
    op.add_column(
        'candidates',
        sa.Column('job_preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="Job search preferences object")
    )
    op.add_column(
        'candidates',
        sa.Column('profile_completeness_score', sa.Numeric(precision=5, scale=2), nullable=True, comment="Profile completion percentage 0-100")
    )

    # Add vector embedding to candidates table
    op.execute("""
        ALTER TABLE candidates
        ADD COLUMN profile_embedding vector(3072) NULL;
    """)
    op.execute("COMMENT ON COLUMN candidates.profile_embedding IS 'Semantic embedding for matching';")

    # Add vector embedding to job_postings table
    op.execute("""
        ALTER TABLE job_postings
        ADD COLUMN job_embedding vector(3072) NULL;
    """)
    op.execute("COMMENT ON COLUMN job_postings.job_embedding IS 'Semantic embedding for matching';")

    # Note: Indexes NOT created automatically due to 2000-dimension limit in pgvector < 0.5.0
    # For 3072-dimensional embeddings, indexes must be created manually after pgvector upgrade
    # or by using exact nearest neighbor search (without indexes) which is acceptable for small datasets
    # Future: When pgvector >= 0.5.0 is available, run:
    # CREATE INDEX idx_candidates_profile_embedding ON candidates
    # USING hnsw (profile_embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
    # CREATE INDEX idx_job_postings_job_embedding ON job_postings
    # USING hnsw (job_embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);


def downgrade() -> None:
    """Downgrade schema - Remove profile fields and vector embeddings."""
    # No indexes to drop (not created due to dimension limitations)

    # Drop vector columns
    op.drop_column('job_postings', 'job_embedding')
    op.drop_column('candidates', 'profile_embedding')

    # Drop profile fields from candidates
    op.drop_column('candidates', 'profile_completeness_score')
    op.drop_column('candidates', 'job_preferences')
    op.drop_column('candidates', 'experience_years')
    op.drop_column('candidates', 'skills')

    # Note: We don't drop the vector extension as it may be used elsewhere

