"""Integration tests for job-context-aware interview flows."""
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.models.interview import Interview
from app.models.interview_session import InterviewSession
from app.models.candidate import Candidate
from app.models.job_posting import JobPosting
from app.services.interview_engine import InterviewEngine
from app.repositories.interview import InterviewRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.repositories.interview_message import InterviewMessageRepository


@pytest.mark.asyncio
async def test_data_engineer_interview_with_job_context(test_db, test_candidate):
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
        resume_id=uuid4(),  # Use fake UUID for testing (FK constraint disabled in tests)
        job_posting_id=job_posting.id,  # Link to job posting
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
            role_type="python",  # data_engineering maps to python base
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
        
        # Verify base data_engineering prompt is included
        assert "data engineer" in system_prompt.lower() or "data engineering" in system_prompt.lower()


@pytest.mark.asyncio
async def test_devops_interview_with_job_context(test_db, test_candidate):
    """Test DevOps interview with Docker/Kubernetes/AWS context (Technical role)."""    # Arrange
    # Create job posting with DevOps tech stack
    job_posting = JobPosting(
        id=uuid4(),
        title="DevOps Engineer",
        company="Cloud Systems Inc",
        description="Manage Kubernetes clusters and CI/CD pipelines on AWS. Expertise in Docker, Terraform, and GitLab CI required.",
        required_skills=["Kubernetes", "Docker", "AWS", "Terraform", "GitLab CI", "Prometheus"],
        role_category="devops",
        tech_stack="devops",
        employment_type="permanent",
        work_setup="hybrid",
        location="Remote",
        experience_level="Senior",
        status="active"
    )
    test_db.add(job_posting)
    await test_db.flush()
    
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),  # Use fake UUID for testing (FK constraint disabled in tests)
        job_posting_id=job_posting.id,
        role_type="python",  # devops maps to python base
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
    
    await test_db.refresh(interview, attribute_names=["job_posting"])
    
    with patch('app.services.interview_engine.OpenAIProvider') as mock_provider_class:
        mock_provider = mock_provider_class.return_value
        
        interview_repo = InterviewRepository(test_db)
        session_repo = InterviewSessionRepository(test_db)
        message_repo = InterviewMessageRepository(test_db)
        
        engine = InterviewEngine(
            ai_provider=mock_provider,
            session_repo=session_repo,
            message_repo=message_repo,
            interview_repo=interview_repo
        )
        
        # Act
        system_prompt = await engine.get_realtime_system_prompt(
            role_type="python",  # devops maps to python base
            session_state=session.to_dict(),
            job_posting=job_posting
        )
        
        # Assert
        assert interview.job_posting_id == job_posting.id
        assert "DevOps Engineer" in system_prompt
        assert "Cloud Systems Inc" in system_prompt
        assert "Kubernetes" in system_prompt
        assert "Docker" in system_prompt
        assert "AWS" in system_prompt
        assert "Terraform" in system_prompt
        assert "JOB-SPECIFIC CONTEXT" in system_prompt


