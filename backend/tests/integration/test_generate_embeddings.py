"""Integration tests for generate_embeddings.py script."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

# Add backend directory to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.models.candidate import Candidate
from app.models.job_posting import JobPosting
from app.repositories.candidate import CandidateRepository
from app.repositories.job_posting_repository import JobPostingRepository
from app.services.embedding_service import EmbeddingService
from scripts.generate_embeddings import process_all_candidates, process_all_jobs


@pytest.mark.asyncio
async def test_process_all_candidates_dry_run(test_db):
    """Test dry-run mode for candidates."""
    # Create test candidate with sufficient completeness
    candidate = Candidate(
        email="test@example.com",
        full_name="Test User",
        profile_completeness_score=50.0,
        skills=["Python", "FastAPI"],
        experience_years=5,
        profile_embedding=None
    )
    test_db.add(candidate)
    await test_db.flush()

    # Initialize services
    candidate_repo = CandidateRepository(test_db)
    job_repo = JobPostingRepository(test_db)
    embedding_service = EmbeddingService(candidate_repo, job_repo)

    # Run dry-run
    stats = await process_all_candidates(
        embedding_service=embedding_service,
        dry_run=True,
        force=False,
        limit_per_batch=100
    )

    # Verify dry-run counted but didn't process
    assert stats["total_processed"] == 1
    assert stats["successful"] == 0
    assert stats["failed"] == 0

    # Verify embedding was NOT generated
    await test_db.refresh(candidate)
    assert candidate.profile_embedding is None


@pytest.mark.asyncio
async def test_process_all_candidates_skip_existing(test_db):
    """Test that candidates with existing embeddings are skipped."""
    # Create candidate with existing embedding
    candidate = Candidate(
        email="test@example.com",
        full_name="Test User",
        profile_completeness_score=50.0,
        skills=["Python", "FastAPI"],
        experience_years=5,
        profile_embedding=[0.1] * 3072  # Mock existing embedding
    )
    test_db.add(candidate)
    await test_db.flush()

    # Initialize services
    candidate_repo = CandidateRepository(test_db)
    job_repo = JobPostingRepository(test_db)
    embedding_service = EmbeddingService(candidate_repo, job_repo)

    # Mock the batch_generate_candidate_embeddings to verify it's not called
    with patch.object(
        embedding_service,
        'batch_generate_candidate_embeddings',
        new_callable=AsyncMock
    ) as mock_batch:
        mock_batch.return_value = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }

        stats = await process_all_candidates(
            embedding_service=embedding_service,
            dry_run=False,
            force=False,
            limit_per_batch=100
        )

        # Verify no candidates were processed
        assert stats["total_processed"] == 0


@pytest.mark.asyncio
async def test_process_all_candidates_force_regenerate(test_db):
    """Test force flag regenerates existing embeddings."""
    # Create candidate with existing embedding
    candidate = Candidate(
        email="test@example.com",
        full_name="Test User",
        profile_completeness_score=50.0,
        skills=["Python", "FastAPI"],
        experience_years=5,
        profile_embedding=[0.1] * 3072  # Mock existing embedding
    )
    test_db.add(candidate)
    await test_db.flush()

    # Initialize services
    candidate_repo = CandidateRepository(test_db)
    job_repo = JobPostingRepository(test_db)
    embedding_service = EmbeddingService(candidate_repo, job_repo)

    # Mock OpenAI API to avoid real calls
    mock_embedding = [0.2] * 3072
    with patch.object(
        embedding_service,
        'batch_generate_embeddings',
        new_callable=AsyncMock
    ) as mock_api:
        mock_api.return_value = [mock_embedding]

        stats = await process_all_candidates(
            embedding_service=embedding_service,
            dry_run=False,
            force=True,
            limit_per_batch=100
        )

        # Verify candidate was processed with force flag
        assert stats["total_processed"] == 1
        assert stats["successful"] == 1
        assert stats["failed"] == 0

        # Verify embedding was updated
        await test_db.refresh(candidate)
        assert candidate.profile_embedding is not None


@pytest.mark.asyncio
async def test_process_all_candidates_low_completeness_skipped(test_db):
    """Test candidates with low completeness are skipped."""
    # Create candidate below 40% completeness threshold
    candidate = Candidate(
        email="test@example.com",
        full_name="Test User",
        profile_completeness_score=30.0,  # Below 40% threshold
        skills=["Python"],
        profile_embedding=None
    )
    test_db.add(candidate)
    await test_db.flush()

    # Initialize services
    candidate_repo = CandidateRepository(test_db)
    job_repo = JobPostingRepository(test_db)
    embedding_service = EmbeddingService(candidate_repo, job_repo)

    stats = await process_all_candidates(
        embedding_service=embedding_service,
        dry_run=False,
        force=False,
        limit_per_batch=100
    )

    # Verify no candidates were processed (below threshold)
    assert stats["total_processed"] == 0


@pytest.mark.asyncio
async def test_process_all_jobs_dry_run(test_db):
    """Test dry-run mode for job postings."""
    # Create test job posting
    job = JobPosting(
        title="Senior Python Developer",
        company="Test Corp",
        description="Test job description",
        role_category="engineering",
        employment_type="permanent",
        work_setup="remote",
        location="Remote",
        experience_level="Senior",
        status="active",
        job_embedding=None
    )
    test_db.add(job)
    await test_db.flush()

    # Initialize services
    candidate_repo = CandidateRepository(test_db)
    job_repo = JobPostingRepository(test_db)
    embedding_service = EmbeddingService(candidate_repo, job_repo)

    # Run dry-run
    stats = await process_all_jobs(
        embedding_service=embedding_service,
        dry_run=True,
        force=False,
        limit_per_batch=100
    )

    # Verify dry-run counted but didn't process
    assert stats["total_processed"] == 1
    assert stats["successful"] == 0
    assert stats["failed"] == 0

    # Verify embedding was NOT generated
    await test_db.refresh(job)
    assert job.job_embedding is None


@pytest.mark.asyncio
async def test_process_all_jobs_inactive_skipped(test_db):
    """Test that inactive job postings are skipped."""
    # Create paused job posting
    job = JobPosting(
        title="Senior Python Developer",
        company="Test Corp",
        description="Test job description",
        role_category="engineering",
        employment_type="permanent",
        work_setup="remote",
        location="Remote",
        experience_level="Senior",
        status="paused",  # Not active
        job_embedding=None
    )
    test_db.add(job)
    await test_db.flush()

    # Initialize services
    candidate_repo = CandidateRepository(test_db)
    job_repo = JobPostingRepository(test_db)
    embedding_service = EmbeddingService(candidate_repo, job_repo)

    stats = await process_all_jobs(
        embedding_service=embedding_service,
        dry_run=False,
        force=False,
        limit_per_batch=100
    )

    # Verify no jobs were processed (not active)
    assert stats["total_processed"] == 0


@pytest.mark.asyncio
async def test_process_all_jobs_pagination(test_db):
    """Test pagination works correctly for job postings."""
    # Create multiple active jobs
    for i in range(5):
        job = JobPosting(
            title=f"Developer {i}",
            company="Test Corp",
            description="Test job description",
            role_category="engineering",
            employment_type="permanent",
            work_setup="remote",
            location="Remote",
            experience_level="Mid-level",
            status="active",
            job_embedding=None
        )
        test_db.add(job)
    await test_db.flush()

    # Initialize services
    candidate_repo = CandidateRepository(test_db)
    job_repo = JobPostingRepository(test_db)
    embedding_service = EmbeddingService(candidate_repo, job_repo)

    # Mock OpenAI API
    mock_embedding = [0.1] * 3072
    with patch.object(
        embedding_service,
        'batch_generate_embeddings',
        new_callable=AsyncMock
    ) as mock_api:
        # Return different sized lists to simulate pagination
        mock_api.side_effect = [
            [mock_embedding] * 2,  # First batch: 2 jobs
            [mock_embedding] * 2,  # Second batch: 2 jobs
            [mock_embedding] * 1   # Third batch: 1 job
        ]

        stats = await process_all_jobs(
            embedding_service=embedding_service,
            dry_run=False,
            force=False,
            limit_per_batch=2  # Small batch to test pagination
        )

        # Verify all jobs were processed across batches
        assert stats["total_processed"] == 5
        assert stats["successful"] == 5
        assert stats["failed"] == 0


@pytest.mark.asyncio
async def test_script_error_handling(test_db):
    """Test that script continues processing on individual failures."""
    # Create multiple candidates
    for i in range(3):
        candidate = Candidate(
            email=f"test{i}@example.com",
            full_name=f"Test User {i}",
            profile_completeness_score=50.0,
            skills=["Python"],
            experience_years=5,
            profile_embedding=None
        )
        test_db.add(candidate)
    await test_db.flush()

    # Initialize services
    candidate_repo = CandidateRepository(test_db)
    job_repo = JobPostingRepository(test_db)
    embedding_service = EmbeddingService(candidate_repo, job_repo)

    # Mock to simulate partial failure
    with patch.object(
        embedding_service,
        'batch_generate_candidate_embeddings',
        new_callable=AsyncMock
    ) as mock_batch:
        mock_batch.return_value = {
            "total_processed": 3,
            "successful": 2,
            "failed": 1,
            "skipped": 0,
            "errors": ["Failed to process candidate UUID: test error"]
        }

        stats = await process_all_candidates(
            embedding_service=embedding_service,
            dry_run=False,
            force=False,
            limit_per_batch=100
        )

        # Verify stats reflect partial success
        assert stats["total_processed"] == 3
        assert stats["successful"] == 2
        assert stats["failed"] == 1
        assert len(stats["errors"]) == 1
