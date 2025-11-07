"""Unit tests for ResumeParsingService."""
import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.core.exceptions import OpenAIProviderError
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.schemas.resume import ResumeParsedDataSchema
from app.services.resume_parsing_service import ResumeParsingService


@pytest.fixture
def mock_openai_provider():
    """Create mock OpenAI provider."""
    mock = Mock()
    mock.generate_completion = AsyncMock()
    return mock


@pytest.fixture
def mock_resume_repo():
    """Create mock resume repository."""
    mock = Mock()
    mock.get_by_id = AsyncMock()
    mock.update_parsing_status = AsyncMock()
    return mock


@pytest.fixture
def mock_candidate_repo():
    """Create mock candidate repository."""
    mock = Mock()
    mock.get_by_id = AsyncMock()
    mock.db = Mock()
    mock.db.commit = AsyncMock()
    mock.db.refresh = AsyncMock()
    return mock


@pytest.fixture
def sample_resume():
    """Create sample resume object."""
    resume_id = uuid4()
    candidate_id = uuid4()
    return Resume(
        id=resume_id,
        candidate_id=candidate_id,
        file_url="https://example.com/resume.pdf",
        file_name="resume.pdf",
        file_size=1024,
        parsing_status="pending",
    )


@pytest.fixture
def sample_candidate():
    """Create sample candidate object."""
    candidate_id = uuid4()
    return Candidate(
        id=candidate_id,
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed",
        status="active",
        skills=None,
        experience_years=None,
    )


@pytest.fixture
def parsing_service(mock_openai_provider, mock_resume_repo, mock_candidate_repo):
    """Create ResumeParsingService with mocked dependencies."""
    with patch.object(ResumeParsingService, '_load_prompt_template', return_value=None):
        service = ResumeParsingService(
            openai_provider=mock_openai_provider,
            resume_repo=mock_resume_repo,
            candidate_repo=mock_candidate_repo,
        )
        service.prompt_template = "Resume text: {resume_text}"
        return service


@pytest.mark.asyncio
async def test_parse_resume_success(
    parsing_service, mock_openai_provider, mock_resume_repo, mock_candidate_repo, 
    sample_resume, sample_candidate
):
    """Test successful resume parsing."""
    # Arrange
    resume_text = "John Doe - Senior Python Developer with 5 years experience"
    
    mock_response = json.dumps({
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "experience_years": 5,
        "education": ["Bachelor of Computer Science"],
        "past_roles": ["Senior Python Developer", "Junior Developer"]
    })
    
    mock_openai_provider.generate_completion.return_value = mock_response
    mock_resume_repo.get_by_id.return_value = sample_resume
    mock_candidate_repo.get_by_id.return_value = sample_candidate
    
    # Act
    result = await parsing_service.parse_resume_text(sample_resume.id, resume_text)
    
    # Assert
    assert isinstance(result, ResumeParsedDataSchema)
    assert result.experience_years == 5
    assert "python" in result.skills  # Should be normalized to lowercase
    assert "fastapi" in result.skills
    assert len(result.education) == 1
    assert len(result.past_roles) == 2
    
    # Verify status updates
    assert mock_resume_repo.update_parsing_status.call_count == 2
    # First call: set to processing
    processing_call = mock_resume_repo.update_parsing_status.call_args_list[0]
    assert processing_call[1]["status"] == "processing"
    # Second call: set to completed
    completed_call = mock_resume_repo.update_parsing_status.call_args_list[1]
    assert completed_call[1]["status"] == "completed"
    assert completed_call[1]["parsed_data"] is not None


@pytest.mark.asyncio
async def test_parse_resume_empty_text(
    parsing_service, mock_resume_repo, sample_resume
):
    """Test parsing fails with empty resume text."""
    # Arrange
    mock_resume_repo.get_by_id.return_value = sample_resume
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        await parsing_service.parse_resume_text(sample_resume.id, "")
    
    assert "No text content to parse" in str(exc_info.value)
    
    # Verify status set to failed
    mock_resume_repo.update_parsing_status.assert_called_once()
    call_args = mock_resume_repo.update_parsing_status.call_args
    assert call_args[1]["status"] == "failed"
    assert "error" in call_args[1]["parsed_data"]


@pytest.mark.asyncio
async def test_parse_resume_experience_years_validation(
    parsing_service, mock_openai_provider, mock_resume_repo, mock_candidate_repo,
    sample_resume, sample_candidate
):
    """Test experience_years validation (0-50 range)."""
    # Arrange
    resume_text = "Senior developer with lots of experience"
    
    # Test with valid value at boundary
    mock_response = json.dumps({
        "skills": ["Python"],
        "experience_years": 50,
        "education": [],
        "past_roles": []
    })
    
    mock_openai_provider.generate_completion.return_value = mock_response
    mock_resume_repo.get_by_id.return_value = sample_resume
    mock_candidate_repo.get_by_id.return_value = sample_candidate
    
    # Act
    result = await parsing_service.parse_resume_text(sample_resume.id, resume_text)
    
    # Assert
    assert result.experience_years == 50


@pytest.mark.asyncio
async def test_parse_resume_skill_deduplication(
    parsing_service, mock_openai_provider, mock_resume_repo, mock_candidate_repo,
    sample_resume, sample_candidate
):
    """Test skill deduplication and normalization."""
    # Arrange
    resume_text = "Developer with Python, PYTHON, python skills"
    
    mock_response = json.dumps({
        "skills": ["Python", "PYTHON", "python", "FastAPI"],
        "experience_years": 3,
        "education": [],
        "past_roles": []
    })
    
    mock_openai_provider.generate_completion.return_value = mock_response
    mock_resume_repo.get_by_id.return_value = sample_resume
    mock_candidate_repo.get_by_id.return_value = sample_candidate
    
    # Act
    result = await parsing_service.parse_resume_text(sample_resume.id, resume_text)
    
    # Assert
    # Should deduplicate and normalize to lowercase
    assert result.skills.count("python") == 1
    assert "fastapi" in result.skills
    assert len(result.skills) == 2


