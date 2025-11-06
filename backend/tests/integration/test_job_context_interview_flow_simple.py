"""Integration tests for job-context-aware interview flows."""
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.models.interview import Interview
from app.models.interview_session import InterviewSession
from app.models.candidate import Candidate
from app.models.job_posting import JobPosting
from app.models.resume import Resume
from app.services.interview_engine import InterviewEngine
from app.repositories.interview import InterviewRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.repositories.interview_message import InterviewMessageRepository


@pytest.fixture
async def test_resume(test_db, test_candidate):
    """Create a test resume for FK constraints."""
    resume = Resume(
        id=uuid4(),
        candidate_id=test_candidate.id,
        file_url="s3://test-bucket/resume.pdf",
        file_name="test_resume.pdf",
        file_size=1024,
        parsing_status="completed"
    )
    test_db.add(resume)
    await test_db.flush()
    return resume


@pytest.mark.asyncio
async def test_data_engineer_interview_with_job_context(test_db, test_candidate, test_resume):
    """Test Data Engineer interview with Kafka/Spark/Snowflake context (Technical role)."""
    # Arrange - Create job posting with data engineering tech stack
    job_posting = JobPosting(
        id=uuid4(),
        title="Senior Data Engineer",
        company="Tech Corp",
        description="Build scalable data pipelines for real-time analytics. Work with Kafka, Spark, and Snowflake.",
        required_skills=["Kafka", "Apache Spark", "Snowflake", "SQL", "Python", "Airflow"],
        role_category="data",
        tech_stack="data_engineering",
        employment_type="permanent",
        work_setup="remote",
        location="Remote",
        experience_level="Senior",
        status="active"
    )
    test_db.add(job_posting)
    await test_db.flush()
    
    # Create interview linked to job posting
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=test_resume.id,
        job_posting_id=job_posting.id,
        role_type="python",  # data_engineering maps to python base
        status="in_progress",
        total_tokens_used=0,
        cost_usd=0.0
    )
    test_db.add(interview)
    await test_db.flush()
    
    session = InterviewSession(
        id=uuid4(),
        interview_id=interview.id,
        current_difficulty_level="warmup",
        questions_asked_count=0,
        conversation_memory={"messages": [], "memory_metadata": {}},
        skill_boundaries_identified={},
        progression_state={"response_scores": []}
    )
    test_db.add(session)
    await test_db.commit()
    
    # Refresh to load relationships
    await test_db.refresh(interview, attribute_names=["job_posting"])
    
    # Mock OpenAI provider
    with patch('app.services.interview_engine.OpenAIProvider') as mock_provider_class:
        mock_provider = mock_provider_class.return_value
        mock_provider.generate_interview_question = AsyncMock(
            return_value=("Can you explain your experience with Kafka and real-time data processing?", 100, 0.001)
        )
        
        # Create repositories
        interview_repo = InterviewRepository(test_db)
        session_repo = InterviewSessionRepository(test_db)
        message_repo = InterviewMessageRepository(test_db)
        
        # Create engine
        engine = InterviewEngine(
            ai_provider=mock_provider,
            session_repo=session_repo,
            message_repo=message_repo,
            interview_repo=interview_repo
        )
        
        # Act - Generate system prompt with job context
        system_prompt = await engine.get_realtime_system_prompt(
            role_type="python",
            session_state=session.to_dict(),
            job_posting=job_posting
        )
        
        # Assert - Verify job context injection
        assert job_posting.id is not None
        assert interview.job_posting_id == job_posting.id
        assert interview.job_posting is not None
        
        # Verify prompt contains job-specific context
        assert "Senior Data Engineer" in system_prompt
        assert "Tech Corp" in system_prompt
        assert "Kafka" in system_prompt
        assert "Spark" in system_prompt or "Apache Spark" in system_prompt
        assert "Snowflake" in system_prompt
        assert "JOB-SPECIFIC CONTEXT" in system_prompt
        
        # Verify instructions to tailor questions
        assert "tailor all questions" in system_prompt.lower() or "adapt" in system_prompt.lower()
