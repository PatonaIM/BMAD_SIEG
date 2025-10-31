"""Integration tests for interview conversation flow."""
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.models.interview import Interview
from app.models.interview_session import InterviewSession
from app.models.candidate import Candidate
from app.services.interview_engine import InterviewEngine
from app.repositories.interview import InterviewRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.repositories.interview_message import InterviewMessageRepository
from app.providers.openai_provider import OpenAIProvider


@pytest.mark.asyncio
async def test_complete_message_exchange_flow(test_db, test_candidate):
    """Test complete message exchange flow with real database."""
    # Arrange - Create interview and session
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),
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
    
    # Mock OpenAI provider
    with patch('app.services.interview_engine.OpenAIProvider') as mock_provider_class:
        mock_provider = mock_provider_class.return_value
        mock_provider.generate_interview_question = AsyncMock(
            return_value=("What is React?", 100, 0.001)
        )
        mock_provider.analyze_candidate_response = AsyncMock(
            return_value={"score": 8, "concepts": ["react"]}
        )
        
        # Create repositories
        interview_repo = InterviewRepository(test_db)
        session_repo = InterviewSessionRepository(test_db)
        message_repo = InterviewMessageRepository(test_db)
        
        # Create engine with mocked AI provider
        engine = InterviewEngine(
            ai_provider=mock_provider,
            session_repo=session_repo,
            message_repo=message_repo,
            interview_repo=interview_repo
        )
        
        # Act - Send message
        result = await engine.process_candidate_response(
            interview_id=interview.id,
            response_text="I have React experience"
        )
        
        # Assert
        assert result["ai_response"] == "What is React?"
        assert result["question_number"] == 1
        
        # Verify database state
        await test_db.refresh(session)
        assert session.questions_asked_count == 1
        assert session.conversation_memory is not None


@pytest.mark.asyncio
async def test_conversation_context_preservation(test_db, test_candidate):
    """Test conversation context is preserved across multiple messages."""
    # Arrange
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),
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
        mock_provider.generate_interview_question = AsyncMock(
            side_effect=[
                ("Question 1?", 100, 0.001),
                ("Question 2?", 110, 0.001),
                ("Question 3?", 120, 0.001),
            ]
        )
        mock_provider.analyze_candidate_response = AsyncMock(
            return_value={"score": 7, "concepts": ["react", "hooks"]}
        )
        
        interview_repo = InterviewRepository(test_db)
        session_repo = InterviewSessionRepository(test_db)
        message_repo = InterviewMessageRepository(test_db)
        
        engine = InterviewEngine(
            ai_provider=mock_provider,
            session_repo=session_repo,
            message_repo=message_repo,
            interview_repo=interview_repo
        )
        
        # Act - Send 3 messages
        for i in range(3):
            result = await engine.process_candidate_response(
                interview_id=interview.id,
                response_text=f"Answer {i+1}"
            )
            assert result["question_number"] == i + 1
        
        # Assert - Verify final state
        await test_db.refresh(session)
        assert session.questions_asked_count == 3
        assert "messages" in session.conversation_memory
        assert len(session.conversation_memory["messages"]) > 0


@pytest.mark.asyncio
async def test_session_state_persistence_and_recovery(test_db, test_candidate):
    """Test session state persists and can be recovered."""
    # Arrange - Create interview with existing conversation
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),
        role_type="react",
        status="in_progress",
        total_tokens_used=200,
        cost_usd=0.002
    )
    test_db.add(interview)
    await test_db.flush()
    
    # Session with existing conversation state
    session = InterviewSession(
        id=uuid4(),
        interview_id=interview.id,
        current_difficulty_level="standard",
        questions_asked_count=3,
        conversation_memory={
            "messages": [
                {"role": "user", "content": "Previous answer"},
                {"role": "assistant", "content": "Previous question"}
            ],
            "memory_metadata": {"message_count": 2}
        },
        skill_boundaries_identified={"react": "proficient"},
        progression_state={"response_scores": [7, 8, 7]}
    )
    test_db.add(session)
    await test_db.commit()
    
    with patch('app.services.interview_engine.OpenAIProvider') as mock_provider_class:
        mock_provider = mock_provider_class.return_value
        mock_provider.generate_interview_question = AsyncMock(
            return_value=("New question?", 150, 0.002)
        )
        mock_provider.analyze_candidate_response = AsyncMock(
            return_value={"score": 8, "concepts": ["hooks"]}
        )
        
        interview_repo = InterviewRepository(test_db)
        session_repo = InterviewSessionRepository(test_db)
        message_repo = InterviewMessageRepository(test_db)
        
        engine = InterviewEngine(
            ai_provider=mock_provider,
            session_repo=session_repo,
            message_repo=message_repo,
            interview_repo=interview_repo
        )
        
        # Act - Continue conversation
        result = await engine.process_candidate_response(
            interview_id=interview.id,
            response_text="Continued answer"
        )
        
        # Assert - State should be preserved and incremented
        assert result["question_number"] == 4  # 3 previous + 1 new
        await test_db.refresh(session)
        assert session.questions_asked_count == 4
        assert session.current_difficulty_level in ["standard", "advanced"]


@pytest.mark.asyncio
async def test_error_recovery_with_state_rollback(test_db, test_candidate):
    """Test error recovery maintains database consistency."""
    # Arrange
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),
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
    
    initial_count = session.questions_asked_count
    
    with patch('app.services.interview_engine.OpenAIProvider') as mock_provider_class:
        mock_provider = mock_provider_class.return_value
        # Simulate AI provider failure
        mock_provider.generate_interview_question = AsyncMock(
            side_effect=Exception("API error")
        )
        mock_provider.analyze_candidate_response = AsyncMock(
            return_value={"score": 7, "concepts": []}
        )
        
        interview_repo = InterviewRepository(test_db)
        session_repo = InterviewSessionRepository(test_db)
        message_repo = InterviewMessageRepository(test_db)
        
        engine = InterviewEngine(
            ai_provider=mock_provider,
            session_repo=session_repo,
            message_repo=message_repo,
            interview_repo=interview_repo
        )
        
        # Act & Assert - Operation should fail
        with pytest.raises(Exception):
            await engine.process_candidate_response(
                interview_id=interview.id,
                response_text="Test answer"
            )
        
        # Verify state wasn't partially updated
        await test_db.refresh(session)
        # Question count should be unchanged on error
        assert session.questions_asked_count == initial_count