@pytest.mark.asyncio
async def test_qa_automation_interview_with_job_context(test_db, test_candidate):
    """Test QA Automation interview with Playwright/Cypress context (Technical role)."""
    # Arrange
    resume = Resume(
        id=uuid4(),
        candidate_id=test_candidate.id,
        file_path="test_resume.pdf",
        text_content="Test resume content"
    )
    test_db.add(resume)
    await test_db.flush()
    
    job_posting = JobPosting(
        id=uuid4(),
        title="QA Automation Engineer",
        company="Testing Solutions Ltd",
        description="Build automated test suites using Playwright and Cypress. Experience with CI/CD integration.",
        required_skills=["Playwright", "Cypress", "TypeScript", "Jest", "GitHub Actions"],
        role_category="quality_assurance",
        tech_stack="qa_automation",
        employment_type="contract",
        work_setup="remote",
        location="Remote",
        experience_level="Senior",
        status="active"
    )
    test_db.add(job_posting)
    await test_db.flush()
    
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),  # Use fake UUID for testing (FK constraint disabled in tests)
        job_posting_id=job_posting.id,
        role_type="javascript",  # qa_automation maps to javascript base
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
    
    await test_db.refresh(interview, attribute_names=["job_posting"])
    
    with patch('app.services.interview_engine.OpenAIProvider') as mock_provider_class:
        mock_provider = mock_provider_class.return_value
        
        interview_repo = InterviewRepository(test_db)
        session_repo = InterviewSessionRepository(test_db)
        message_repo = InterviewMessageRepository(test_db)
        
        engine = InterviewEngine(
            ai_provider=mock_provider,
            session_repo=session_repo,
            message_repo=message_repo,
            interview_repo=interview_repo
        )
        
        # Act
        system_prompt = await engine.get_realtime_system_prompt(
            role_type="javascript",  # qa_automation maps to javascript base
            session_state=session.to_dict(),
            job_posting=job_posting
        )
        
        # Assert
        assert interview.job_posting_id == job_posting.id
        assert "QA Automation Engineer" in system_prompt
        assert "Testing Solutions Ltd" in system_prompt
        assert "Playwright" in system_prompt
        assert "Cypress" in system_prompt
        assert "JOB-SPECIFIC CONTEXT" in system_prompt


@pytest.mark.asyncio
async def test_sales_interview_with_job_context(test_db, test_candidate):
    """Test Sales interview with B2B/Salesforce context (Non-technical role)."""
    # Arrange - Non-technical role using role_category
    resume = Resume(
        id=uuid4(),
        candidate_id=test_candidate.id,
        file_path="test_resume.pdf",
        text_content="Test resume content"
    )
    test_db.add(resume)
    await test_db.flush()
    
    job_posting = JobPosting(
        id=uuid4(),
        title="Enterprise Sales Executive",
        company="SaaS Unicorn Inc",
        description="Drive B2B SaaS sales. Experience with Salesforce, enterprise deals, and consultative selling required.",
        required_skills=["B2B Sales", "Salesforce", "Enterprise Sales", "Consultative Selling", "Account Management"],
        role_category="sales",  # Non-technical role
        employment_type="permanent",
        work_setup="remote",
        location="Remote",
        experience_level="Senior",
        status="active"
    )
    test_db.add(job_posting)
    await test_db.flush()
    
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),  # Use fake UUID for testing (FK constraint disabled in tests)
        job_posting_id=job_posting.id,
        role_type="fullstack",  # sales (non-technical) maps to fullstack base  # Maps from role_category
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
    
    await test_db.refresh(interview, attribute_names=["job_posting"])
    
    with patch('app.services.interview_engine.OpenAIProvider') as mock_provider_class:
        mock_provider = mock_provider_class.return_value
        
        interview_repo = InterviewRepository(test_db)
        session_repo = InterviewSessionRepository(test_db)
        message_repo = InterviewMessageRepository(test_db)
        
        engine = InterviewEngine(
            ai_provider=mock_provider,
            session_repo=session_repo,
            message_repo=message_repo,
            interview_repo=interview_repo
        )
        
        # Act
        system_prompt = await engine.get_realtime_system_prompt(
            role_type="fullstack",  # sales (non-technical) maps to fullstack base
            session_state=session.to_dict(),
            job_posting=job_posting
        )
        
        # Assert
        assert interview.job_posting_id == job_posting.id
        assert "Enterprise Sales Executive" in system_prompt
        assert "SaaS Unicorn Inc" in system_prompt
        assert "B2B" in system_prompt or "B2B Sales" in system_prompt
        assert "Salesforce" in system_prompt
        assert "JOB-SPECIFIC CONTEXT" in system_prompt
        
        # Verify it's a sales-focused prompt (not technical)
        assert "sales" in system_prompt.lower()
        assert "selling" in system_prompt.lower() or "revenue" in system_prompt.lower()


