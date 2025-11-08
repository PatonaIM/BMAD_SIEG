"""Pydantic schemas for interviews."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InterviewStartRequest(BaseModel):
    """
    Schema for starting an interview.
    
    Supports two modes:
    1. Standalone interview: Provide role_type
    2. Job-linked interview: Provide application_id (role_type derived from job)
    
    At least one of (role_type, application_id) must be provided.
    """

    role_type: str | None = Field(
        None,
        description="Role type for standalone interview (e.g., 'react', 'python', 'javascript', 'fullstack')"
    )
    resume_id: UUID | None = Field(
        None,
        description="Optional resume ID"
    )
    application_id: UUID | None = Field(
        None,
        description="Optional application ID to link interview to job posting"
    )

    @field_validator('application_id')
    @classmethod
    def validate_at_least_one(cls, v, info):
        """Ensure at least one of role_type or application_id is provided."""
        role_type = info.data.get('role_type')
        if not v and not role_type:
            raise ValueError('Either role_type or application_id must be provided')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "role_type": "react",
                    "resume_id": None,
                    "application_id": None
                },
                {
                    "role_type": None,
                    "resume_id": None,
                    "application_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            ]
        }
    )


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


class SkillAssessment(BaseModel):
    """Individual skill assessment result."""
    
    skill_area: str = Field(..., description="Skill area assessed")
    proficiency_level: str = Field(..., description="Proficiency: novice|intermediate|proficient|expert")
    display_name: str = Field(..., description="Human-readable skill name")


class InterviewHighlight(BaseModel):
    """Positive moment from the interview."""
    
    title: str = Field(..., description="Short headline for the highlight")
    description: str = Field(..., description="Brief description of what went well")
    skill_area: str | None = Field(None, description="Related skill area")


class GrowthArea(BaseModel):
    """Area for improvement identified during interview."""
    
    skill_area: str = Field(..., description="Skill area to develop")
    suggestion: str = Field(..., description="Specific improvement suggestion")
    display_name: str = Field(..., description="Human-readable skill name")


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
    
    # Enhanced feedback fields
    skill_assessments: list[SkillAssessment] = Field(
        default_factory=list,
        description="Detailed breakdown of skills assessed with proficiency levels"
    )
    highlights: list[InterviewHighlight] = Field(
        default_factory=list,
        description="Positive moments and strengths demonstrated during interview"
    )
    growth_areas: list[GrowthArea] = Field(
        default_factory=list,
        description="Areas for improvement with specific suggestions"
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
                    "message": "Interview completed successfully",
                    "skill_assessments": [
                        {
                            "skill_area": "react_hooks",
                            "proficiency_level": "proficient",
                            "display_name": "React Hooks"
                        }
                    ],
                    "highlights": [
                        {
                            "title": "Strong React Fundamentals",
                            "description": "Demonstrated solid understanding of component lifecycle",
                            "skill_area": "react_fundamentals"
                        }
                    ],
                    "growth_areas": [
                        {
                            "skill_area": "performance_optimization",
                            "suggestion": "Consider learning more about React.memo and useMemo",
                            "display_name": "Performance Optimization"
                        }
                    ]
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


class TechCheckRequest(BaseModel):
    """Schema for tech check results submission."""

    audio_test_passed: bool = Field(..., description="Whether audio test passed")
    camera_test_passed: bool = Field(..., description="Whether camera test passed")
    audio_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Audio test metadata (device_name, level, duration)"
    )
    camera_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Camera test metadata (device_name, resolution, format)"
    )
    browser_info: str = Field(..., description="Browser user agent string")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "audio_test_passed": True,
                    "camera_test_passed": True,
                    "audio_metadata": {
                        "device_name": "Built-in Microphone",
                        "level": 0.75,
                        "duration": 3.2
                    },
                    "camera_metadata": {
                        "device_name": "FaceTime HD Camera",
                        "resolution": "1280x720",
                        "format": "video/webm"
                    },
                    "browser_info": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                }
            ]
        }
    )


class TechCheckResponse(BaseModel):
    """Schema for tech check submission response."""

    success: bool = Field(..., description="Whether tech check results were saved")
    message: str = Field(..., description="Response message")


# ================================================================
# Video Recording Schemas
# ================================================================


class VideoChunkUploadRequest(BaseModel):
    """Schema for video chunk upload request."""

    chunk_index: int = Field(..., description="Zero-indexed chunk number")
    is_final: bool = Field(default=False, description="Whether this is the final chunk")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "chunk_index": 0,
                    "is_final": False
                }
            ]
        }
    )


class VideoChunkUploadResponse(BaseModel):
    """Schema for video chunk upload response."""

    success: bool = Field(..., description="Whether chunk upload succeeded")
    chunk_index: int = Field(..., description="Chunk index that was uploaded")
    uploaded_at: datetime = Field(..., description="Timestamp of upload")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "chunk_index": 0,
                    "uploaded_at": "2025-11-01T12:34:56Z"
                }
            ]
        }
    )


class VideoConsentRequest(BaseModel):
    """Schema for video recording consent."""

    video_recording_consent: bool = Field(
        ...,
        description="Whether candidate consents to video recording"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "video_recording_consent": True
                }
            ]
        }
    )


class VideoConsentResponse(BaseModel):
    """Schema for video consent submission response."""

    success: bool = Field(..., description="Whether consent was recorded")
    video_recording_consent: bool = Field(..., description="Consent value recorded")
    video_recording_status: str = Field(..., description="Video recording status")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "video_recording_consent": True,
                    "video_recording_status": "recording"
                }
            ]
        }
    )