@pytest.mark.asyncio
async def test_parse_resume_openai_timeout(
    parsing_service, mock_openai_provider, mock_resume_repo, sample_resume
):
    """Test timeout handling with retry logic."""
    # Arrange
    import asyncio
    
    mock_resume_repo.get_by_id.return_value = sample_resume
    mock_openai_provider.generate_completion.side_effect = asyncio.TimeoutError()
    
    # Act & Assert
    with pytest.raises(OpenAIProviderError) as exc_info:
        await parsing_service.parse_resume_text(sample_resume.id, "Resume text")
    
    assert "timeout" in str(exc_info.value).lower()
    
    # Verify retry attempts (initial + 3 retries = 4 total status updates)
    # 1 for processing, 1 for failed
    assert mock_resume_repo.update_parsing_status.call_count == 2
    
    # Verify final status is failed
    final_call = mock_resume_repo.update_parsing_status.call_args_list[-1]
    assert final_call[1]["status"] == "failed"


@pytest.mark.asyncio
async def test_parse_resume_invalid_json_response(
    parsing_service, mock_openai_provider, mock_resume_repo, mock_candidate_repo,
    sample_resume, sample_candidate
):
    """Test handling of invalid JSON response."""
    # Arrange
    resume_text = "Sample resume"
    
    # Return invalid JSON
    mock_openai_provider.generate_completion.return_value = "This is not JSON"
    mock_resume_repo.get_by_id.return_value = sample_resume
    
    # Act & Assert
    with pytest.raises(OpenAIProviderError) as exc_info:
        await parsing_service.parse_resume_text(sample_resume.id, resume_text)
    
    assert "Invalid JSON" in str(exc_info.value)


@pytest.mark.asyncio
async def test_auto_populate_candidate_profile(
    parsing_service, mock_candidate_repo, sample_candidate
):
    """Test auto-population of candidate profile."""
    # Arrange
    parsed_data = ResumeParsedDataSchema(
        skills=["python", "react", "postgresql"],
        experience_years=7,
        education=["Bachelor of Science"],
        past_roles=["Senior Engineer"]
    )
    
    mock_candidate_repo.get_by_id.return_value = sample_candidate
    
    # Act
    await parsing_service._auto_populate_candidate_profile(
        sample_candidate.id, parsed_data
    )
    
    # Assert
    # Skills are deduplicated using set(), so order may vary
    assert set(sample_candidate.skills) == {"python", "react", "postgresql"}
    assert sample_candidate.experience_years == 7
    mock_candidate_repo.db.commit.assert_called_once()
    mock_candidate_repo.db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_auto_populate_merge_skills(
    parsing_service, mock_candidate_repo, sample_candidate
):
    """Test merging skills with existing candidate skills."""
    # Arrange
    sample_candidate.skills = ["java", "spring"]
    
    parsed_data = ResumeParsedDataSchema(
        skills=["python", "java"],  # java is duplicate
        experience_years=5,
        education=[],
        past_roles=[]
    )
    
    mock_candidate_repo.get_by_id.return_value = sample_candidate
    
    # Act
    await parsing_service._auto_populate_candidate_profile(
        sample_candidate.id, parsed_data
    )
    
    # Assert
    # Should merge and deduplicate
    assert "java" in sample_candidate.skills
    assert "python" in sample_candidate.skills
    assert "spring" in sample_candidate.skills
    # java should appear only once
    assert sample_candidate.skills.count("java") == 1


@pytest.mark.asyncio
async def test_auto_populate_preserve_existing_experience(
    parsing_service, mock_candidate_repo, sample_candidate
):
    """Test that existing experience_years is not overwritten."""
    # Arrange
    sample_candidate.experience_years = 10  # Already set
    
    parsed_data = ResumeParsedDataSchema(
        skills=["python"],
        experience_years=5,  # Different value
        education=[],
        past_roles=[]
    )
    
    mock_candidate_repo.get_by_id.return_value = sample_candidate
    
    # Act
    await parsing_service._auto_populate_candidate_profile(
        sample_candidate.id, parsed_data
    )
    
    # Assert
    # Should preserve existing value
    assert sample_candidate.experience_years == 10


@pytest.mark.asyncio
async def test_extract_json_from_markdown_code_fence(parsing_service):
    """Test extraction of JSON from markdown code fence."""
    # Arrange
    response = """Here is the parsed data:
```json
{
  "skills": ["Python"],
  "experience_years": 3,
  "education": [],
  "past_roles": []
}
```
Hope this helps!
"""
    
    # Act
    result = parsing_service._extract_json_from_response(response)
    
    # Assert
    assert result["skills"] == ["Python"]
    assert result["experience_years"] == 3


@pytest.mark.asyncio
async def test_extract_json_from_embedded_json(parsing_service):
    """Test extraction of JSON embedded in text."""
    # Arrange
    response = """The resume contains the following data: {"skills": ["Java"], "experience_years": 2, "education": [], "past_roles": []} as shown above."""
    
    # Act
    result = parsing_service._extract_json_from_response(response)
    
    # Assert
    assert result["skills"] == ["Java"]
    assert result["experience_years"] == 2