@pytest.mark.asyncio
async def test_support_interview_with_job_context(test_db, test_candidate):
    """Test Customer Support interview with SaaS product context (Non-technical role)."""
    # Arrange
    resume = Resume(
        id=uuid4(),
        candidate_id=test_candidate.id,
        file_path="test_resume.pdf",
        text_content="Test resume content"
    )
    test_db.add(resume)
    await test_db.flush()
    
    job_posting = JobPosting(
        id=uuid4(),
        title="Senior Customer Support Specialist",
        company="HelpDesk Pro",
        description="Provide technical support for SaaS product. Experience with Zendesk, JIRA, and customer success required.",
        required_skills=["Customer Service", "Zendesk", "JIRA", "Technical Support", "Problem Solving"],
        role_category="support",
        employment_type="permanent",
        work_setup="onsite",
        location="Remote",
        experience_level="Senior",
        status="active"
    )
    test_db.add(job_posting)
    await test_db.flush()
    
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),  # Use fake UUID for testing (FK constraint disabled in tests)
        job_posting_id=job_posting.id,
        role_type="fullstack",  # support (non-technical) maps to fullstack base
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
    
    await test_db.refresh(interview, attribute_names=["job_posting"])
    
    with patch('app.services.interview_engine.OpenAIProvider') as mock_provider_class:
        mock_provider = mock_provider_class.return_value
        
        interview_repo = InterviewRepository(test_db)
        session_repo = InterviewSessionRepository(test_db)
        message_repo = InterviewMessageRepository(test_db)
        
        engine = InterviewEngine(
            ai_provider=mock_provider,
            session_repo=session_repo,
            message_repo=message_repo,
            interview_repo=interview_repo
        )
        
        # Act
        system_prompt = await engine.get_realtime_system_prompt(
            role_type="fullstack",  # support (non-technical) maps to fullstack base
            session_state=session.to_dict(),
            job_posting=job_posting
        )
        
        # Assert
        assert interview.job_posting_id == job_posting.id
        assert "Senior Customer Support Specialist" in system_prompt
        assert "HelpDesk Pro" in system_prompt
        assert "Zendesk" in system_prompt or "JIRA" in system_prompt
        assert "JOB-SPECIFIC CONTEXT" in system_prompt
        assert "support" in system_prompt.lower() or "customer" in system_prompt.lower()


@pytest.mark.asyncio
async def test_product_manager_interview_with_job_context(test_db, test_candidate):
    """Test Product Manager interview with B2B SaaS context (Non-technical role)."""
    # Arrange
    resume = Resume(
        id=uuid4(),
        candidate_id=test_candidate.id,
        file_path="test_resume.pdf",
        text_content="Test resume content"
    )
    test_db.add(resume)
    await test_db.flush()
    
    job_posting = JobPosting(
        id=uuid4(),
        title="Senior Product Manager",
        company="ProductCo",
        description="Lead product strategy for B2B SaaS platform. Experience with Agile, roadmapping, and user research.",
        required_skills=["Product Management", "Agile", "User Research", "Roadmapping", "Stakeholder Management", "Data Analysis"],
        role_category="product",
        employment_type="permanent",
        work_setup="hybrid",
        location="Remote",
        experience_level="Senior",
        status="active"
    )
    test_db.add(job_posting)
    await test_db.flush()
    
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),  # Use fake UUID for testing (FK constraint disabled in tests)
        job_posting_id=job_posting.id,
        role_type="fullstack",  # product (non-technical) maps to fullstack base
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
    
    await test_db.refresh(interview, attribute_names=["job_posting"])
    
    with patch('app.services.interview_engine.OpenAIProvider') as mock_provider_class:
        mock_provider = mock_provider_class.return_value
        
        interview_repo = InterviewRepository(test_db)
        session_repo = InterviewSessionRepository(test_db)
        message_repo = InterviewMessageRepository(test_db)
        
        engine = InterviewEngine(
            ai_provider=mock_provider,
            session_repo=session_repo,
            message_repo=message_repo,
            interview_repo=interview_repo
        )
        
        # Act
        system_prompt = await engine.get_realtime_system_prompt(
            role_type="fullstack",  # product (non-technical) maps to fullstack base
            session_state=session.to_dict(),
            job_posting=job_posting
        )
        
        # Assert
        assert interview.job_posting_id == job_posting.id
        assert "Senior Product Manager" in system_prompt
        assert "ProductCo" in system_prompt
        assert "Agile" in system_prompt or "product" in system_prompt.lower()
        assert "JOB-SPECIFIC CONTEXT" in system_prompt


