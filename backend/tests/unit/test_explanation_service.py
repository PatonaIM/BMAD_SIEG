"""Unit tests for ExplanationService."""
import json
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.candidate import Candidate
from app.models.job_posting import JobPosting
from app.services.explanation_service import ExplanationService


@pytest.mark.asyncio
async def test_generate_explanation_success():
    """Test successful explanation generation."""
    # Mock dependencies
    mock_openai = AsyncMock()
    mock_candidate_repo = AsyncMock()
    mock_job_repo = AsyncMock()
    mock_cache = AsyncMock()
    
    # Mock OpenAI response
    explanation_json = {
        "matching_factors": ["Skill 1 matches", "Skill 2 matches"],
        "missing_requirements": ["Gap 1"],
        "overall_reasoning": "Good match overall with strong technical alignment",
        "confidence_score": 0.85
    }
    mock_openai.generate_completion.return_value = json.dumps(explanation_json)
    
    # Mock candidate and job
    candidate_id = uuid4()
    job_id = uuid4()
    
    mock_candidate = Candidate(
        id=candidate_id,
        email="test@test.com",
        full_name="Test User",
        password_hash="hash",
        skills=["python", "react"],
        experience_years=5,
        job_preferences={"locations": ["Remote"], "employment_types": ["permanent"]}
    )
    mock_job = JobPosting(
        id=job_id,
        title="Senior Developer",
        company="TechCorp",
        description="Building scalable systems",
        required_skills=["python", "react"],
        experience_level="senior",
        employment_type="permanent",
        work_setup="remote",
        location="Sydney",
        salary_currency="AUD",
        role_category="engineering",
        tech_stack="Python"
    )
    
    mock_candidate_repo.get_by_id.return_value = mock_candidate
    mock_job_repo.get_by_id.return_value = mock_job
    mock_cache.get.return_value = None  # Cache miss
    
    # Execute
    service = ExplanationService(
        mock_openai, mock_candidate_repo, mock_job_repo, mock_cache
    )
    result = await service.generate_explanation(
        candidate_id=candidate_id,
        job_id=job_id,
        match_score=Decimal("85.0"),
        match_classification="Excellent",
        preference_matches={"location": True, "work_setup": True}
    )
    
    # Verify
    assert result["matching_factors"] == ["Skill 1 matches", "Skill 2 matches"]
    assert result["missing_requirements"] == ["Gap 1"]
    assert result["confidence_score"] == 0.85
    mock_cache.set.assert_called_once()
    mock_openai.generate_completion.assert_called_once()


@pytest.mark.asyncio
async def test_generate_explanation_cache_hit():
    """Test cached explanation retrieval."""
    mock_cache = AsyncMock()
    cached_explanation = {
        "matching_factors": ["Cached 1"],
        "missing_requirements": [],
        "overall_reasoning": "Cached result",
        "confidence_score": 0.9
    }
    mock_cache.get.return_value = cached_explanation
    
    service = ExplanationService(
        AsyncMock(), AsyncMock(), AsyncMock(), mock_cache
    )
    result = await service.generate_explanation(
        candidate_id=uuid4(),
        job_id=uuid4(),
        match_score=Decimal("90.0"),
        match_classification="Excellent",
        preference_matches={}
    )
    
    # Should return cached result without calling OpenAI
    assert result == cached_explanation


