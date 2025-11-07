"""Unit tests for MatchingService."""
import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from fastapi import HTTPException

from app.models.candidate import Candidate
from app.models.job_posting import JobPosting
from app.schemas.matching import JobMatchListResponse
from app.services.matching_service import MatchingService


@pytest.fixture
def mock_matching_repo():
    """Mock MatchingRepository."""
    return AsyncMock()


@pytest.fixture
def mock_profile_service():
    """Mock ProfileService."""
    return AsyncMock()


@pytest.fixture
def matching_service(mock_matching_repo, mock_profile_service):
    """Create MatchingService with mocked dependencies."""
    return MatchingService(mock_matching_repo, mock_profile_service)


@pytest.fixture
def candidate_with_complete_profile():
    """Candidate with complete profile and preferences."""
    return Candidate(
        id=uuid4(),
        email="test@example.com",
        full_name="Test Candidate",
        password_hash="hashed",
        profile_completeness_score=Decimal("75.00"),
        profile_embedding=[0.1] * 3072,
        job_preferences={
            "locations": ["Sydney", "Melbourne"],
            "work_setups": ["remote", "hybrid"],
            "employment_types": ["permanent"],
            "salary_min": 80000,
            "salary_max": 120000
        }
    )


@pytest.fixture
def candidate_incomplete_profile():
    """Candidate with incomplete profile."""
    return Candidate(
        id=uuid4(),
        email="incomplete@example.com",
        full_name="Incomplete User",
        password_hash="hashed",
        profile_completeness_score=Decimal("30.00"),  # Below threshold
        profile_embedding=None
    )


@pytest.fixture
def candidate_no_embedding():
    """Candidate with complete profile but no embedding."""
    return Candidate(
        id=uuid4(),
        email="noembedding@example.com",
        full_name="No Embedding User",
        password_hash="hashed",
        profile_completeness_score=Decimal("60.00"),
        profile_embedding=None  # Missing embedding
    )


@pytest.fixture
def sample_job():
    """Sample job posting."""
    return JobPosting(
        id=uuid4(),
        title="Senior Python Developer",
        company="TechCorp",
        description="Building scalable systems",
        role_category="engineering",
        tech_stack="Python",
        employment_type="permanent",
        work_setup="remote",
        location="Sydney",
        salary_min=Decimal("100000"),
        salary_max=Decimal("140000"),
        salary_currency="AUD",
        required_skills=["Python", "FastAPI"],
        experience_level="senior",
        status="active",
        is_cancelled=False,
        job_embedding=[0.1] * 3072
    )


# Test check_preference_matches
def test_check_preference_matches_all_match(matching_service, sample_job):
    """Test preference matching when all preferences match."""
    preferences = {
        "locations": ["Sydney", "Melbourne"],
        "work_setups": ["remote", "hybrid"],
        "employment_types": ["permanent"],
        "salary_min": 80000,
        "salary_max": 120000
    }
    
    matches = matching_service.check_preference_matches(sample_job, preferences)
    
    assert matches["location"] is True
    assert matches["work_setup"] is True
    assert matches["employment_type"] is True
    assert matches["salary"] is True


def test_check_preference_matches_partial(matching_service, sample_job):
    """Test preference matching with partial matches."""
    # Change job to onsite so location won't auto-match
    sample_job.work_setup = "onsite"
    
    preferences = {
        "locations": ["Brisbane"],  # Won't match (job is in Sydney)
        "work_setups": ["remote"],  # Won't match (job is onsite)
        "employment_types": ["contract"],  # Won't match
        "salary_min": 150000,  # Won't match (no overlap - job max is 140k)
        "salary_max": 200000
    }
    
    matches = matching_service.check_preference_matches(sample_job, preferences)
    
    assert matches["location"] is False
    assert matches["work_setup"] is False
    assert matches["employment_type"] is False
    assert matches["salary"] is False


def test_check_preference_matches_remote_job(matching_service, sample_job):
    """Test that remote jobs match any location preference."""
    sample_job.work_setup = "remote"
    preferences = {
        "locations": ["Perth"],  # Different city, but job is remote
    }
    
    matches = matching_service.check_preference_matches(sample_job, preferences)
    
    assert matches["location"] is True


