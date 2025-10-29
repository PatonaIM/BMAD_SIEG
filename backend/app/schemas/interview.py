"""Pydantic schemas for interviews."""
from datetime import datetime
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
