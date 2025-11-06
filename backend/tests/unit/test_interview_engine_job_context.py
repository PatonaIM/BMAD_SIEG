"""Unit tests for InterviewEngine job context functionality."""
import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.services.interview_engine import InterviewEngine
from app.models.job_posting import JobPosting
from app.models.interview_session import InterviewSession


@pytest.fixture
def sample_job_posting():
    """Create sample job posting for testing."""
    return JobPosting(
        id=uuid4(),
        title="Senior Data Engineer",
        company="Tech Corp",
        description="We are looking for an experienced Data Engineer to build scalable data pipelines using Kafka, Spark, and Snowflake. You will work with large datasets and optimize ETL processes.",
        role_category="data",
        tech_stack="python",
        employment_type="permanent",
        work_setup="remote",
        location="Sydney, Australia",
        required_skills=["Kafka", "Spark", "Snowflake", "SQL", "Python", "Airflow"],
        experience_level="Senior"
    )


@pytest.fixture
def sample_sales_job_posting():
    """Create sample sales job posting for non-technical role testing."""
    return JobPosting(
        id=uuid4(),
        title="Account Manager - Enterprise SaaS",
        company="SaaS Startup",
        description="Manage a portfolio of enterprise accounts, drive upsells and renewals, and build long-term client relationships. Experience with Salesforce required.",
        role_category="sales",
        tech_stack=None,  # Non-technical role
        employment_type="permanent",
        work_setup="hybrid",
        location="Melbourne, Australia",
        required_skills=["B2B Sales", "Salesforce", "Account Management", "Negotiation", "CRM"],
        experience_level="Mid"
    )


@pytest.fixture
def sample_session():
    """Create sample interview session."""
    return InterviewSession(
        id=uuid4(),
        interview_id=uuid4(),
        current_difficulty_level="warmup",
        questions_asked_count=2,
        conversation_memory={"messages": [], "memory_metadata": {}},
        skill_boundaries_identified={},
        progression_state={
            "phase_history": [],
            "response_quality_history": [],
            "skills_assessed": [],
            "skills_pending": [],
            "boundary_detections": []
        }
    )


def test_get_realtime_system_prompt_with_job_posting(sample_job_posting, sample_session):
    """Test system prompt generation with job posting context."""
    # Arrange
    engine = InterviewEngine(
        ai_provider=Mock(),
        session_repo=Mock(),
        message_repo=Mock(),
        interview_repo=Mock()
    )
    
    # Act
    prompt = engine.get_realtime_system_prompt(
        role_type="python",
        session=sample_session,
        job_posting=sample_job_posting
    )
    
    # Assert - Verify job context is injected
    assert "Senior Data Engineer" in prompt, "Job title should appear in prompt"
    assert "Tech Corp" in prompt, "Company name should appear in prompt"
    assert "Kafka" in prompt, "Required skill 'Kafka' should appear"
    assert "Spark" in prompt, "Required skill 'Spark' should appear"
    assert "Snowflake" in prompt, "Required skill 'Snowflake' should appear"
    assert "data" in prompt.lower(), "Role category should be mentioned"
    assert "JOB-SPECIFIC CONTEXT" in prompt, "Job context section should be present"
    assert "tailor all questions" in prompt.lower(), "Instructions to tailor questions should be present"
    
    # Verify base prompt is still there
    assert "You are an expert technical interviewer" in prompt
    assert "python" in prompt.lower()


def test_get_realtime_system_prompt_without_job_posting(sample_session):
    """Test system prompt generation WITHOUT job posting (backward compatibility)."""
    # Arrange
    engine = InterviewEngine(
        ai_provider=Mock(),
        session_repo=Mock(),
        message_repo=Mock(),
        interview_repo=Mock()
    )
    
    # Act
    prompt = engine.get_realtime_system_prompt(
        role_type="react",
        session=sample_session,
        job_posting=None  # No job context
    )
    
    # Assert - Verify base prompt only
    assert "You are an expert technical interviewer" in prompt
    assert "react" in prompt.lower()
    assert "JOB-SPECIFIC CONTEXT" not in prompt, "Job context section should NOT be present"
    assert "TAILOR ALL questions" not in prompt, "Job-specific instructions should NOT be present"