@pytest.mark.asyncio
async def test_generate_explanation_match_too_low():
    """Test explanation blocked for low match scores."""
    service = ExplanationService(
        AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock()
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await service.generate_explanation(
            candidate_id=uuid4(),
            job_id=uuid4(),
            match_score=Decimal("35.0"),  # Below 40% threshold
            match_classification="Poor",
            preference_matches={}
        )
    
    assert exc_info.value.status_code == 400
    assert "≥40%" in exc_info.value.detail


@pytest.mark.asyncio
async def test_generate_explanation_candidate_not_found():
    """Test explanation fails when candidate not found."""
    mock_candidate_repo = AsyncMock()
    mock_candidate_repo.get_by_id.return_value = None
    mock_cache = AsyncMock()
    mock_cache.get.return_value = None
    
    service = ExplanationService(
        AsyncMock(), mock_candidate_repo, AsyncMock(), mock_cache
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await service.generate_explanation(
            candidate_id=uuid4(),
            job_id=uuid4(),
            match_score=Decimal("80.0"),
            match_classification="Great",
            preference_matches={}
        )
    
    assert exc_info.value.status_code == 404
    assert "Candidate not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_generate_explanation_job_not_found():
    """Test explanation fails when job not found."""
    mock_candidate_repo = AsyncMock()
    mock_candidate_repo.get_by_id.return_value = Candidate(
        id=uuid4(),
        email="test@test.com",
        full_name="Test",
        password_hash="hash"
    )
    
    mock_job_repo = AsyncMock()
    mock_job_repo.get_by_id.return_value = None
    
    mock_cache = AsyncMock()
    mock_cache.get.return_value = None
    
    service = ExplanationService(
        AsyncMock(), mock_candidate_repo, mock_job_repo, mock_cache
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await service.generate_explanation(
            candidate_id=uuid4(),
            job_id=uuid4(),
            match_score=Decimal("80.0"),
            match_classification="Great",
            preference_matches={}
        )
    
    assert exc_info.value.status_code == 404
    assert "Job posting not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_generate_explanation_json_parse_error():
    """Test explanation fails when GPT returns invalid JSON."""
    mock_openai = AsyncMock()
    mock_openai.generate_completion.return_value = "Not valid JSON"
    
    mock_candidate_repo = AsyncMock()
    mock_candidate_repo.get_by_id.return_value = Candidate(
        id=uuid4(),
        email="test@test.com",
        full_name="Test",
        password_hash="hash",
        skills=["python"]
    )
    
    mock_job_repo = AsyncMock()
    mock_job_repo.get_by_id.return_value = JobPosting(
        id=uuid4(),
        title="Dev",
        company="Corp",
        description="Job",
        role_category="engineering",
        tech_stack="Python",
        employment_type="permanent",
        work_setup="remote",
        location="Sydney",
        salary_currency="AUD"
    )
    
    mock_cache = AsyncMock()
    mock_cache.get.return_value = None
    
    service = ExplanationService(
        mock_openai, mock_candidate_repo, mock_job_repo, mock_cache
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await service.generate_explanation(
            candidate_id=uuid4(),
            job_id=uuid4(),
            match_score=Decimal("80.0"),
            match_classification="Great",
            preference_matches={}
        )
    
    assert exc_info.value.status_code == 500
    assert "Failed to parse explanation" in exc_info.value.detail


@pytest.mark.asyncio
async def test_generate_explanation_invalid_structure():
    """Test explanation fails when GPT returns incomplete JSON structure."""
    mock_openai = AsyncMock()
    # Missing required fields
    incomplete_json = {
        "matching_factors": ["Factor 1"],
        # Missing missing_requirements, overall_reasoning, confidence_score
    }
    mock_openai.generate_completion.return_value = json.dumps(incomplete_json)
    
    mock_candidate_repo = AsyncMock()
    mock_candidate_repo.get_by_id.return_value = Candidate(
        id=uuid4(),
        email="test@test.com",
        full_name="Test",
        password_hash="hash",
        skills=["python"]
    )
    
    mock_job_repo = AsyncMock()
    mock_job_repo.get_by_id.return_value = JobPosting(
        id=uuid4(),
        title="Dev",
        company="Corp",
        description="Job",
        role_category="engineering",
        tech_stack="Python",
        employment_type="permanent",
        work_setup="remote",
        location="Sydney",
        salary_currency="AUD"
    )
    
    mock_cache = AsyncMock()
    mock_cache.get.return_value = None
    
    service = ExplanationService(
        mock_openai, mock_candidate_repo, mock_job_repo, mock_cache
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await service.generate_explanation(
            candidate_id=uuid4(),
            job_id=uuid4(),
            match_score=Decimal("80.0"),
            match_classification="Great",
            preference_matches={}
        )
    
    assert exc_info.value.status_code == 500


def test_build_explanation_prompt():
    """Test explanation prompt building with all fields."""
    candidate = Candidate(
        id=uuid4(),
        email="test@test.com",
        full_name="Test User",
        password_hash="hash",
        skills=["python", "react", "typescript"],
        experience_years=5,
        job_preferences={
            "locations": ["Sydney", "Remote"],
            "employment_types": ["permanent"],
            "work_setups": ["remote", "hybrid"],
            "salary_min": 100000,
            "salary_max": 150000,
            "role_categories": ["engineering"]
        }
    )
    
    job = JobPosting(
        id=uuid4(),
        title="Senior Full Stack Developer",
        company="TechCorp Australia",
        description="We are building scalable cloud applications using Python and React. Join our remote-first team!",
        required_skills=["python", "react", "typescript", "aws"],
        experience_level="senior",
        employment_type="permanent",
        work_setup="remote",
        location="Sydney",
        salary_min=120000,
        salary_max=160000,
        salary_currency="AUD",
        role_category="engineering",
        tech_stack="Python"
    )
    
    service = ExplanationService(
        AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock()
    )
    
    prompt = service.build_explanation_prompt(
        candidate=candidate,
        job=job,
        match_score=Decimal("87.5"),
        match_classification="Excellent",
        preference_matches={
            "location": True,
            "work_setup": True,
            "employment_type": True,
            "salary": True
        }
    )
    
    # Verify all key data is in prompt
    assert "python, react, typescript" in prompt.lower()
    assert "5 years" in prompt
    assert "Senior Full Stack Developer" in prompt
    assert "TechCorp Australia" in prompt
    assert "87.5%" in prompt
    assert "Excellent" in prompt
    assert "✅ Yes" in prompt  # All preferences match
    assert "Remote" in prompt


def test_build_explanation_prompt_minimal_data():
    """Test explanation prompt building with minimal candidate data."""
    candidate = Candidate(
        id=uuid4(),
        email="test@test.com",
        full_name="Test User",
        password_hash="hash",
        skills=None,
        experience_years=None,
        job_preferences=None
    )
    
    job = JobPosting(
        id=uuid4(),
        title="Developer",
        company="Corp",
        description="Short description",
        role_category="engineering",
        tech_stack="Python",
        employment_type="permanent",
        work_setup="remote",
        location="Sydney",
        salary_currency="AUD"
    )
    
    service = ExplanationService(
        AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock()
    )
    
    prompt = service.build_explanation_prompt(
        candidate=candidate,
        job=job,
        match_score=Decimal("50.0"),
        match_classification="Fair",
        preference_matches={}
    )
    
    # Verify "Not specified" fallbacks are used
    assert "None listed" in prompt or "Not specified" in prompt
    assert "Fair" in prompt
    assert "50.0%" in prompt