@pytest.mark.asyncio
async def test_interview_without_job_context_still_works(test_db, test_candidate):
    """Test backward compatibility: interview without job_posting_id still works (AC #7, #13)."""    # Arrange
    # Interview WITHOUT job_posting_id
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),  # Use fake UUID for testing (FK constraint disabled in tests)
        job_posting_id=None,  # No job posting linked
        role_type="react",
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
    
    with patch('app.services.interview_engine.OpenAIProvider') as mock_provider_class:
        mock_provider = mock_provider_class.return_value
        
        interview_repo = InterviewRepository(test_db)
        session_repo = InterviewSessionRepository(test_db)
        message_repo = InterviewMessageRepository(test_db)
        
        engine = InterviewEngine(
            ai_provider=mock_provider,
            session_repo=session_repo,
            message_repo=message_repo,
            interview_repo=interview_repo
        )
        
        # Act - Generate prompt WITHOUT job_posting parameter
        system_prompt = await engine.get_realtime_system_prompt(
            role_type="react",
            session_state=session.to_dict(),
            job_posting=None  # No job context
        )
        
        # Assert - Should work with just base prompt
        assert interview.job_posting_id is None
        assert "JOB-SPECIFIC CONTEXT" not in system_prompt  # No job context injected
        assert "react" in system_prompt.lower()  # Base React prompt still present
        assert len(system_prompt) > 100  # Has meaningful content


@pytest.mark.asyncio
async def test_rust_interview_with_systems_programming_context(test_db, test_candidate):
    """Test Rust interview with systems programming context (Technical role - diverse from Python/JS)."""
    # Arrange - Test a different tech stack (Rust for systems programming)
    resume = Resume(
        id=uuid4(),
        candidate_id=test_candidate.id,
        file_path="test_resume.pdf",
        text_content="Test resume content"
    )
    test_db.add(resume)
    await test_db.flush()
    
    job_posting = JobPosting(
        id=uuid4(),
        title="Rust Systems Engineer",
        company="Systems Lab",
        description="Build high-performance systems software in Rust. Work with async/await, tokio, and low-level optimization.",
        required_skills=["Rust", "async/await", "tokio", "Systems Programming", "Memory Management", "Performance Optimization"],
        role_category="engineering",
        tech_stack="rust",
        employment_type="permanent",
        work_setup="remote",
        location="Remote",
        experience_level="Senior",
        status="active"
    )
    test_db.add(job_posting)
    await test_db.flush()
    
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),  # Use fake UUID for testing (FK constraint disabled in tests)
        job_posting_id=job_posting.id,
        role_type="python",  # rust maps to python base
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
    
    await test_db.refresh(interview, attribute_names=["job_posting"])
    
    with patch('app.services.interview_engine.OpenAIProvider') as mock_provider_class:
        mock_provider = mock_provider_class.return_value
        
        interview_repo = InterviewRepository(test_db)
        session_repo = InterviewSessionRepository(test_db)
        message_repo = InterviewMessageRepository(test_db)
        
        engine = InterviewEngine(
            ai_provider=mock_provider,
            session_repo=session_repo,
            message_repo=message_repo,
            interview_repo=interview_repo
        )
        
        # Act
        system_prompt = await engine.get_realtime_system_prompt(
            role_type="python",  # rust maps to python base
            session_state=session.to_dict(),
            job_posting=job_posting
        )
        
        # Assert
        assert interview.job_posting_id == job_posting.id
        assert "Rust Systems Engineer" in system_prompt
        assert "Systems Lab" in system_prompt
        assert "Rust" in system_prompt
        assert "tokio" in system_prompt or "async" in system_prompt.lower()
        assert "JOB-SPECIFIC CONTEXT" in system_prompt
        assert "rust" in system_prompt.lower()