def test_check_preference_matches_no_preferences(matching_service, sample_job):
    """Test matching with no candidate preferences."""
    matches = matching_service.check_preference_matches(sample_job, None)
    
    assert matches == {}


def test_check_preference_matches_no_job_salary(matching_service, sample_job):
    """Test salary matching when job has no salary info."""
    sample_job.salary_min = None
    sample_job.salary_max = None
    
    preferences = {
        "salary_min": 80000,
        "salary_max": 120000
    }
    
    matches = matching_service.check_preference_matches(sample_job, preferences)
    
    assert matches["salary"] is False


# Test calculate_match_score
def test_calculate_match_score_perfect(matching_service):
    """Test score calculation with perfect similarity and all preferences matched."""
    similarity = 1.0
    preference_matches = {
        "location": True,
        "work_setup": True,
        "employment_type": True,
        "salary": True
    }
    
    score = matching_service.calculate_match_score(similarity, preference_matches)
    
    # (1.0 * 0.7) + (4/4 * 0.3) * 100 = 100
    assert score == Decimal("100.00")


def test_calculate_match_score_no_preferences(matching_service):
    """Test score calculation with no preferences (should treat as perfect preference match)."""
    similarity = 0.85
    preference_matches = {}
    
    score = matching_service.calculate_match_score(similarity, preference_matches)
    
    # (0.85 * 0.7) + (1.0 * 0.3) * 100 = 89.5
    assert score == Decimal("89.50")


def test_calculate_match_score_partial_preferences(matching_service):
    """Test score calculation with partial preference matches."""
    similarity = 0.80
    preference_matches = {
        "location": True,
        "work_setup": True,
        "employment_type": False,
        "salary": False
    }
    
    score = matching_service.calculate_match_score(similarity, preference_matches)
    
    # (0.80 * 0.7) + (2/4 * 0.3) * 100 = 71.0
    assert score == Decimal("71.00")


def test_calculate_match_score_low_similarity(matching_service):
    """Test score calculation with low similarity."""
    similarity = 0.30
    preference_matches = {
        "location": True,
        "work_setup": True
    }
    
    score = matching_service.calculate_match_score(similarity, preference_matches)
    
    # (0.30 * 0.7) + (2/2 * 0.3) * 100 = 51.0
    assert score == Decimal("51.00")


# Test classify_match
def test_classify_match_excellent(matching_service):
    """Test classification for Excellent tier."""
    assert matching_service.classify_match(Decimal("85.00")) == "Excellent"
    assert matching_service.classify_match(Decimal("95.00")) == "Excellent"
    assert matching_service.classify_match(Decimal("100.00")) == "Excellent"


def test_classify_match_great(matching_service):
    """Test classification for Great tier."""
    assert matching_service.classify_match(Decimal("70.00")) == "Great"
    assert matching_service.classify_match(Decimal("80.00")) == "Great"
    assert matching_service.classify_match(Decimal("84.99")) == "Great"


def test_classify_match_good(matching_service):
    """Test classification for Good tier."""
    assert matching_service.classify_match(Decimal("55.00")) == "Good"
    assert matching_service.classify_match(Decimal("65.00")) == "Good"
    assert matching_service.classify_match(Decimal("69.99")) == "Good"


def test_classify_match_fair(matching_service):
    """Test classification for Fair tier."""
    assert matching_service.classify_match(Decimal("40.00")) == "Fair"
    assert matching_service.classify_match(Decimal("50.00")) == "Fair"
    assert matching_service.classify_match(Decimal("54.99")) == "Fair"


def test_classify_match_poor(matching_service):
    """Test classification for Poor tier."""
    assert matching_service.classify_match(Decimal("0.00")) == "Poor"
    assert matching_service.classify_match(Decimal("20.00")) == "Poor"
    assert matching_service.classify_match(Decimal("39.99")) == "Poor"


