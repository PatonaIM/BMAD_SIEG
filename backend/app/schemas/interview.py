"""Pydantic schemas for interviews."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InterviewStartRequest(BaseModel):
    """Schema for starting an interview."""

    role_type: str = Field(..., pattern="^(react|python|javascript|fullstack)$")
    resume_id: UUID | None = None


class InterviewResponse(BaseModel):
    """Schema for interview data in responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_id: UUID
    resume_id: UUID | None
    role_type: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: int | None
    ai_model_used: str | None
    total_tokens_used: int
    created_at: datetime


class SendMessageRequest(BaseModel):
    """Schema for sending a candidate message."""

    message_text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Candidate's response text (max 2000 characters)"
    )
    audio_metadata: dict[str, Any] | None = Field(
        None,
        description="Optional audio metadata for future speech integration"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "message_text": "I have 3 years of React experience and work with hooks daily",
                    "audio_metadata": None
                }
            ]
        }
    )


class SendMessageResponse(BaseModel):
    """Schema for AI response to candidate message."""

    message_id: UUID = Field(
        ...,
        description="UUID of the created candidate message"
    )
    ai_response: str = Field(
        ...,
        description="AI-generated follow-up question"
    )
    question_number: int = Field(
        ...,
        description="Current question number in sequence"
    )
    total_questions: int = Field(
        ...,
        description="Estimated total questions for interview"
    )
    session_state: dict[str, Any] = Field(
        ...,
        description="Current session progression state for UI"
    )
    interview_complete: bool = Field(
        default=False,
        description="Flag indicating if interview should be completed (criteria met)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "message_id": "550e8400-e29b-41d4-a716-446655440000",
                    "ai_response": "Great! Can you explain the useEffect hook and when to use it?",
                    "question_number": 5,
                    "total_questions": 15,
                    "interview_complete": False,
                    "session_state": {
                        "current_difficulty": "standard",
                        "skill_boundaries": {
                            "react_fundamentals": "proficient",
                            "hooks": "exploring"
                        }
                    }
                }
            ]
        }
    )


class InterviewStatusResponse(BaseModel):
    """Schema for interview status check."""

    id: UUID
    status: str
    question_count: int
    last_activity_at: datetime
    current_difficulty: str


class InterviewMessageResponse(BaseModel):
    """Schema for individual interview message."""

    id: UUID
    sequence_number: int
    message_type: str
    content_text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewMessagesResponse(BaseModel):
    """Schema for conversation history."""

    messages: list[InterviewMessageResponse]
    total_count: int


class InterviewCompleteResponse(BaseModel):
    """Schema for interview completion response."""

    interview_id: UUID = Field(
        ...,
        description="UUID of the completed interview"
    )
    completed_at: datetime = Field(
        ...,
        description="Timestamp when interview was completed"
    )
    duration_seconds: int = Field(
        ...,
        description="Total interview duration in seconds"
    )
    questions_answered: int = Field(
        ...,
        description="Total number of questions answered"
    )
    skill_boundaries_identified: int = Field(
        ...,
        description="Number of skill boundaries identified during interview"
    )
    message: str = Field(
        default="Interview completed successfully",
        description="Completion confirmation message"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "interview_id": "550e8400-e29b-41d4-a716-446655440000",
                    "completed_at": "2025-11-01T14:30:45Z",
                    "duration_seconds": 1845,
                    "questions_answered": 15,
                    "skill_boundaries_identified": 3,
                    "message": "Interview completed successfully"
                }
            ]
        }
    )


class TranscriptMessage(BaseModel):
    """Schema for a single transcript message."""

    sequence_number: int = Field(
        ...,
        description="Message sequence number in conversation"
    )
    message_type: str = Field(
        ...,
        description="Type of message: 'ai_question' or 'candidate_response'"
    )
    content_text: str = Field(
        ...,
        description="Message text content"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when message was created"
    )
    audio_url: str | None = Field(
        None,
        description="Optional audio recording URL"
    )

    model_config = ConfigDict(from_attributes=True)


class InterviewTranscriptResponse(BaseModel):
    """Schema for complete interview transcript."""

    interview_id: UUID = Field(
        ...,
        description="UUID of the interview"
    )
    started_at: datetime = Field(
        ...,
        description="Interview start timestamp"
    )
    completed_at: datetime | None = Field(
        None,
        description="Interview completion timestamp (null if in progress)"
    )
    duration_seconds: int | None = Field(
        None,
        description="Total interview duration in seconds (null if in progress)"
    )
    messages: list[TranscriptMessage] = Field(
        ...,
        description="List of all interview messages in chronological order"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "interview_id": "550e8400-e29b-41d4-a716-446655440000",
                    "started_at": "2025-11-01T14:00:00Z",
                    "completed_at": "2025-11-01T14:30:45Z",
                    "duration_seconds": 1845,
                    "messages": [
                        {
                            "sequence_number": 1,
                            "message_type": "ai_question",
                            "content_text": "Let's start with React fundamentals...",
                            "created_at": "2025-11-01T14:00:15Z",
                            "audio_url": None
                        }
                    ]
                }
            ]
        }
    )