def test_get_realtime_system_prompt_non_technical_role(sample_sales_job_posting, sample_session):
    """Test system prompt for non-technical roles (sales) with job context."""
    # Arrange
    engine = InterviewEngine(
        ai_provider=Mock(),
        session_repo=Mock(),
        message_repo=Mock(),
        interview_repo=Mock()
    )
    
    # Act
    prompt = engine.get_realtime_system_prompt(
        role_type="fullstack",  # Non-technical roles use 'fullstack' base
        session=sample_session,
        job_posting=sample_sales_job_posting
    )
    
    # Assert - Verify non-technical focus
    assert "Account Manager" in prompt, "Job title should appear"
    assert "SaaS Startup" in prompt, "Company should appear"
    assert "Salesforce" in prompt, "Required skill should appear"
    assert "B2B Sales" in prompt, "Sales skill should appear"
    assert "sales" in prompt.lower(), "Role category should be mentioned"
    
    # Verify instructions for non-technical interviews
    assert "DO NOT ask coding" in prompt.upper() or "non-technical" in prompt.lower(), \
        "Should have instructions to avoid technical questions"
    

def test_prompt_length_with_job_context(sample_job_posting):
    """Test that prompt with job context stays under reasonable token limit."""
    # Arrange
    engine = InterviewEngine(
        ai_provider=Mock(),
        session_repo=Mock(),
        message_repo=Mock(),
        interview_repo=Mock()
    )
    
    # Act
    prompt = engine.get_realtime_system_prompt(
        role_type="python",
        session=None,
        job_posting=sample_job_posting
    )
    
    # Assert - Rough token estimation (1 token ≈ 4 chars)
    estimated_tokens = len(prompt) / 4
    assert estimated_tokens < 4000, f"Prompt too long: ~{estimated_tokens} tokens (limit: 4000)"
    print(f"Prompt length: {len(prompt)} chars (~{estimated_tokens:.0f} tokens)")


def test_job_description_truncation():
    """Test that very long job descriptions are truncated."""
    # Arrange
    engine = InterviewEngine(
        ai_provider=Mock(),
        session_repo=Mock(),
        message_repo=Mock(),
        interview_repo=Mock()
    )
    
    # Create job with very long description (> 500 chars)
    long_description = "A" * 1000  # 1000 character description
    job_posting = JobPosting(
        id=uuid4(),
        title="Test Role",
        company="Test Co",
        description=long_description,
        role_category="engineering",
        tech_stack="python",
        employment_type="permanent",
        work_setup="remote",
        location="Sydney",
        required_skills=["Python"],
        experience_level="Mid"
    )
    
    # Act
    prompt = engine.get_realtime_system_prompt(
        role_type="python",
        session=None,
        job_posting=job_posting
    )
    
    # Assert - Description should be truncated to 500 chars + "..."
    assert "..." in prompt, "Long description should be truncated with ellipsis"
    # Count occurrences of 'A' - should be ~500, not 1000
    a_count = prompt.count("A")
    assert a_count < 600, f"Description not truncated properly: {a_count} characters"


def test_session_state_in_prompt(sample_job_posting):
    """Test that session state (questions asked, difficulty) appears in prompt."""
    # Arrange
    engine = InterviewEngine(
        ai_provider=Mock(),
        session_repo=Mock(),
        message_repo=Mock(),
        interview_repo=Mock()
    )
    
    session = InterviewSession(
        id=uuid4(),
        interview_id=uuid4(),
        current_difficulty_level="advanced",
        questions_asked_count=10,
        conversation_memory={"messages": [], "memory_metadata": {}},
        skill_boundaries_identified={},
        progression_state={}
    )
    
    # Act
    prompt = engine.get_realtime_system_prompt(
        role_type="python",
        session=session,
        job_posting=sample_job_posting
    )
    
    # Assert
    assert "10" in prompt, "Questions asked count should appear"
    assert "advanced" in prompt.lower(), "Current difficulty should appear"


def test_required_skills_formatting(sample_job_posting):
    """Test that required skills are properly formatted in prompt."""
    # Arrange
    engine = InterviewEngine(
        ai_provider=Mock(),
        session_repo=Mock(),
        message_repo=Mock(),
        interview_repo=Mock()
    )
    
    # Act
    prompt = engine.get_realtime_system_prompt(
        role_type="python",
        session=None,
        job_posting=sample_job_posting
    )
    
    # Assert - All required skills should be present
    for skill in sample_job_posting.required_skills:
        assert skill in prompt, f"Required skill '{skill}' should appear in prompt"
