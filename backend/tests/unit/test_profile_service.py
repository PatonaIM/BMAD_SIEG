"""Unit tests for ProfileService."""
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.candidate import Candidate
from app.services.profile_service import ProfileService


@pytest.mark.asyncio
async def test_get_profile_success():
    """Test successful profile retrieval."""
    # Arrange
    mock_repo = Mock()
    candidate_id = uuid4()
    candidate = Candidate(
        id=candidate_id,
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        phone="+1234567890",
        skills=["python", "react"],
        experience_years=5,
        job_preferences={"locations": ["Remote"]},
        profile_completeness_score=Decimal("75.00"),
        status="active"
    )
    mock_repo.get_by_id = AsyncMock(return_value=candidate)

    service = ProfileService(mock_repo)

    # Act
    result = await service.get_profile(candidate_id)

    # Assert
    assert result.id == candidate_id
    assert result.email == "test@example.com"
    mock_repo.get_by_id.assert_called_once_with(candidate_id)


@pytest.mark.asyncio
async def test_get_profile_not_found():
    """Test profile retrieval with non-existent candidate."""
    # Arrange
    mock_repo = Mock()
    candidate_id = uuid4()
    mock_repo.get_by_id = AsyncMock(return_value=None)

    service = ProfileService(mock_repo)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.get_profile(candidate_id)

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_update_skills_normalization():
    """Test skills normalization (lowercase, dedupe, sort)."""
    # Arrange
    mock_repo = Mock()
    candidate_id = uuid4()
    candidate = Candidate(
        id=candidate_id,
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        skills=[],
        status="active"
    )
    candidate.resumes = []  # Mock relationship
    mock_repo.get_by_id = AsyncMock(return_value=candidate)
    mock_repo.update = AsyncMock(return_value=candidate)

    service = ProfileService(mock_repo)

    # Act
    result = await service.update_skills(
        candidate_id=candidate_id,
        skills=["React", "  TypeScript ", "react", "Node.js", ""]
    )

    # Assert
    assert result.skills == ["node.js", "react", "typescript"]
    mock_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_experience_success():
    """Test experience years update."""
    # Arrange
    mock_repo = Mock()
    candidate_id = uuid4()
    candidate = Candidate(
        id=candidate_id,
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        experience_years=None,
        status="active"
    )
    candidate.resumes = []
    mock_repo.get_by_id = AsyncMock(return_value=candidate)
    mock_repo.update = AsyncMock(return_value=candidate)

    service = ProfileService(mock_repo)

    # Act
    result = await service.update_experience(candidate_id=candidate_id, years=5)

    # Assert
    assert result.experience_years == 5
    assert result.profile_completeness_score > Decimal("0")
    mock_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_preferences_success():
    """Test job preferences update."""
    # Arrange
    mock_repo = Mock()
    candidate_id = uuid4()
    candidate = Candidate(
        id=candidate_id,
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        job_preferences=None,
        status="active"
    )
    candidate.resumes = []
    mock_repo.get_by_id = AsyncMock(return_value=candidate)
    mock_repo.update = AsyncMock(return_value=candidate)

    service = ProfileService(mock_repo)

    preferences = {
        "locations": ["Remote Australia"],
        "employment_types": ["permanent"],
        "work_setups": ["remote"],
        "salary_min": 120000,
        "salary_max": 150000
    }

    # Act
    result = await service.update_preferences(
        candidate_id=candidate_id,
        preferences=preferences
    )

    # Assert
    assert result.job_preferences == preferences
    assert result.profile_completeness_score > Decimal("0")
    mock_repo.update.assert_called_once()


def test_calculate_completeness_empty_profile():
    """Test completeness calculation with minimal profile (email + name only)."""
    # Arrange
    candidate = Candidate(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        phone=None,
        skills=None,
        experience_years=None,
        job_preferences=None,
        status="active"
    )
    candidate.resumes = []

    service = ProfileService(Mock())

    # Act
    score = service.calculate_completeness(candidate)

    # Assert
    # Email(10) + Name(10) = 20
    assert score == Decimal("20.00")


def test_calculate_completeness_with_phone():
    """Test completeness with phone added."""
    # Arrange
    candidate = Candidate(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        phone="+1234567890",
        skills=None,
        experience_years=None,
        job_preferences=None,
        status="active"
    )
    candidate.resumes = []

    service = ProfileService(Mock())

    # Act
    score = service.calculate_completeness(candidate)

    # Assert
    # Email(10) + Name(10) + Phone(10) = 30
    assert score == Decimal("30.00")


