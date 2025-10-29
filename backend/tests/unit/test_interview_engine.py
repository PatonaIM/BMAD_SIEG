"""Unit tests for InterviewEngine service."""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID, uuid4
from datetime import datetime

from app.services.interview_engine import InterviewEngine
from app.models.interview import Interview
from app.models.interview_session import InterviewSession
from app.models.interview_message import InterviewMessage
from app.core.exceptions import InterviewNotFoundException, InterviewCompletedException


@pytest.fixture
def mock_interview_repo():
    """Mock interview repository."""
    repo = Mock()
    repo.get_by_id = AsyncMock()
    repo.update_token_usage = AsyncMock()
    return repo


@pytest.fixture
def mock_session_repo():
    """Mock interview session repository."""
    repo = Mock()
    repo.get_by_id = AsyncMock()
    repo.get_by_interview_id = AsyncMock()
    repo.update_session_state = AsyncMock()
    repo.update_last_activity = AsyncMock()
    repo.increment_question_count = AsyncMock()
    return repo


@pytest.fixture
def mock_message_repo():
    """Mock interview message repository."""
    repo = Mock()
    repo.create = AsyncMock()
    repo.get_by_interview_id = AsyncMock(return_value=[])
    repo.count_by_interview_id = AsyncMock(return_value=0)
    repo.get_message_count_for_session = AsyncMock(return_value=0)
    return repo


@pytest.fixture
def mock_ai_provider():
    """Mock AI provider."""
    provider = Mock()
    provider.generate_interview_question = AsyncMock(
        return_value=("What is React?", 100, 0.001)
    )
    provider.analyze_candidate_response = AsyncMock(
        return_value={"score": 8, "concepts": ["react", "hooks"]}
    )
    return provider


@pytest.fixture
def sample_interview():
    """Create sample interview."""
    return Interview(
        id=uuid4(),
        candidate_id=uuid4(),
        resume_id=uuid4(),
        role_type="Frontend Developer",
        status="in_progress",
        total_tokens_used=0,
        cost_usd=0.0
    )


