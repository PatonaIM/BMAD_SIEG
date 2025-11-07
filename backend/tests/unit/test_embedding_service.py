"""Unit tests for EmbeddingService."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from openai import APIError, APITimeoutError, AuthenticationError, RateLimitError

from app.core.exceptions import OpenAIProviderError, RateLimitExceededError
from app.models.candidate import Candidate
from app.models.job_posting import JobPosting
from app.services.embedding_service import (
    EmbeddingService,
    build_candidate_embedding_text,
    build_job_embedding_text,
)


# ============================================================================
# Text Construction Function Tests
# ============================================================================

def test_build_candidate_embedding_text_full_profile():
    """Test candidate embedding text with complete profile."""
    candidate = Candidate(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        skills=["python", "react", "typescript", "aws"],
        experience_years=5,
        job_preferences={
            "locations": ["Remote Australia", "Sydney NSW"],
            "employment_types": ["permanent"],
            "work_setups": ["remote", "hybrid"],
            "salary_min": 120000,
            "salary_max": 150000,
            "role_categories": ["engineering", "quality_assurance"]
        }
    )

    text = build_candidate_embedding_text(candidate)

    assert "Skills: python, react, typescript, aws" in text
    assert "Experience: 5 years" in text
    assert "Locations Remote Australia Sydney NSW" in text
    assert "Employment permanent" in text
    assert "Work Setup remote hybrid" in text
    assert "Salary Range 120000-150000 AUD" in text
    assert "Role Categories engineering quality_assurance" in text


def test_build_candidate_embedding_text_minimal_profile():
    """Test candidate embedding text with minimal profile (skills only)."""
    candidate = Candidate(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        skills=["javascript", "node.js"],
        experience_years=None,
        job_preferences=None
    )

    text = build_candidate_embedding_text(candidate)

    assert "Skills: javascript, node.js" in text
    assert "Experience" not in text
    assert "Preferences" not in text


def test_build_candidate_embedding_text_no_skills():
    """Test candidate embedding text with no skills."""
    candidate = Candidate(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        skills=None,
        experience_years=3,
        job_preferences=None
    )

    text = build_candidate_embedding_text(candidate)

    assert "Skills" not in text
    assert "Experience: 3 years" in text


def test_build_job_embedding_text_full_job():
    """Test job embedding text with complete job posting."""
    job = JobPosting(
        id=uuid4(),
        title="Senior React Developer",
        company="TechCorp",
        description="We are seeking an experienced React developer to join our team.",
        role_category="engineering",
        required_skills=["react", "typescript", "redux", "graphql"],
        experience_level="Senior",
        employment_type="permanent",
        work_setup="remote",
        location="Remote Australia"
    )

    text = build_job_embedding_text(job)

    assert "Title: Senior React Developer" in text
    assert "Company: TechCorp" in text
    assert "Description: We are seeking" in text
    assert "Required Skills: react, typescript, redux, graphql" in text
    assert "Experience Level: Senior" in text
    assert "Employment: permanent" in text
    assert "Work Setup: remote" in text
    assert "Location: Remote Australia" in text


def test_build_job_embedding_text_long_description():
    """Test job embedding text truncates long descriptions."""
    long_description = "A" * 1000  # 1000 character description

    job = JobPosting(
        id=uuid4(),
        title="Developer",
        company="Company",
        description=long_description,
        role_category="engineering",
        required_skills=["python"],
        experience_level="Mid",
        employment_type="permanent",
        work_setup="remote",
        location="Remote"
    )

    text = build_job_embedding_text(job)

    # Description should be truncated to 500 chars + "..."
    assert len(text.split("Description: ")[1].split("\n")[0]) == 503


# ============================================================================
# EmbeddingService Tests
# ============================================================================

@pytest.mark.asyncio
async def test_generate_embedding_success():
    """Test successful embedding generation."""
    # Mock repositories
    candidate_repo = AsyncMock()
    job_repo = AsyncMock()

    # Mock OpenAI response
    mock_embedding = [0.1] * 3072
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=mock_embedding)]
    mock_response.usage.total_tokens = 150

    with patch('app.services.embedding_service.AsyncOpenAI') as mock_client:
        mock_client.return_value.embeddings.create = AsyncMock(return_value=mock_response)

        service = EmbeddingService(candidate_repo, job_repo)
        result = await service.generate_embedding("test text")

        assert len(result) == 3072
        assert result == mock_embedding
        mock_client.return_value.embeddings.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_embedding_rate_limit_retry():
    """Test embedding generation with rate limit retry."""
    candidate_repo = AsyncMock()
    job_repo = AsyncMock()

    # Mock OpenAI response (success on second attempt)
    mock_embedding = [0.1] * 3072
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=mock_embedding)]
    mock_response.usage.total_tokens = 150

    # Create proper RateLimitError mock
    mock_rate_limit_response = MagicMock()
    mock_rate_limit_response.status_code = 429
    rate_limit_error = RateLimitError(
        "Rate limit",
        response=mock_rate_limit_response,
        body={}
    )

    with patch('app.services.embedding_service.AsyncOpenAI') as mock_client:
        # First call fails with rate limit, second succeeds
        mock_client.return_value.embeddings.create = AsyncMock(
            side_effect=[rate_limit_error, mock_response]
        )

        service = EmbeddingService(candidate_repo, job_repo)
        result = await service.generate_embedding("test text")

        assert len(result) == 3072
        assert mock_client.return_value.embeddings.create.call_count == 2


@pytest.mark.asyncio
async def test_generate_embedding_rate_limit_exhausted():
    """Test embedding generation fails after max retries."""
    candidate_repo = AsyncMock()
    job_repo = AsyncMock()

    # Create proper RateLimitError mock
    mock_rate_limit_response = MagicMock()
    mock_rate_limit_response.status_code = 429
    rate_limit_error = RateLimitError(
        "Rate limit",
        response=mock_rate_limit_response,
        body={}
    )

    with patch('app.services.embedding_service.AsyncOpenAI') as mock_client:
        # All calls fail with rate limit
        mock_client.return_value.embeddings.create = AsyncMock(
            side_effect=rate_limit_error
        )

        service = EmbeddingService(candidate_repo, job_repo)

        with pytest.raises(RateLimitExceededError):
            await service.generate_embedding("test text")

        # Should attempt 3 times
        assert mock_client.return_value.embeddings.create.call_count == 3


@pytest.mark.asyncio
async def test_generate_embedding_timeout_error():
    """Test embedding generation handles timeout error."""
    candidate_repo = AsyncMock()
    job_repo = AsyncMock()

    with patch('app.services.embedding_service.AsyncOpenAI') as mock_client:
        mock_client.return_value.embeddings.create = AsyncMock(
            side_effect=APITimeoutError("Timeout")
        )

        service = EmbeddingService(candidate_repo, job_repo)

        with pytest.raises(OpenAIProviderError, match="timed out"):
            await service.generate_embedding("test text")


@pytest.mark.asyncio
async def test_generate_embedding_auth_error():
    """Test embedding generation handles auth error without retry."""
    candidate_repo = AsyncMock()
    job_repo = AsyncMock()

    # Create proper AuthenticationError mock
    mock_auth_response = MagicMock()
    mock_auth_response.status_code = 401
    auth_error = AuthenticationError(
        "Auth failed",
        response=mock_auth_response,
        body={}
    )

    with patch('app.services.embedding_service.AsyncOpenAI') as mock_client:
        mock_client.return_value.embeddings.create = AsyncMock(
            side_effect=auth_error
        )

        service = EmbeddingService(candidate_repo, job_repo)

        with pytest.raises(AuthenticationError):
            await service.generate_embedding("test text")

        # Should not retry on auth error
        assert mock_client.return_value.embeddings.create.call_count == 1


@pytest.mark.asyncio
async def test_batch_generate_embeddings_success():
    """Test successful batch embedding generation."""
    candidate_repo = AsyncMock()
    job_repo = AsyncMock()

    # Mock OpenAI batch response
    mock_embeddings = [[0.1] * 3072 for _ in range(10)]
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=emb) for emb in mock_embeddings]
    mock_response.usage.total_tokens = 500

    with patch('app.services.embedding_service.AsyncOpenAI') as mock_client:
        mock_client.return_value.embeddings.create = AsyncMock(return_value=mock_response)

        service = EmbeddingService(candidate_repo, job_repo)
        texts = ["text"] * 10

        result = await service.batch_generate_embeddings(texts)

        assert len(result) == 10
        assert all(len(emb) == 3072 for emb in result)
        mock_client.return_value.embeddings.create.assert_called_once()


@pytest.mark.asyncio
async def test_batch_generate_embeddings_size_validation():
    """Test batch generation rejects batches > 100."""
    candidate_repo = AsyncMock()
    job_repo = AsyncMock()

    service = EmbeddingService(candidate_repo, job_repo)
    texts = ["text"] * 101

    with pytest.raises(ValueError, match="Batch size must be <= 100"):
        await service.batch_generate_embeddings(texts)


@pytest.mark.asyncio
async def test_generate_candidate_embedding_not_found():
    """Test candidate embedding generation with non-existent candidate."""
    candidate_repo = AsyncMock()
    candidate_repo.get_by_id = AsyncMock(return_value=None)
    job_repo = AsyncMock()

    service = EmbeddingService(candidate_repo, job_repo)
    candidate_id = uuid4()

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await service.generate_candidate_embedding(candidate_id)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_generate_candidate_embedding_success():
    """Test successful candidate embedding generation and storage."""
    candidate_repo = AsyncMock()
    job_repo = AsyncMock()

    # Mock candidate
    candidate = Candidate(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        skills=["python", "react"],
        experience_years=5,
        job_preferences={"locations": ["Remote"]}
    )
    candidate_repo.get_by_id = AsyncMock(return_value=candidate)
    candidate_repo.update_embedding = AsyncMock()

    # Mock OpenAI response
    mock_embedding = [0.1] * 3072
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=mock_embedding)]
    mock_response.usage.total_tokens = 150

    with patch('app.services.embedding_service.AsyncOpenAI') as mock_client:
        mock_client.return_value.embeddings.create = AsyncMock(return_value=mock_response)

        service = EmbeddingService(candidate_repo, job_repo)
        result = await service.generate_candidate_embedding(candidate.id)

        assert len(result) == 3072
        candidate_repo.update_embedding.assert_called_once_with(candidate.id, mock_embedding)