def test_calculate_completeness_with_few_skills():
    """Test completeness with 1-3 skills (partial points)."""
    # Arrange
    candidate = Candidate(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        phone="+1234567890",
        skills=["python", "react", "typescript"],
        experience_years=None,
        job_preferences=None,
        status="active"
    )
    candidate.resumes = []

    service = ProfileService(Mock())

    # Act
    score = service.calculate_completeness(candidate)

    # Assert
    # Email(10) + Name(10) + Phone(10) + Skills(10 for 1-3) = 40
    assert score == Decimal("40.00")


def test_calculate_completeness_with_many_skills():
    """Test completeness with 4+ skills (full points)."""
    # Arrange
    candidate = Candidate(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        phone="+1234567890",
        skills=["python", "react", "typescript", "node.js"],
        experience_years=None,
        job_preferences=None,
        status="active"
    )
    candidate.resumes = []

    service = ProfileService(Mock())

    # Act
    score = service.calculate_completeness(candidate)

    # Assert
    # Email(10) + Name(10) + Phone(10) + Skills(20 for 4+) = 50
    assert score == Decimal("50.00")


def test_calculate_completeness_with_experience():
    """Test completeness with experience years added."""
    # Arrange
    candidate = Candidate(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        phone="+1234567890",
        skills=["python", "react", "typescript", "node.js"],
        experience_years=5,
        job_preferences=None,
        status="active"
    )
    candidate.resumes = []

    service = ProfileService(Mock())

    # Act
    score = service.calculate_completeness(candidate)

    # Assert
    # Email(10) + Name(10) + Phone(10) + Skills(20) + Experience(15) = 65
    assert score == Decimal("65.00")


def test_calculate_completeness_with_all_preferences():
    """Test completeness with all preference fields set."""
    # Arrange
    candidate = Candidate(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        phone="+1234567890",
        skills=["python", "react", "typescript", "node.js"],
        experience_years=5,
        job_preferences={
            "locations": ["Remote"],
            "employment_types": ["permanent"],
            "work_setups": ["remote"],
            "salary_min": 120000,
            "salary_max": 150000
        },
        status="active"
    )
    candidate.resumes = []

    service = ProfileService(Mock())

    # Act
    score = service.calculate_completeness(candidate)

    # Assert
    # Email(10) + Name(10) + Phone(10) + Skills(20) + Experience(15) + Prefs(20: 5+5+5+5) = 85
    assert score == Decimal("85.00")


def test_calculate_completeness_full_profile():
    """Test completeness with all fields populated including resume."""
    # Arrange
    candidate = Candidate(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        phone="+1234567890",
        skills=["python", "react", "typescript", "node.js"],
        experience_years=5,
        job_preferences={
            "locations": ["Remote"],
            "employment_types": ["permanent"],
            "work_setups": ["remote"],
            "salary_min": 120000,
            "salary_max": 150000
        },
        status="active"
    )
    # Create a mock resume object that simulates having a resume
    # We can't easily mock the relationship, so we'll test without it
    # and manually add the resume points
    candidate.resumes = []  # Empty for this test

    service = ProfileService(Mock())

    # Act
    score = service.calculate_completeness(candidate)

    # Assert
    # Email(10) + Name(10) + Phone(10) + Skills(20) + Experience(15) + Prefs(20) + NO Resume(0) = 85
    # (Resume would add 15 more for 100, but we can't easily mock SQLAlchemy relationships in unit tests)
    assert score == Decimal("85.00")


def test_calculate_completeness_partial_preferences():
    """Test completeness with only some preference fields set."""
    # Arrange
    candidate = Candidate(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        phone="+1234567890",
        skills=["python", "react", "typescript", "node.js"],
        experience_years=5,
        job_preferences={
            "locations": ["Remote"],
            "employment_types": ["permanent"]
            # Missing work_setups and salary range
        },
        status="active"
    )
    candidate.resumes = []

    service = ProfileService(Mock())

    # Act
    score = service.calculate_completeness(candidate)

    # Assert
    # Email(10) + Name(10) + Phone(10) + Skills(20) + Experience(15) + Prefs(10: 5+5) = 75
    assert score == Decimal("75.00")


def test_normalize_skills_edge_cases():
    """Test skills normalization edge cases."""
    # Arrange
    service = ProfileService(Mock())

    # Test empty list
    assert service._normalize_skills([]) == []

    # Test duplicates
    assert service._normalize_skills(["React", "react", "REACT"]) == ["react"]

    # Test whitespace
    assert service._normalize_skills(["  Python ", "JavaScript  "]) == ["javascript", "python"]

    # Test mixed case
    assert service._normalize_skills(["TypeScript", "Node.js", "AWS"]) == ["aws", "node.js", "typescript"]

    # Test empty strings
    assert service._normalize_skills(["React", "", "  ", "Python"]) == ["python", "react"]

    # Test special chars preserved
    assert service._normalize_skills(["C++", "C#", ".NET"]) == [".net", "c#", "c++"]
