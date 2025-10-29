"""Integration tests for database operations."""
from decimal import Decimal

import pytest
from sqlalchemy import select, text

from app.models.candidate import Candidate
from app.models.interview import Interview
from app.models.interview_message import InterviewMessage
from app.models.interview_session import InterviewSession


@pytest.mark.asyncio
async def test_database_connection(test_db):
    """Test basic database connectivity."""
    result = await test_db.execute(text("SELECT 1"))
    assert result.scalar() == 1


@pytest.mark.asyncio
async def test_create_candidate_and_query(test_db):
    """Test creating and querying a candidate."""
    candidate = Candidate(
        email="query@example.com",
        full_name="Query Test",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.commit()

    # Query by email
    stmt = select(Candidate).where(Candidate.email == "query@example.com")
    result = await test_db.execute(stmt)
    found = result.scalar_one_or_none()

    assert found is not None
    assert found.email == "query@example.com"
    assert found.full_name == "Query Test"


@pytest.mark.asyncio
async def test_interview_with_session_and_messages(test_db):
    """Test creating interview with session and messages."""
    # Create candidate
    candidate = Candidate(
        email="fulltest@example.com",
        full_name="Full Test",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.flush()

    # Create interview
    interview = Interview(
        candidate_id=candidate.id,
        role_type="fullstack",
        status="in_progress"
    )
    test_db.add(interview)
    await test_db.flush()

    # Create session
    session = InterviewSession(
        interview_id=interview.id,
        current_difficulty_level="standard",
        questions_asked_count=3,
        conversation_memory={"history": []},
        skill_boundaries_identified={"react": "intermediate"}
    )
    test_db.add(session)
    await test_db.flush()

    # Create messages
    message1 = InterviewMessage(
        interview_id=interview.id,
        session_id=session.id,
        sequence_number=1,
        message_type="ai_question",
        content_text="Tell me about your React experience"
    )
    message2 = InterviewMessage(
        interview_id=interview.id,
        session_id=session.id,
        sequence_number=2,
        message_type="candidate_response",
        content_text="I have 3 years of React experience",
        response_time_seconds=45
    )
    test_db.add_all([message1, message2])
    await test_db.commit()

    # Query back
    stmt = select(Interview).where(Interview.id == interview.id)
    result = await test_db.execute(stmt)
    found_interview = result.scalar_one()

    await test_db.refresh(found_interview, ["session", "messages"])
    assert found_interview.session is not None
    assert len(found_interview.messages) == 2
    assert found_interview.messages[0].sequence_number == 1


@pytest.mark.asyncio
async def test_jsonb_field_operations(test_db):
    """Test JSONB field serialization/deserialization."""
    candidate = Candidate(
        email="jsonb@example.com",
        full_name="JSONB Test",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.flush()

    interview = Interview(
        candidate_id=candidate.id,
        role_type="python",
        status="scheduled"
    )
    test_db.add(interview)
    await test_db.flush()

    session = InterviewSession(
        interview_id=interview.id,
        current_difficulty_level="warmup",
        questions_asked_count=0,
        conversation_memory={
            "messages": [
                {"role": "system", "content": "You are an interviewer"}
            ]
        },
        skill_boundaries_identified={
            "python": {"level": "advanced", "topics": ["async", "metaclasses"]},
            "sql": {"level": "intermediate"}
        }
    )
    test_db.add(session)
    await test_db.commit()
    await test_db.refresh(session)

    # Verify JSONB data persisted correctly
    assert session.conversation_memory["messages"][0]["role"] == "system"
    assert session.skill_boundaries_identified["python"]["level"] == "advanced"
    assert "async" in session.skill_boundaries_identified["python"]["topics"]


@pytest.mark.asyncio
async def test_cascading_delete(test_db):
    """Test cascading deletes maintain referential integrity."""
    candidate = Candidate(
        email="cascade@example.com",
        full_name="Cascade Test",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.flush()

    interview = Interview(
        candidate_id=candidate.id,
        role_type="javascript",
        status="scheduled"
    )
    test_db.add(interview)
    await test_db.commit()

    interview_id = interview.id

    # Delete candidate (should cascade to interview)
    await test_db.delete(candidate)
    await test_db.commit()

    # Verify interview was deleted
    stmt = select(Interview).where(Interview.id == interview_id)
    result = await test_db.execute(stmt)
    found = result.scalar_one_or_none()

    assert found is None


@pytest.mark.asyncio
async def test_decimal_precision(test_db):
    """Test decimal field precision for costs."""
    candidate = Candidate(
        email="decimal@example.com",
        full_name="Decimal Test",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.flush()

    interview = Interview(
        candidate_id=candidate.id,
        role_type="fullstack",
        status="completed",
        cost_usd=Decimal("12.3456")
    )
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)

    assert interview.cost_usd == Decimal("12.3456")
    assert str(interview.cost_usd) == "12.3456"