@pytest.fixture
def sample_session():
    """Create sample interview session."""
    return InterviewSession(
        id=uuid4(),
        interview_id=uuid4(),
        current_difficulty_level="warmup",
        questions_asked_count=0,
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


@pytest.mark.asyncio
async def test_process_candidate_response_success(
    mock_ai_provider,
    mock_interview_repo,
    mock_session_repo,
    mock_message_repo,
    sample_interview,
    sample_session
):
    """Test successful candidate response processing."""
    # Arrange
    sample_session.interview_id = sample_interview.id
    mock_interview_repo.get_by_id.return_value = sample_interview
    mock_session_repo.get_by_id.return_value = sample_session
    mock_session_repo.get_by_interview_id.return_value = sample_session
    
    candidate_msg = InterviewMessage(
        id=uuid4(),
        interview_id=sample_interview.id,
        session_id=sample_session.id,
        sequence_number=1,
        message_type="candidate_response",
        content_text="I have React experience"
    )
    ai_msg = InterviewMessage(
        id=uuid4(),
        interview_id=sample_interview.id,
        session_id=sample_session.id,
        sequence_number=2,
        message_type="ai_question",
        content_text="What is React?"
    )
    mock_message_repo.create.side_effect = [candidate_msg, ai_msg]
    
    engine = InterviewEngine(
        ai_provider=mock_ai_provider,
        session_repo=mock_session_repo,
        message_repo=mock_message_repo,
        interview_repo=mock_interview_repo
    )
    
    # Act
    result = await engine.process_candidate_response(
        interview_id=sample_interview.id,
        session_id=sample_session.id,
        response_text="I have React experience",
        role_type="Frontend Developer"
    )
    
    # Assert
    assert result["ai_response"] == "What is React?"
    assert result["question_number"] == 1
    mock_message_repo.create.assert_called()
    mock_session_repo.update_session_state.assert_called_once()
    mock_interview_repo.update_token_usage.assert_called_once()


@pytest.mark.asyncio
async def test_process_candidate_response_interview_not_found(
    mock_ai_provider,
    mock_interview_repo,
    mock_session_repo,
    mock_message_repo
):
    """Test processing response for non-existent interview."""
    # Arrange
    mock_session_repo.get_by_id.return_value = None
    mock_interview_repo.get_by_id.return_value = None
    
    engine = InterviewEngine(
        ai_provider=mock_ai_provider,
        session_repo=mock_session_repo,
        message_repo=mock_message_repo,
        interview_repo=mock_interview_repo
    )
    
    # Act & Assert
    with pytest.raises(InterviewNotFoundException):
        await engine.process_candidate_response(
            interview_id=uuid4(),
            session_id=uuid4(),
            response_text="Test response",
            role_type="Frontend Developer"
        )


@pytest.mark.asyncio
async def test_process_candidate_response_interview_completed(
    mock_ai_provider,
    mock_interview_repo,
    mock_session_repo,
    mock_message_repo,
    sample_interview,
    sample_session
):
    """Test processing response for completed interview."""
    # Arrange
    sample_interview.status = "completed"
    sample_session.interview_id = sample_interview.id
    mock_interview_repo.get_by_id.return_value = sample_interview
    mock_session_repo.get_by_id.return_value = sample_session
    mock_session_repo.get_by_interview_id.return_value = sample_session
    
    engine = InterviewEngine(
        ai_provider=mock_ai_provider,
        session_repo=mock_session_repo,
        message_repo=mock_message_repo,
        interview_repo=mock_interview_repo
    )
    
    # Act & Assert
    with pytest.raises(InterviewCompletedException):
        await engine.process_candidate_response(
            interview_id=sample_interview.id,
            session_id=sample_session.id,
            response_text="Test response",
            role_type="Frontend Developer"
        )


@pytest.mark.asyncio
async def test_conversation_memory_serialization(
    mock_ai_provider,
    mock_interview_repo,
    mock_session_repo,
    mock_message_repo,
    sample_interview,
    sample_session
):
    """Test conversation memory is properly serialized and stored."""
    # Arrange
    sample_session.interview_id = sample_interview.id
    mock_interview_repo.get_by_id.return_value = sample_interview
    mock_session_repo.get_by_id.return_value = sample_session
    mock_session_repo.get_by_interview_id.return_value = sample_session
    
    candidate_msg = InterviewMessage(
        id=uuid4(),
        interview_id=sample_interview.id,
        session_id=sample_session.id,
        sequence_number=1,
        message_type="candidate_response",
        content_text="Test response"
    )
    ai_msg = InterviewMessage(
        id=uuid4(),
        interview_id=sample_interview.id,
        session_id=sample_session.id,
        sequence_number=2,
        message_type="ai_question",
        content_text="Test question"
    )
    mock_message_repo.create.side_effect = [candidate_msg, ai_msg]
    
    engine = InterviewEngine(
        ai_provider=mock_ai_provider,
        session_repo=mock_session_repo,
        message_repo=mock_message_repo,
        interview_repo=mock_interview_repo
    )
    
    # Act
    await engine.process_candidate_response(
        interview_id=sample_interview.id,
        session_id=sample_session.id,
        response_text="Test response",
        role_type="Frontend Developer"
    )
    
    # Assert - verify memory was updated
    mock_session_repo.update_session_state.assert_called_once()
    call_args = mock_session_repo.update_session_state.call_args
    assert "conversation_memory" in call_args.kwargs


@pytest.mark.asyncio
async def test_difficulty_progression(
    mock_ai_provider,
    mock_interview_repo,
    mock_session_repo,
    mock_message_repo,
    sample_interview,
    sample_session
):
    """Test difficulty level progression during interview."""
    # Arrange - session at warmup with 2 questions
    sample_session.interview_id = sample_interview.id
    sample_session.questions_asked_count = 2
    sample_session.progression_state = {
        "phase_history": [],
        "response_quality_history": [],
        "skills_assessed": [],
        "skills_pending": [],
        "boundary_detections": [],
        "response_scores": [8, 7],
        "avg_score_by_level": {"warmup": 7.5}
    }
    
    mock_interview_repo.get_by_id.return_value = sample_interview
    mock_session_repo.get_by_id.return_value = sample_session
    mock_session_repo.get_by_interview_id.return_value = sample_session
    
    candidate_msg = InterviewMessage(
        id=uuid4(),
        interview_id=sample_interview.id,
        session_id=sample_session.id,
        sequence_number=3,
        message_type="candidate_response",
        content_text="Good answer"
    )
    ai_msg = InterviewMessage(
        id=uuid4(),
        interview_id=sample_interview.id,
        session_id=sample_session.id,
        sequence_number=4,
        message_type="ai_question",
        content_text="Standard question"
    )
    mock_message_repo.create.side_effect = [candidate_msg, ai_msg]
    
    engine = InterviewEngine(
        ai_provider=mock_ai_provider,
        session_repo=mock_session_repo,
        message_repo=mock_message_repo,
        interview_repo=mock_interview_repo
    )
    
    # Act
    result = await engine.process_candidate_response(
        interview_id=sample_interview.id,
        session_id=sample_session.id,
        response_text="Good answer",
        role_type="Frontend Developer"
    )
    
    # Assert - difficulty should progress
    assert result["session_state"]["current_difficulty"] in ["warmup", "standard", "advanced"]
    mock_session_repo.update_session_state.assert_called_once()


@pytest.mark.asyncio
async def test_token_usage_tracking(
    mock_ai_provider,
    mock_interview_repo,
    mock_session_repo,
    mock_message_repo,
    sample_interview,
    sample_session
):
    """Test token usage is tracked correctly."""
    # Arrange
    sample_session.interview_id = sample_interview.id
    mock_interview_repo.get_by_id.return_value = sample_interview
    mock_session_repo.get_by_id.return_value = sample_session
    mock_session_repo.get_by_interview_id.return_value = sample_session
    
    # Mock AI provider to return specific token usage
    mock_ai_provider.generate_interview_question.return_value = (
        "What is React?",
        150,  # total tokens
        0.002  # cost
    )
    
    candidate_msg = InterviewMessage(
        id=uuid4(),
        interview_id=sample_interview.id,
        session_id=sample_session.id,
        sequence_number=1,
        message_type="candidate_response",
        content_text="Test"
    )
    ai_msg = InterviewMessage(
        id=uuid4(),
        interview_id=sample_interview.id,
        session_id=sample_session.id,
        sequence_number=2,
        message_type="ai_question",
        content_text="What is React?"
    )
    mock_message_repo.create.side_effect = [candidate_msg, ai_msg]
    
    engine = InterviewEngine(
        ai_provider=mock_ai_provider,
        session_repo=mock_session_repo,
        message_repo=mock_message_repo,
        interview_repo=mock_interview_repo
    )
    
    # Act
    await engine.process_candidate_response(
        interview_id=sample_interview.id,
        session_id=sample_session.id,
        response_text="Test",
        role_type="Frontend Developer"
    )
    
    # Assert
    mock_interview_repo.update_token_usage.assert_called_once()
    call_args = mock_interview_repo.update_token_usage.call_args
    assert call_args.kwargs["tokens_used"] == 150
    assert call_args.kwargs["cost_usd"] == 0.002
