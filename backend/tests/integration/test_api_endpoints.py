"""Integration tests for interview API endpoints."""
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.models.interview import Interview
from app.models.interview_session import InterviewSession


@pytest.mark.asyncio
async def test_send_message_endpoint_success(test_client, test_candidate, test_db):
    """Test POST /interviews/{id}/messages endpoint with valid request."""
    # Arrange - Create interview and session
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),
        role_type="Frontend Developer",
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
        
        # Act
        response = test_client.post(
            f"/api/v1/interviews/{interview.id}/messages",
            json={"message_text": "I have React experience"},
            headers={"Authorization": f"Bearer {test_candidate.auth_token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "ai_response" in data
        assert "question_number" in data
        assert "message_id" in data
        assert data["ai_response"] == "What is React?"


@pytest.mark.asyncio
async def test_send_message_endpoint_unauthorized(test_client, test_db):
    """Test endpoint rejects requests without authentication."""
    # Arrange
    interview_id = uuid4()
    
    # Act
    response = test_client.post(
        f"/api/v1/interviews/{interview_id}/messages",
        json={"message_text": "Test message"}
    )
    
    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_send_message_endpoint_interview_not_found(test_client, test_candidate, test_db):
    """Test endpoint returns 404 for non-existent interview."""
    # Arrange
    fake_interview_id = uuid4()
    
    # Act
    response = test_client.post(
        f"/api/v1/interviews/{fake_interview_id}/messages",
        json={"message_text": "Test message"},
        headers={"Authorization": f"Bearer {test_candidate.auth_token}"}
    )
    
    # Assert
    assert response.status_code == 404
    assert "INTERVIEW_NOT_FOUND" in response.json()["code"]


@pytest.mark.asyncio
async def test_send_message_endpoint_empty_message(test_client, test_candidate, test_db):
    """Test endpoint validates empty message text."""
    # Arrange - Create interview
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),
        role_type="Frontend Developer",
        status="in_progress",
        total_tokens_used=0,
        cost_usd=0.0
    )
    test_db.add(interview)
    await test_db.commit()
    
    # Act
    response = test_client.post(
        f"/api/v1/interviews/{interview.id}/messages",
        json={"message_text": ""},
        headers={"Authorization": f"Bearer {test_candidate.auth_token}"}
    )
    
    # Assert
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_send_message_endpoint_too_long_message(test_client, test_candidate, test_db):
    """Test endpoint validates message length limit."""
    # Arrange - Create interview
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),
        role_type="Frontend Developer",
        status="in_progress",
        total_tokens_used=0,
        cost_usd=0.0
    )
    test_db.add(interview)
    await test_db.commit()
    
    # Act - Send message over 2000 chars
    long_message = "a" * 2001
    response = test_client.post(
        f"/api/v1/interviews/{interview.id}/messages",
        json={"message_text": long_message},
        headers={"Authorization": f"Bearer {test_candidate.auth_token}"}
    )
    
    # Assert
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_send_message_endpoint_completed_interview(test_client, test_candidate, test_db):
    """Test endpoint rejects messages for completed interviews."""
    # Arrange - Create completed interview
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),
        role_type="Frontend Developer",
        status="completed",
        total_tokens_used=500,
        cost_usd=0.05
    )
    test_db.add(interview)
    
    session = InterviewSession(
        id=uuid4(),
        interview_id=interview.id,
        current_difficulty_level="advanced",
        questions_asked_count=15
    )
    test_db.add(session)
    await test_db.commit()
    
    # Act
    response = test_client.post(
        f"/api/v1/interviews/{interview.id}/messages",
        json={"message_text": "Test message"},
        headers={"Authorization": f"Bearer {test_candidate.auth_token}"}
    )
    
    # Assert
    assert response.status_code == 400
    assert "INTERVIEW_COMPLETED" in response.json()["code"]


@pytest.mark.asyncio
async def test_get_interview_status_endpoint(test_client, test_candidate, test_db):
    """Test GET /interviews/{id}/status endpoint."""
    # Arrange
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),
        role_type="Frontend Developer",
        status="in_progress",
        total_tokens_used=250,
        cost_usd=0.025
    )
    test_db.add(interview)
    
    session = InterviewSession(
        id=uuid4(),
        interview_id=interview.id,
        current_difficulty_level="standard",
        questions_asked_count=5
    )
    test_db.add(session)
    await test_db.commit()
    
    # Act
    response = test_client.get(
        f"/api/v1/interviews/{interview.id}/status",
        headers={"Authorization": f"Bearer {test_candidate.auth_token}"}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["questions_asked_count"] == 5


@pytest.mark.asyncio
async def test_get_interview_messages_endpoint(test_client, test_candidate, test_db):
    """Test GET /interviews/{id}/messages endpoint."""
    # Arrange
    interview = Interview(
        id=uuid4(),
        candidate_id=test_candidate.id,
        resume_id=uuid4(),
        role_type="Frontend Developer",
        status="in_progress",
        total_tokens_used=0,
        cost_usd=0.0
    )
    test_db.add(interview)
    
    session = InterviewSession(
        id=uuid4(),
        interview_id=interview.id,
        current_difficulty_level="warmup",
        questions_asked_count=0
    )
    test_db.add(session)
    await test_db.commit()
    
    # Act
    response = test_client.get(
        f"/api/v1/interviews/{interview.id}/messages",
        headers={"Authorization": f"Bearer {test_candidate.auth_token}"}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