# Test get_job_matches
@pytest.mark.asyncio
async def test_get_job_matches_success(
    matching_service,
    mock_matching_repo,
    candidate_with_complete_profile,
    sample_job
):
    """Test successful job matching flow."""
    # Mock repository responses
    mock_matching_repo.get_vector_matches.return_value = [
        {
            "job": sample_job,
            "similarity_score": 0.85
        }
    ]
    mock_matching_repo.count_matching_jobs.return_value = 1
    
    # Execute
    result = await matching_service.get_job_matches(
        candidate=candidate_with_complete_profile,
        page=1,
        page_size=20
    )
    
    # Verify
    assert isinstance(result, JobMatchListResponse)
    assert len(result.matches) == 1
    assert result.total_count == 1
    assert result.page == 1
    assert result.page_size == 20
    assert result.has_more is False
    
    # Verify match details
    match = result.matches[0]
    assert match.id == sample_job.id
    assert match.title == sample_job.title
    assert match.match_score >= 70  # Should be high with 0.85 similarity
    assert match.match_classification in ["Excellent", "Great"]
    assert match.similarity_score == Decimal("0.8500")


@pytest.mark.asyncio
async def test_get_job_matches_incomplete_profile(
    matching_service,
    candidate_incomplete_profile
):
    """Test matching blocked for incomplete profiles."""
    with pytest.raises(HTTPException) as exc_info:
        await matching_service.get_job_matches(
            candidate=candidate_incomplete_profile
        )
    
    assert exc_info.value.status_code == 403
    assert "profile completeness" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_get_job_matches_no_embedding(
    matching_service,
    candidate_no_embedding
):
    """Test matching blocked when embedding is missing."""
    with pytest.raises(HTTPException) as exc_info:
        await matching_service.get_job_matches(
            candidate=candidate_no_embedding
        )
    
    assert exc_info.value.status_code == 400
    assert "embedding" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_get_job_matches_pagination(
    matching_service,
    mock_matching_repo,
    candidate_with_complete_profile,
    sample_job
):
    """Test pagination logic."""
    # Mock 50 total jobs, return 20 for page 1
    mock_jobs = [
        {"job": sample_job, "similarity_score": 0.80 - (i * 0.01)}
        for i in range(20)
    ]
    mock_matching_repo.get_vector_matches.return_value = mock_jobs
    mock_matching_repo.count_matching_jobs.return_value = 50
    
    # Get page 1
    result = await matching_service.get_job_matches(
        candidate=candidate_with_complete_profile,
        page=1,
        page_size=20
    )
    
    assert len(result.matches) == 20
    assert result.total_count == 50
    assert result.has_more is True
    
    # Verify repository called with correct offset
    mock_matching_repo.get_vector_matches.assert_called_once()
    call_kwargs = mock_matching_repo.get_vector_matches.call_args.kwargs
    assert call_kwargs["offset"] == 0  # Page 1, offset 0


@pytest.mark.asyncio
async def test_get_job_matches_sorting(
    matching_service,
    mock_matching_repo,
    candidate_with_complete_profile
):
    """Test that matches are sorted by score descending."""
    # Create jobs with different similarity scores
    jobs = []
    for i, similarity in enumerate([0.60, 0.90, 0.75, 0.85]):
        job = JobPosting(
            id=uuid4(),
            title=f"Job {i}",
            company="Company",
            description="Description",
            role_category="engineering",
            employment_type="permanent",
            work_setup="remote",
            location="Sydney",
            salary_currency="AUD",
            required_skills=[],
            experience_level="mid",
            status="active",
            is_cancelled=False,
            job_embedding=[0.1] * 3072
        )
        jobs.append({"job": job, "similarity_score": similarity})
    
    mock_matching_repo.get_vector_matches.return_value = jobs
    mock_matching_repo.count_matching_jobs.return_value = 4
    
    # Execute
    result = await matching_service.get_job_matches(
        candidate=candidate_with_complete_profile
    )
    
    # Verify sorting (highest scores first)
    scores = [m.match_score for m in result.matches]
    assert scores == sorted(scores, reverse=True)
    
    # Highest similarity (0.90) should be first
    assert result.matches[0].title == "Job 1"
